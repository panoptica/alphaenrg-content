-- LFC Agent Database Schema
-- Run: psql -d lfc_agent -f init_db.sql

-- Fixtures
CREATE TABLE IF NOT EXISTS fixtures (
    id SERIAL PRIMARY KEY,
    opponent VARCHAR(100) NOT NULL,
    match_date TIMESTAMP NOT NULL,
    competition VARCHAR(50),
    venue VARCHAR(50),
    is_rival BOOLEAN DEFAULT FALSE,
    is_home BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content Assets
CREATE TABLE IF NOT EXISTS content_assets (
    id SERIAL PRIMARY KEY,
    type VARCHAR(20) NOT NULL, -- 'image', 'video', 'quote', 'stat'
    source_type VARCHAR(30), -- 'youtube', 'twitter', 'wikimedia', 'manual'
    source_url TEXT,
    local_path TEXT,
    attribution TEXT,
    copyright_risk VARCHAR(10) DEFAULT 'medium', -- 'low', 'medium', 'high'
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Quotes
CREATE TABLE IF NOT EXISTS quotes (
    id SERIAL PRIMARY KEY,
    quote_text TEXT NOT NULL,
    author VARCHAR(100),
    context TEXT,
    year INT,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Stats
CREATE TABLE IF NOT EXISTS stats (
    id SERIAL PRIMARY KEY,
    stat_type VARCHAR(50),
    opponent VARCHAR(100),
    stat_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Generated Posts
CREATE TABLE IF NOT EXISTS posts (
    id SERIAL PRIMARY KEY,
    fixture_id INT REFERENCES fixtures(id),
    content_type VARCHAR(30),
    variants JSONB,
    selected_variant INT,
    asset_ids INT[],
    scheduled_time TIMESTAMP,
    posted BOOLEAN DEFAULT FALSE,
    post_url TEXT,
    performance JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Engagement Metrics
CREATE TABLE IF NOT EXISTS engagement_metrics (
    id SERIAL PRIMARY KEY,
    post_id INT REFERENCES posts(id),
    measured_at TIMESTAMP DEFAULT NOW(),
    likes INT,
    comments INT,
    shares INT,
    saves INT,
    reach INT,
    impressions INT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_fixtures_date ON fixtures(match_date);
CREATE INDEX IF NOT EXISTS idx_assets_tags ON content_assets USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_posts_fixture ON posts(fixture_id);
CREATE INDEX IF NOT EXISTS idx_posts_scheduled ON posts(scheduled_time);

-- Seed the City fixture
INSERT INTO fixtures (opponent, match_date, competition, venue, is_rival, is_home)
VALUES ('Manchester City', '2025-02-09 16:30:00', 'Premier League', 'Anfield', TRUE, TRUE)
ON CONFLICT DO NOTHING;
