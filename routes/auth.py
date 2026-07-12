"""
routes/auth.py - Authentication Route Handlers

Registers all endpoints under the /api/auth prefix:
  POST /api/auth/register  - Create a new user account
  POST /api/auth/login     - Authenticate and receive a JWT
  GET  /api/auth/me        - Return the currently authenticated user's profile
"""

from fastapi import APIRouter, HTTPException, status, Depends

from auth import hash_password, verify_password, create_access_token
from dependencies import get_current_active_user, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RegisterSuccessResponse,
    UserPublicResponse,
    UserInDB,
)
from services.user_service import get_user_by_email, create_user, get_user_by_phone_number

# All routes in this file share the /api/auth prefix and the "auth" tag
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=RegisterSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Creates a new user account. "
        "Validates email format and password strength, "
        "checks for duplicate emails, and stores a bcrypt hash of the password."
    ),
)
async def register(payload: UserRegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Registration endpoint.

    Flow:
      1. Check if the email is already registered.
      2. Hash the plaintext password.
      3. Persist the new user via user_service.create_user().
      4. Return a success response with the public user profile.
    """

    # Step 1: Guard against duplicate emails
    # TODO (Database Teammate): get_user_by_email will hit your DB here.
    existing_user = await get_user_by_email(db, payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    existing_user_byphone_number= await get_user_by_phone_number(db, payload.phone_number)
    if existing_user_byphone_number:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this phone number already exists.",
        )

    # Step 2: Hash the password — never store plaintext
    hashed_pw = hash_password(payload.password)
    

    # Step 3: Persist the user
    
    new_user = await create_user(
        db=db,
        full_name=payload.full_name,    # ← maps to users.full_name
        email=payload.email,
        phone_number=payload.phone_number,
        hashed_password=hashed_pw,
        role=payload.role,              # ← resolved to users.role_id via roles table
    )

    print(new_user)
    # Step 4: Build and return the safe public response
    return RegisterSuccessResponse(
        message="User registered successfully.",
        user=UserPublicResponse(
            id=new_user.id,
            full_name=new_user.full_name,
            email=new_user.email,
            phone_number=new_user.phone_number,
            rid=new_user.role_id,           # FK to roles.id
            role=new_user.role,
            created_at=new_user.created_at,
        ),
    )


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and receive a JWT",
    description=(
        "Authenticates a user by email and password. "
        "Returns a signed JWT access token on success."
    ),
)
async def login(payload: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login endpoint.

    Flow:
      1. Look up the user by email.
      2. Verify the provided password against the stored bcrypt hash.
      3. Generate and return a JWT access token.

    Security note:
      Both 'user not found' and 'wrong password' return the same 401 response
      to prevent user enumeration attacks.
    """
    # Shared error used for both "not found" and "wrong password"
    # to prevent user-enumeration via differing error messages.
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Step 1: Fetch the user
    # TODO (Database Teammate): get_user_by_email will query your DB here.
    user = await get_user_by_email(db, payload.email)
    if user is None:
        raise auth_error

    # Step 2: Verify password
    if not verify_password(payload.password, user.hashed_password):
        raise auth_error

    # Step 3: Generate JWT
    # Claims:
    #   "sub"     — email     (standard RFC 7519 subject claim)
    #   "user_id" — int       (users.id PK)
    #   "uid"     — str       (composite uid, e.g. "crt12")
    #   "rid"     — int       (users.role_id FK to roles.id)
    #   "role"    — str       (roles.role_name — avoids a DB hit on every request)
    access_token = create_access_token(
        data={
            "sub":     user.email,
            "user_id": user.id,
            "rid":     user.role_id,        # FK to roles.id
            "role":    user.role.value,
        }
    )

    return TokenResponse(access_token=access_token, token_type="bearer")


# ---------------------------------------------------------------------------
# GET /api/auth/me
# ---------------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserPublicResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user",
    description=(
        "Returns the profile of the currently authenticated user. "
        "Requires a valid Bearer token in the Authorization header."
    ),
)
async def get_me(current_user: UserInDB = Depends(get_current_active_user)):
    """
    Protected route — returns the caller's profile.

    The `get_current_active_user` dependency handles all token validation.
    This handler simply formats and returns the user data.
    """
    return UserPublicResponse(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        rid=current_user.role_id,           # FK to roles.id
        role=current_user.role,
        created_at=current_user.created_at,
    )