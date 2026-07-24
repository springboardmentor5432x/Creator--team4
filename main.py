"""
main.py - FastAPI Application Entry Point

Creates the FastAPI app, registers middleware, and mounts routers.
Run with: uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes.auth import router as auth_router
from routes.creator import router as creator_router
from routes.agency import router as agency_router
from routes.marketing import router as marketing_router
from routes.admin import router as admin_router
from routes.profile import router as profile_router
from routes.account import router as account_router
from routes.content_analytics import router as content_router
from routes.social_media import router as social_router

# Growth Analytics Module
from routes.growth import router as growth_router
from routes.trend import router as trend_router
from routes.hashtag import router as hashtag_router
from routes.prediction import prediction_router, forecast_router
from routes.content_growth import router as content_growth_router


# ---------------------------------------------------------------------------

# App Initialization
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A production-ready JWT authentication service built with FastAPI. "
        "Database integration points are marked with TODO comments."
    ),
    docs_url="/docs",        # Swagger UI
    redoc_url="/redoc",      # ReDoc UI
    openapi_url="/openapi.json",
)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

# CORS — adjust origins for your frontend's domain in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

# Mount the authentication router (/api/auth/*)
app.include_router(auth_router)

# Mount role-specific routers
app.include_router(creator_router)    # /api/creator/*
app.include_router(agency_router)     # /api/agency/*
app.include_router(marketing_router)  # /api/marketing/*
app.include_router(admin_router)      # /api/admin/*

# Mount the shared profile router (all roles)
app.include_router(profile_router)    # /api/profile

# Mount the account settings & lifecycle router (all authenticated users)
app.include_router(account_router)    # /api/account/*

# Mount the content analytics router
app.include_router(content_router)    # /api/content/*

# Mount the social media integration router
app.include_router(social_router)     # /api/social/*

# Mount the Growth Analytics Module routers
app.include_router(growth_router)          # /api/growth/*
app.include_router(trend_router)           # /api/trend/*
app.include_router(hashtag_router)         # /api/hashtags/*
app.include_router(prediction_router)      # /api/prediction/*
app.include_router(forecast_router)        # /api/forecast/*
app.include_router(content_growth_router)  # /api/content/{id}/growth


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Simple liveness probe.
    Returns 200 OK when the service is up and running.
    """
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# ---------------------------------------------------------------------------
# Startup / Shutdown Events
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def on_startup():
    """
    Runs once when the server starts.
    """
    print(f"[{settings.APP_NAME}] Starting up...")
    from mongo.mongodb import connect_to_mongo, get_database
    from models.mongo import setup_mongodb_indexes
    await connect_to_mongo()
    await setup_mongodb_indexes(get_database())

@app.on_event("shutdown")
async def on_shutdown():
    """
    Runs once when the server stops.
    """
    print(f"[{settings.APP_NAME}] Shutting down...")
    from mongo.mongodb import close_mongo_connection
    await close_mongo_connection()
