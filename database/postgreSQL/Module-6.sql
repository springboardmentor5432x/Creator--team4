--Sync_history
CREATE TABLE sync_history (
    id SERIAL PRIMARY KEY,
    creator_id VARCHAR(20) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(20)
        CHECK (status IN ('success','failed','in_progress')) NOT NULL,
    records_updated INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    FOREIGN KEY (creator_id)
    REFERENCES creator_profiles(id)
    ON DELETE CASCADE
);

CREATE INDEX idx_sync_history_creator
ON sync_history(creator_id, platform, started_at DESC);
