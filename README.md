# CreatorIQ - Creator Analytics & Content Performance Dashboard

CreatorIQ is a high-fidelity, premium creator analytics dashboard designed to consolidate multi-platform metrics, audience engagement, content growth, and monetization insights into a single unified workspace.

---

## 🏗️ System Architecture

The application is structured into decoupled frontend and backend services:
1. **Frontend**: React SPA powered by Vite (running on port `5173`).
2. **Backend**: Django REST API backend (running on port `8000`).
3. **Database**: Primary connection to Aiven PostgreSQL (with automatic fallback to local SQLite for sandbox development).

```
creator_iq/
├── frontend/               # React SPA (Vite)
│   ├── src/
│   │   ├── api.js          # Unified API caller (w/ auto JWT Authorization headers)
│   │   ├── App.jsx         # Main router and controller
│   │   └── components/     # High-Fidelity UI Components (Auth, Inputs, Success views)
│   └── vite.config.js      # Proxy endpoints to Django API
└── backend/                # Django REST Backend
    ├── backend/
    │   └── settings.py     # CORS & CSRF configurations + startup DB testing
    └── accounts/
        ├── models.py       # Custom UserProfile matching roles
        ├── jwt_utils.py    # Local JWT generation & validation signing
        └── views.py        # Token validation & Admin API registry views
```

---

## ✨ Implemented Features

### 1. High-Fidelity Dashboard Interface
- **Premium Split-Screen Layout**: Elegant dark-themed visual layout with a sleek mesh gradient sidebar, mockup charts, and interactive platform statistics.
- **Social Media SVGs**: High-quality branding badges representing YouTube, Instagram, TikTok, Facebook, X (Twitter), and LinkedIn integrations.
- **Indian Rupees (₹) System**: Unified analytics parameters displaying monetary metrics in local currency (`₹`).
- **Interactive Dark/Light Theme**: Theme toggling button with persistent state stored in the browser's local storage.
- **Floating Inputs**: CSS-transitions and state indicators to prevent placeholder overlapping.

### 2. Authentication & Authorization
- **Google OAuth 2.0 Identity Services**: Real integration with Google Sign-in overlay popup.
- **Local JWT Authentication**: Standard credentials and Google OAuth both issue local JSON Web Tokens (JWT) signed using the Django secret key.
- **User Role Manager**: Admin console workspace for users with the `Administrator` role. Admins can view all registered users and modify their workspace roles (**Creator**, **Agency**, **Marketing Team**, **Administrator**) directly from the UI.

### 3. Graceful Database Connectivity
- Django tests database availability at startup. If the credentials for the remote **Aiven PostgreSQL** instance fail (or aren't configured), the server prints a warning and automatically falls back to local SQLite to ensure zero-downtime local testing.

---

## ⚡ Quick Start (Single Command / One-Click Launcher)

Run both Backend and Frontend together with a single command from the project root:

```cmd
npm start
```
or
```cmd
python run_project.py
```
or double-click **`start.bat`** on Windows.

- **Frontend Application**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

---

## 🚀 Setup & Installation (Manual Method)

### Prerequisite Checklist
- **Node.js**: v18.0.0+
- **Python**: v3.10+
- **Git**: Installed and configured

### 1. Backend Configuration (Django)
1. Navigate to the `backend` folder:
   ```cmd
   cd backend
   ```
2. Install Python dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
3. Configure the environment variables in a `.env` file inside `backend/`:
   ```env
   DATABASE_URL=postgres://avnadmin:YOUR_PASSWORD@pg-2ec22b92-biswajitsahoo773535-d02c.d.aivencloud.com:23661/defaultdb?sslmode=require
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   FRONTEND_URL=http://localhost:5173
   GOOGLE_CLIENT_ID=your_google_oauth_client_id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
   ```
4. Run migrations:
   ```cmd
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Start the backend server:
   ```cmd
   python manage.py runserver 8000
   ```

### 2. Frontend Configuration (Vite)
1. Navigate to the `frontend` folder:
   ```cmd
   cd ../frontend
   ```
2. Install Node packages:
   ```cmd
   npm install
   ```
3. Configure the frontend `.env` file inside `frontend/`:
   ```env
   VITE_GOOGLE_CLIENT_ID=your_google_oauth_client_id.apps.googleusercontent.com
   ```
4. Run the frontend development server:
   ```cmd
   npm run dev
   ```

Open **`http://localhost:5173`** in your browser to view the application.

### Default Admin Credentials for Demo
- **Email**: `admin@creatoriq.com`
- **Password**: `AdminPassword123!`
