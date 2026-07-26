# 🚀 CreatorIQ — Social Media Analytics Backend

A production-ready **FastAPI** backend that enables content creators to integrate all their social media accounts (Instagram, Facebook, YouTube, LinkedIn, X/Twitter) into a single platform to track growth, revenue, content performance, and analytics.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Database Architecture](#database-architecture)
- [Social Media Integration](#social-media-integration)
- [How OAuth Flow Works](#how-oauth-flow-works)

---

## Overview

CreatorIQ is a centralized analytics dashboard backend for content creators. Creators register with email/password, then **connect** their social media accounts via OAuth. The application stores access tokens and fetches analytics data (followers, engagement, content metrics, growth trends) from each platform's API.

### Key Features

- 🔐 **JWT Authentication** — Secure registration, login, and role-based access control
- 📊 **Multi-Platform Analytics** — Instagram, Facebook, YouTube, LinkedIn, X (Twitter)
- 📈 **Growth Tracking** — Daily growth metrics, trends, and performance scores
- 🏢 **Multi-Role Support** — Creator, Agency, Marketing, Admin roles
- 🔗 **OAuth Integration** — One-click social media account connection
- 🧠 **Content Insights** — Hashtag analytics, trend scoring, and predictions

---

## Tech Stack

| Component | Technology |
|---|---|
| **Framework** | FastAPI |
| **Server** | Uvicorn (ASGI) |
| **Auth** | JWT (python-jose) + bcrypt |
| **Relational DB** | PostgreSQL (via SQLAlchemy + asyncpg) |
| **Document DB** | MongoDB (via Motor + PyMongo) |
| **HTTP Client** | httpx (async) |
| **Validation** | Pydantic v2 |
| **Migrations** | Alembic |

---

## Project Structure

```
backend/
├── main.py                    # FastAPI app entry point
├── config.py                  # Environment config (Pydantic Settings)
├── auth.py                    # Password hashing & JWT creation
├── authorization.py           # Permission & role-based access control
├── permissions.py             # Permission definitions
├── roles.py                   # Role definitions
├── security.py                # Security utilities
├── dependencies.py            # FastAPI dependencies (auth, DB sessions)
├── database.py                # PostgreSQL async engine setup
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (DO NOT COMMIT)
├── .env.example               # Template for environment variables
│
├── routes/                    # API route handlers
│   ├── auth.py                #   /api/auth/* — Register, Login, Me
│   ├── creator.py             #   /api/creator/* — Creator endpoints
│   ├── agency.py              #   /api/agency/* — Agency endpoints
│   ├── marketing.py           #   /api/marketing/* — Marketing endpoints
│   ├── admin.py               #   /api/admin/* — Admin endpoints
│   ├── profile.py             #   /api/profile — User profile
│   ├── account.py             #   /api/account/* — Account settings
│   ├── social_media.py        #   /api/social/* — OAuth & analytics
│   ├── content_analytics.py   #   /api/content/* — Content analytics
│   ├── growth.py              #   /api/growth/* — Growth metrics
│   ├── trend.py               #   /api/trend/* — Trend analysis
│   ├── hashtag.py             #   /api/hashtags/* — Hashtag analytics
│   ├── prediction.py          #   /api/prediction/* & /api/forecast/*
│   └── content_growth.py      #   /api/content/{id}/growth
│
├── services/                  # Business logic layer
│   ├── social_media_service.py    # OAuth orchestration (all platforms)
│   ├── account_service.py         # Account management
│   ├── creator_service.py         # Creator operations
│   ├── agency_service.py          # Agency operations
│   ├── profile_service.py         # Profile management
│   ├── content_analytics_service.py
│   ├── growth_service.py          # Growth calculations
│   ├── trend_service.py           # Trend analysis
│   ├── hashtag_service.py         # Hashtag analytics
│   ├── prediction_service.py      # Predictions
│   ├── forecast_service.py        # Forecasting
│   ├── content_growth_service.py  # Content growth tracking
│   ├── user_service.py            # User CRUD
│   └── platforms/                 # Platform-specific API clients
│       ├── instagram.py           #   Instagram Graph API
│       ├── facebook.py            #   Facebook Graph API
│       ├── youtube.py             #   YouTube Data + Analytics API
│       ├── linkedin.py            #   LinkedIn Marketing API
│       └── x_twitter.py           #   X (Twitter) API v2
│
├── repositories/              # Data access layer (MongoDB)
│   ├── social_media_repository.py
│   ├── content_repository.py
│   ├── growth_repository.py
│   ├── content_growth_repository.py
│   ├── hashtag_repository.py
│   ├── trend_repository.py
│   ├── prediction_repository.py
│   └── audience_repository.py
│
├── models/                    # Data models
│   ├── __init__.py            #   SQLAlchemy models (PostgreSQL)
│   └── mongo.py               #   MongoDB collections & indexes
│
├── schemas/                   # Pydantic request/response schemas
│   └── social_media.py        #   Social media schemas + PlatformEnum
│
├── mongo/                     # MongoDB connection management
│   └── mongodb.py
│
├── utils/                     # Shared utilities
│   ├── analytics.py           #   Engagement rate, performance scores
│   └── exceptions.py          #   Custom exceptions
│
└── database/                  # Database schemas
    ├── postgreSQL/
    │   └── create_tables.sql  #   PostgreSQL table definitions
    └── mongoDB/               #   MongoDB schema docs
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL database (or Supabase)
- MongoDB database (or MongoDB Atlas)
- Social media developer accounts (Meta, Google, LinkedIn, X)

### Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd backend

# 2. Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your actual credentials

# 5. Run the server
uvicorn main:app --reload --port 8000
```

### Verify It's Running

```
GET http://localhost:8000/health
GET http://localhost:8000/docs     ← Swagger UI
GET http://localhost:8000/redoc    ← ReDoc
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
# JWT
SECRET_KEY=your_strong_random_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=FastAPI Auth Service
APP_VERSION=1.0.0
DEBUG=false

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# MongoDB
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/
MONGODB_DB_NAME=creatoriq

# YouTube (Google)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/social/callback/youtube

# Meta (Instagram + Facebook)
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_REDIRECT_URI=http://localhost:8000/api/social/callback/instagram
META_FACEBOOK_REDIRECT_URI=http://localhost:8000/api/social/callback/facebook

# LinkedIn
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/social/callback/linkedin

# X (Twitter)
X_CLIENT_ID=your_x_client_id
X_CLIENT_SECRET=your_x_client_secret
X_REDIRECT_URI=http://localhost:8000/api/social/callback/x
```

> ⚠️ **Never commit `.env` to version control.**

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login and receive JWT |
| `GET` | `/api/auth/me` | Get current user profile |

### Social Media Integration

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/social/connect/{platform}` | Get OAuth URL for a platform |
| `GET` | `/api/social/callback/{platform}` | Handle OAuth callback |
| `GET` | `/api/social/accounts` | List all connected accounts |
| `GET` | `/api/social/analytics/{platform}` | Fetch platform analytics |
| `DELETE` | `/api/social/disconnect/{platform}` | Disconnect an account |

**Supported platforms:** `instagram`, `facebook`, `youtube`, `linkedin`, `x`

### Growth & Analytics

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/growth/*` | Growth metrics |
| `GET` | `/api/trend/*` | Trend analysis |
| `GET` | `/api/hashtags/*` | Hashtag analytics |
| `GET` | `/api/prediction/*` | Predictions |
| `GET` | `/api/forecast/*` | Forecasting |
| `GET` | `/api/content/{id}/growth` | Per-content growth |
| `GET` | `/api/content/*` | Content analytics |

### User Management

| Method | Endpoint | Description |
|---|---|---|
| `GET/PUT` | `/api/profile` | User profile |
| `GET/PUT/DELETE` | `/api/account/*` | Account settings & lifecycle |
| `GET` | `/api/creator/*` | Creator-specific endpoints |
| `GET` | `/api/agency/*` | Agency-specific endpoints |
| `GET` | `/api/admin/*` | Admin endpoints |

---

## Database Architecture

### PostgreSQL (Relational Data)

Stores structured, relational data:

| Table | Purpose |
|---|---|
| `roles` | Role definitions (Creator, Agency, Marketing, Admin) |
| `users` | User accounts with hashed passwords |
| `creator_profiles` | Creator-specific profile data |
| `agency_profiles` | Agency-specific profile data |
| `account_settings` | User preferences (theme, language, notifications) |
| `agency_creators` | Agency ↔ Creator relationships |

### MongoDB (Analytics & Social Data)

Stores flexible, document-based social media data:

| Collection | Purpose |
|---|---|
| `social_accounts` | Connected OAuth accounts & tokens |
| `content_posts` | Posts/videos from all platforms |
| `content_metrics` | Per-post engagement metrics (snapshots) |
| `analytics_summary` | Aggregated analytics per creator |
| `performance_trends` | Daily performance trends |
| `content_insights` | Computed content insights |
| `growth_metrics` | Daily growth data per platform |
| `content_growth` | Per-content growth over time |
| `hashtags` | Hashtag performance stats |
| `trend_scores` | Trend rankings (7-day TTL) |
| `predictions` | Reach/audience predictions (30-day TTL) |

---

## Social Media Integration

### Supported Platforms & APIs

| Platform | API Used | OAuth Type | Data Collected |
|---|---|---|---|
| **Instagram** | Meta Graph API v21.0 | OAuth 2.0 | Profile, followers, impressions, reach, media insights |
| **Facebook** | Meta Graph API v21.0 | OAuth 2.0 | Pages, fan count, page impressions, engagement, post insights |
| **YouTube** | YouTube Data API v3 + Analytics API | OAuth 2.0 | Channel info, subscribers, views, watch time, video stats |
| **LinkedIn** | LinkedIn Marketing API | OAuth 2.0 | Profile, organization pages, page statistics |
| **X (Twitter)** | X API v2 | OAuth 2.0 + PKCE | Profile, followers, tweets, engagement metrics |

### Developer Console Links

| Platform | Console |
|---|---|
| Meta (Instagram/Facebook) | https://developers.facebook.com/ |
| Google (YouTube) | https://console.cloud.google.com/ |
| LinkedIn | https://www.linkedin.com/developers/ |
| X (Twitter) | https://developer.x.com/ |

---

## How OAuth Flow Works

```
┌──────────┐     1. GET /api/social/connect/instagram     ┌──────────────┐
│          │ ──────────────────────────────────────────▶  │              │
│  Creator │     ◀── Returns OAuth URL                    │   Backend    │
│ (Browser)│                                              │   (FastAPI)  │
│          │     2. Redirect to Facebook OAuth             │              │
│          │ ──────────────────────────────────────────▶  │              │
│          │                                              └──────────────┘
│          │     3. Creator approves permissions                 │
│          │ ──────────────────────────────────────────▶        │
│          │                                              ┌──────────────┐
│          │     4. Redirect back with ?code=...           │   Meta API   │
│          │ ◀────────────────────────────────────────── │              │
│          │                                              └──────────────┘
│          │     5. GET /api/social/callback/instagram?code=abc
│          │ ──────────────────────────────────────────▶  ┌──────────────┐
│          │                                              │   Backend    │
│          │     6. Backend exchanges code → token          │ • Exchange   │
│          │        Fetches profile & saves to MongoDB     │ • Save token │
│          │     ◀── { status: "connected" }              │ • Fetch data │
└──────────┘                                              └──────────────┘
```

After connecting, the backend can fetch analytics anytime using the stored tokens.

---

## Roles & Permissions

| Role | Description |
|---|---|
| **Creator** | Content creators — can connect social accounts, view own analytics |
| **Agency** | Talent agencies — can manage multiple creators |
| **Marketing** | Marketing teams — can view analytics across creators |
| **Admin** | Full access to all features |

---

## License

This project is private and proprietary.
