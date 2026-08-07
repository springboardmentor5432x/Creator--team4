CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

--Users
CREATE TABLE users (
    id VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (role_id)
    REFERENCES roles(id)
);

--Creator Profiles
CREATE TABLE creator_profiles (
    id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) UNIQUE NOT NULL,
    username VARCHAR(100),
    bio TEXT,
    youtube_url TEXT,
    instagram_url TEXT,
    facebook_url TEXT,
    linkedin_url TEXT,

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

--Agency Profiles
CREATE TABLE agency_profiles (
    id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) UNIQUE NOT NULL,
    agency_name VARCHAR(150),
    website TEXT,
    contact_number VARCHAR(20),

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

--Account Settings
CREATE TABLE account_settings (
    id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) UNIQUE NOT NULL,
    theme VARCHAR(20) DEFAULT 'Light',
    notifications BOOLEAN DEFAULT TRUE,
    language VARCHAR(30) DEFAULT 'English',

    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);

--Agency Creators
CREATE TABLE agency_creators (
    id VARCHAR(20) PRIMARY KEY,
    agency_id VARCHAR(20) NOT NULL,
    creator_id VARCHAR(20) NOT NULL,
    assigned_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (agency_id)
    REFERENCES agency_profiles(id),

    FOREIGN KEY (creator_id)
    REFERENCES creator_profiles(id)
);

-- Sponsorships Table
CREATE TABLE sponsorships (
    sponsorship_id SERIAL PRIMARY KEY,
    creator_id VARCHAR(20) NOT NULL,
    brand_name VARCHAR(100) NOT NULL,
    campaign_name VARCHAR(150),
    platform VARCHAR(50),
    contract_amount DECIMAL(12,2),
    amount_received DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(20) CHECK (status IN ('Pending','Active','Completed','Cancelled')),
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (creator_id)
    REFERENCES creator_profiles(id)
    ON DELETE CASCADE
);

-- Revenue Transactions Table
CREATE TABLE revenue_transactions (
    transaction_id SERIAL PRIMARY KEY,
    creator_id VARCHAR(20) NOT NULL,
    platform VARCHAR(50),
    revenue_source VARCHAR(50),
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',
    transaction_date DATE,
    month VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (creator_id)
    REFERENCES creator_profiles(id)
    ON DELETE CASCADE
);

-- Subscription Revenue Table
CREATE TABLE subscription_revenue (
    subscription_id SERIAL PRIMARY KEY,
    creator_id VARCHAR(20) NOT NULL,
    platform VARCHAR(50),
    month VARCHAR(20),
    subscribers INTEGER DEFAULT 0,
    revenue DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (creator_id)
    REFERENCES creator_profiles(id)
    ON DELETE CASCADE
);

-- Financial Summary Table
CREATE TABLE financial_summary (
    summary_id SERIAL PRIMARY KEY,
    creator_id VARCHAR(20) NOT NULL,
    month VARCHAR(20),
    total_revenue DECIMAL(12,2),
    ad_revenue DECIMAL(12,2),
    sponsorship_revenue DECIMAL(12,2),
    affiliate_revenue DECIMAL(12,2),
    subscription_revenue DECIMAL(12,2),
    highest_revenue_source VARCHAR(50),
    highest_platform VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (creator_id)
    REFERENCES creator_profiles(id)
    ON DELETE CASCADE
);

-- Brand Collaborations Details Table
CREATE TABLE brand_collaborations (
    collaboration_id SERIAL PRIMARY KEY,
    creator_id VARCHAR(20) NOT NULL,
    sponsorship_id INTEGER,
    deliverables TEXT,
    campaign_status VARCHAR(30),
    completion_percentage INTEGER DEFAULT 0,
    payment_status VARCHAR(20),
    remarks TEXT,

    FOREIGN KEY (creator_id)
    REFERENCES creator_profiles(id)
    ON DELETE CASCADE,

    FOREIGN KEY (sponsorship_id)
    REFERENCES sponsorships(sponsorship_id)
    ON DELETE CASCADE
);

-- Sync History: tracks each analytics synchronization attempt per creator per platform
CREATE TABLE sync_history (
    id              SERIAL PRIMARY KEY,
    creator_id      VARCHAR(20) NOT NULL,
    platform        VARCHAR(50) NOT NULL,
    status          VARCHAR(20) CHECK (status IN ('success', 'failed', 'in_progress')) NOT NULL,
    records_updated INTEGER     DEFAULT 0,
    error_message   TEXT,
    started_at      TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    completed_at    TIMESTAMP,

    FOREIGN KEY (creator_id)
    REFERENCES creator_profiles(id)
    ON DELETE CASCADE
);

CREATE INDEX idx_sync_history_creator ON sync_history(creator_id, platform, started_at DESC);

-- Notifications Table (In-App Notification Center & Alert Tracking)
CREATE TABLE notifications (
    id          SERIAL PRIMARY KEY,
    user_id     VARCHAR(20) NOT NULL,
    creator_id  VARCHAR(20),
    title       VARCHAR(255) NOT NULL,
    message     TEXT NOT NULL,
    type        VARCHAR(50) NOT NULL CHECK (type IN ('performance_milestone', 'revenue_update', 'report_generated', 'system_alert')),
    is_read     BOOLEAN DEFAULT FALSE,
    link_url    TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (creator_id) REFERENCES creator_profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read, created_at DESC);

-- Generated Reports History Table
CREATE TABLE generated_reports (
    id            SERIAL PRIMARY KEY,
    creator_id    VARCHAR(20) NOT NULL,
    report_name   VARCHAR(255) NOT NULL,
    report_type   VARCHAR(50) NOT NULL CHECK (report_type IN ('weekly', 'monthly', 'quarterly', 'annual', 'custom')),
    period_label  VARCHAR(100) NOT NULL,
    start_date    DATE NOT NULL,
    end_date      DATE NOT NULL,
    pdf_path      TEXT,
    excel_path    TEXT,
    status        VARCHAR(20) DEFAULT 'generated' CHECK (status IN ('generated', 'failed', 'processing')),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (creator_id) REFERENCES creator_profiles(id) ON DELETE CASCADE
);

CREATE INDEX idx_reports_creator ON generated_reports(creator_id, created_at DESC);

