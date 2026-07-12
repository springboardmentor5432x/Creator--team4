from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from roles import UserRole
from schemas import UserInDB
from models import UserModel, RoleModel

_UID_PREFIX: dict[str, str] = {
    "creator":        "crt",
    "agency":         "agc",
    "marketing_team": "mrt",
    "administrator":  "adm",
}

def generate_uid(role: UserRole, overall_user_index: int, role_user_index: int) -> str:
    """
    Generate the composite User ID string.
    Format:  <prefix><u><n>
    """
    prefix = _UID_PREFIX[role.value]
    return f"{prefix}{overall_user_index}{role_user_index}"

async def get_role_id_by_name(db: AsyncSession, role_name: str) -> Optional[int]:
    result = await db.execute(select(RoleModel.id).where(RoleModel.role_name == role_name))
    return result.scalar_one_or_none()

async def get_role_name_by_id(db: AsyncSession, role_id: int) -> Optional[str]:
    result = await db.execute(select(RoleModel.role_name).where(RoleModel.id == role_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserInDB]:
    result = await db.execute(
        select(UserModel, RoleModel.role_name)
        .join(RoleModel, UserModel.role_id == RoleModel.id)
        .where(UserModel.email == email.lower())
    )
    row = result.first()
    if row is None:
        return None
    user_row, role_name = row
    return UserInDB(
        id=user_row.id,
        full_name=user_row.full_name,
        email=user_row.email,
        phone_number=user_row.phone_number,
        hashed_password=user_row.password_hash,
        role_id=user_row.role_id,
        role=UserRole(role_name),
        created_at=user_row.created_at,
    )

async def get_user_by_phone_number(db: AsyncSession, phone_number: str) -> Optional[UserInDB]:
    result = await db.execute(
        select(UserModel, RoleModel.role_name)
        .join(RoleModel, UserModel.role_id == RoleModel.id)
        .where(UserModel.phone_number == phone_number)
    )
    row = result.first()
    if row is None:
        return None
    user_row, role_name = row
    return UserInDB(
        id=user_row.id,
        full_name=user_row.full_name,
        email=user_row.email,
        phone_number=user_row.phone_number,
        hashed_password=user_row.password_hash,
        role_id=user_row.role_id,
        role=UserRole(role_name),
        created_at=user_row.created_at,
    )

async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[UserInDB]:
    result = await db.execute(
        select(UserModel, RoleModel.role_name)
        .join(RoleModel, UserModel.role_id == RoleModel.id)
        .where(UserModel.id == user_id)
    )
    row = result.first()
    if row is None:
        return None
    user_row, role_name = row
    return UserInDB(
        id=user_row.id,
        full_name=user_row.full_name,
        email=user_row.email,
        phone_number=user_row.phone_number,
        hashed_password=user_row.password_hash,
        role_id=user_row.role_id,
        role=UserRole(role_name),
        created_at=user_row.created_at,
    )

async def create_user(
    db: AsyncSession,
    full_name: str,
    email: str,
    phone_number: str,
    hashed_password: str,
    role: UserRole,
) -> UserInDB:
    # 1. Resolve role_id
    role_row = await db.execute(
        select(RoleModel).where(RoleModel.role_name == role.value)
    )
    role_obj = role_row.scalar_one()

    # 2. Count existing users overall to get u (overall_user_index)
    overall_count_result = await db.execute(select(func.count(UserModel.id)))
    overall_user_index = overall_count_result.scalar() + 1

    # 3. Count existing users in this role to get n (role_user_index)
    role_count_result = await db.execute(
        select(func.count(UserModel.id)).where(UserModel.role_id == role_obj.id)
    )
    role_user_index = role_count_result.scalar() + 1

    uid = generate_uid(role, overall_user_index, role_user_index)

    new_user = UserModel(
        id=uid,
        full_name=full_name,
        email=email.lower(),
        phone_number=phone_number,
        password_hash=hashed_password,
        role_id=role_obj.id,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserInDB(
        id=new_user.id,
        full_name=new_user.full_name,
        email=new_user.email,
        phone_number=new_user.phone_number,
        hashed_password=new_user.password_hash,
        role_id=new_user.role_id,
        role=role,
        created_at=new_user.created_at,
    )
