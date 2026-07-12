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
