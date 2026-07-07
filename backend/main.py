import os
import requests
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv
import jwt

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# FastAPI Application
app = FastAPI(title="CreatorIQ FastAPI API", version="1.0.0")

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================================
# DATABASE CONFIGURATION & INITIALIZATION
# ========================================================
DATABASE_URL = os.getenv('DATABASE_URL')
db_connected = False

if DATABASE_URL:
    try:
        # Quick test connection to PostgreSQL
        engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"}, connect_timeout=3)
        with engine.connect() as conn:
            pass
        db_connected = True
        print("[FASTAPI] Successfully connected to remote Aiven PostgreSQL.")
    except Exception as e:
        print(f"\n[WARNING] Failed to connect to PostgreSQL: {e}")
        print("[WARNING] Falling back to local SQLite database.\n")

if not (DATABASE_URL and db_connected):
    # SQLite local DB fallback
    engine = create_engine("sqlite:///db.sqlite3", connect_args={"check_same_thread": False})
    print("[FASTAPI] Using local SQLite database.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Model
class UserDB(Base):
    __tablename__ = "users_fastapi"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    role = Column(String, default="Creator")
    is_superuser = Column(Boolean, default=False)
    youtube_channel_id = Column(String, nullable=True)
    youtube_channel_title = Column(String, nullable=True)

# Hashing utilities using raw bcrypt
def hash_password(password: str) -> str:
    pw_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw_bytes, salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        pw_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pw_bytes, hashed_bytes)
    except Exception:
        return False

# Seed Administrator Account & Create Tables
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin_email = "admin@creatoriq.com"
        admin_user = db.query(UserDB).filter(UserDB.email == admin_email).first()
        if not admin_user:
            hashed = hash_password("AdminPassword123!")
            admin = UserDB(
                email=admin_email,
                hashed_password=hashed,
                name="Administrator",
                role="Administrator",
                is_superuser=True
            )
            db.add(admin)
            db.commit()
            print("[FASTAPI] Pre-populated database with default administrator.")
    finally:
        db.close()

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ========================================================
# JWT AUTHENTICATION HELPERS
# ========================================================
SECRET_KEY = os.getenv('SECRET_KEY', 'fastapi-secret-key-fallback-2026')
ALGORITHM = "HS256"

def generate_jwt(user: UserDB):
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(request: Request, db: Session = Depends(get_db)) -> UserDB:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided"
        )
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except Exception as e:
        print("[FASTAPI AUTH ERROR]", type(e), str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_current_admin(current_user: UserDB = Depends(get_current_user)) -> UserDB:
    if current_user.role != "Administrator" and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: Administrator role required"
        )
    return current_user

# ========================================================
# PYDANTIC SCHEMAS
# ========================================================
class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleLoginSchema(BaseModel):
    credential: str

class UpdateRoleSchema(BaseModel):
    userId: int
    role: str

class ConnectYoutubeSchema(BaseModel):
    channelId: str
    channelTitle: str

# ========================================================
# ENDPOINTS
# ========================================================

@app.get("/api/health")
@app.get("/api/health/")
def health_check():
    return {"status": "healthy", "service": "CreatorIQ FastAPI API"}

@app.post("/api/register/")
@app.post("/api/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(UserDB).filter(UserDB.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    
    # Hash password & Save
    hashed = hash_password(user_data.password)
    new_user = UserDB(
        email=user_data.email,
        hashed_password=hashed,
        name=user_data.name,
        role="Creator"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    token = generate_jwt(new_user)
    return {
        "message": "Registration successful",
        "token": token,
        "user": {
            "email": new_user.email,
            "name": new_user.name,
            "role": new_user.role,
            "youtube_channel_id": new_user.youtube_channel_id
        }
    }

@app.post("/api/login/")
@app.post("/api/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token = generate_jwt(user)
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "email": user.email,
            "name": user.name or user.email,
            "role": user.role,
            "youtube_channel_id": user.youtube_channel_id
        }
    }

@app.post("/api/google-login/")
@app.post("/api/google-login")
def google_login(google_data: GoogleLoginSchema, db: Session = Depends(get_db)):
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    try:
        idinfo = id_token.verify_oauth2_token(
            google_data.credential,
            google_requests.Request(),
            google_client_id
        )
        email = idinfo.get('email')
        name = idinfo.get('name', '')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract email from Google identity token"
            )
            
        # Get or create user
        user = db.query(UserDB).filter(UserDB.email == email).first()
        if not user:
            # OAuth signup gets a random secure password
            import secrets
            random_pwd = secrets.token_hex(16)
            user = UserDB(
                email=email,
                hashed_password=hash_password(random_pwd),
                name=name,
                role="Creator"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
        token = generate_jwt(user)
        return {
            "message": "Google authentication successful",
            "token": token,
            "user": {
                "email": user.email,
                "name": user.name or user.email,
                "role": user.role,
                "youtube_channel_id": user.youtube_channel_id
            }
        }
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Google token: {str(ve)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.get("/api/users/")
@app.get("/api/users")
def list_users(db: Session = Depends(get_db), admin: UserDB = Depends(get_current_admin)):
    users = db.query(UserDB).order_by(UserDB.id).all()
    user_list = []
    for u in users:
        user_list.append({
            "id": u.id,
            "email": u.email,
            "name": u.name or u.email,
            "role": u.role
        })
    return {"users": user_list}

@app.post("/api/users/update-role/")
@app.post("/api/users/update-role")
def update_user_role(role_data: UpdateRoleSchema, db: Session = Depends(get_db), admin: UserDB = Depends(get_current_admin)):
    target_user = db.query(UserDB).filter(UserDB.id == role_data.userId).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    target_user.role = role_data.role
    if role_data.role == "Administrator":
        target_user.is_superuser = True
    else:
        target_user.is_superuser = False
        
    db.commit()
    return {
        "message": "User role updated successfully",
        "userId": target_user.id,
        "role": target_user.role
    }

@app.post("/api/users/connect-youtube/")
@app.post("/api/users/connect-youtube")
def connect_youtube(data: ConnectYoutubeSchema, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    current_user.youtube_channel_id = data.channelId
    current_user.youtube_channel_title = data.channelTitle
    db.commit()
    return {
        "message": "YouTube channel connected successfully",
        "youtube_channel_id": current_user.youtube_channel_id,
        "youtube_channel_title": current_user.youtube_channel_title
    }

@app.post("/api/users/disconnect-youtube/")
@app.post("/api/users/disconnect-youtube")
def disconnect_youtube(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    current_user.youtube_channel_id = None
    current_user.youtube_channel_title = None
    db.commit()
    return {"message": "YouTube channel disconnected successfully"}


@app.get("/api/youtube/channel/")
@app.get("/api/youtube/channel")
def youtube_channel_analytics(q: Optional[str] = "", channel_id: Optional[str] = ""):
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="YouTube API Key is not configured on the backend."
        )

    q = q.strip()
    channel_id = channel_id.strip()

    if not q and not channel_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Either "q" or "channel_id" parameter is required.'
        )

    try:
        # Step 1: Search for channel if only q is provided
        if q and not channel_id:
            search_url = 'https://www.googleapis.com/youtube/v3/search'
            search_params = {
                'part': 'snippet',
                'type': 'channel',
                'q': q,
                'maxResults': 1,
                'key': api_key
            }
            res = requests.get(search_url, params=search_params, timeout=5)
            if res.status_code != 200:
                raise HTTPException(
                    status_code=res.status_code,
                    detail=f"YouTube search API error: {res.text}"
                )
            
            search_data = res.json()
            items = search_data.get('items', [])
            if not items:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'No channel found matching "{q}"'
                )
            
            channel_id = items[0]['id']['channelId']

        # Step 2: Fetch channel statistics
        channel_url = 'https://www.googleapis.com/youtube/v3/channels'
        channel_params = {
            'part': 'snippet,statistics,brandingSettings',
            'id': channel_id,
            'key': api_key
        }
        res = requests.get(channel_url, params=channel_params, timeout=5)
        if res.status_code != 200:
            raise HTTPException(
                status_code=res.status_code,
                detail=f"YouTube channels API error: {res.text}"
            )

        channel_data = res.json()
        channel_items = channel_data.get('items', [])
        if not channel_items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel details not found."
            )

        channel_item = channel_items[0]
        snippet = channel_item.get('snippet', {})
        stats = channel_item.get('statistics', {})
        branding = channel_item.get('brandingSettings', {})
        
        channel_info = {
            'id': channel_id,
            'title': snippet.get('title', ''),
            'handle': snippet.get('customUrl', ''),
            'description': snippet.get('description', ''),
            'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
            'banner': branding.get('image', {}).get('bannerExternalUrl', ''),
            'subscribers': int(stats.get('subscriberCount', 0)),
            'views': int(stats.get('viewCount', 0)),
            'videos': int(stats.get('videoCount', 0)),
        }

        # Step 3: Fetch 5 recent videos
        videos_search_url = 'https://www.googleapis.com/youtube/v3/search'
        videos_search_params = {
            'part': 'snippet',
            'channelId': channel_id,
            'order': 'date',
            'type': 'video',
            'maxResults': 5,
            'key': api_key
        }
        res = requests.get(videos_search_url, params=videos_search_params, timeout=5)
        recent_videos = []
        
        if res.status_code == 200:
            video_items = res.json().get('items', [])
            video_ids = [item['id']['videoId'] for item in video_items if item.get('id', {}).get('videoId')]
            
            if video_ids:
                # Step 4: Fetch detailed video stats
                videos_url = 'https://www.googleapis.com/youtube/v3/videos'
                videos_params = {
                    'part': 'snippet,statistics',
                    'id': ','.join(video_ids),
                    'key': api_key
                }
                v_res = requests.get(videos_url, params=videos_params, timeout=5)
                if v_res.status_code == 200:
                    v_items = v_res.json().get('items', [])
                    v_stats_map = {item['id']: item for item in v_items}
                    
                    for v_id in video_ids:
                        if v_id in v_stats_map:
                            v_item = v_stats_map[v_id]
                            v_snippet = v_item.get('snippet', {})
                            v_stats = v_item.get('statistics', {})
                            recent_videos.append({
                                'id': v_id,
                                'title': v_snippet.get('title', ''),
                                'publishedAt': v_snippet.get('publishedAt', ''),
                                'thumbnail': v_snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                                'views': int(v_stats.get('viewCount', 0)),
                                'likes': int(v_stats.get('likeCount', 0)),
                                'comments': int(v_stats.get('commentCount', 0))
                            })

        return {
            'channel': channel_info,
            'videos': recent_videos
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ========================================================
# RUN SERVER SETUP
# ========================================================
if __name__ == "__main__":
    import uvicorn
    # Initialize the tables and admin accounts
    init_db()
    print("[FASTAPI] Starting server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
