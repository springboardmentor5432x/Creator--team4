--Notifications Table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    creator_id VARCHAR(20),

    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,

    type VARCHAR(50) NOT NULL
        CHECK (
            type IN (
                'performance_milestone',
                'revenue_update',
                'report_generated',
                'system_alert'
            )
        ),

    is_read BOOLEAN DEFAULT FALSE,

    link_url TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (creator_id)
        REFERENCES creator_profiles(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user
ON notifications(user_id, is_read, created_at DESC);

--Generated Reports Table
CREATE TABLE generated_reports (
    id SERIAL PRIMARY KEY,

    creator_id VARCHAR(20) NOT NULL,

    report_name VARCHAR(255) NOT NULL,

    report_type VARCHAR(50) NOT NULL
        CHECK (
            report_type IN (
                'weekly',
                'monthly',
                'quarterly',
                'annual',
                'custom'
            )
        ),

    period_label VARCHAR(100) NOT NULL,

    start_date DATE NOT NULL,

    end_date DATE NOT NULL,

    pdf_path TEXT,

    excel_path TEXT,

    status VARCHAR(20)
        DEFAULT 'generated'
        CHECK (
            status IN (
                'generated',
                'failed',
                'processing'
            )
        ),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (creator_id)
        REFERENCES creator_profiles(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_reports_creator
ON generated_reports(creator_id, created_at DESC);


