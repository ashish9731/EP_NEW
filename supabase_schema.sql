-- Executive Presence Assessment - Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Videos Table
-- Stores information about uploaded videos
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    content_type TEXT NOT NULL,
    storage_path TEXT,
    storage_type TEXT DEFAULT 'local', -- 'local', 's3', 'supabase'
    duration_seconds NUMERIC,
    status TEXT DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'completed', 'failed', 'deleted')),
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);

-- 2. Upload Sessions Table
-- Tracks upload progress and chunked uploads
CREATE TABLE IF NOT EXISTS upload_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id TEXT UNIQUE NOT NULL,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    content_type TEXT NOT NULL,
    total_chunks INTEGER,
    uploaded_chunks INTEGER DEFAULT 0,
    chunk_data JSONB DEFAULT '[]'::jsonb,
    upload_type TEXT DEFAULT 'direct' CHECK (upload_type IN ('direct', 'chunked', 's3_presigned', 's3_multipart')),
    s3_upload_id TEXT,
    s3_key TEXT,
    status TEXT DEFAULT 'initiated' CHECK (status IN ('initiated', 'uploading', 'completed', 'failed', 'cancelled', 'expired')),
    error_message TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_upload_sessions_session_id ON upload_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_upload_sessions_status ON upload_sessions(status);
CREATE INDEX IF NOT EXISTS idx_upload_sessions_video_id ON upload_sessions(video_id);

-- 3. Assessments Table
-- Stores assessment analysis results
CREATE TABLE IF NOT EXISTS assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_id UUID UNIQUE NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    overall_score NUMERIC(5,2),
    communication_score NUMERIC(5,2),
    appearance_score NUMERIC(5,2),
    storytelling_score NUMERIC(5,2),
    scores_data JSONB DEFAULT '{}'::jsonb,
    audio_features JSONB DEFAULT '{}'::jsonb,
    video_features JSONB DEFAULT '{}'::jsonb,
    nlp_features JSONB DEFAULT '{}'::jsonb,
    transcript TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_assessments_video_id ON assessments(video_id);
CREATE INDEX IF NOT EXISTS idx_assessments_status ON assessments(status);
CREATE INDEX IF NOT EXISTS idx_assessments_overall_score ON assessments(overall_score DESC);

-- 4. Reports Table
-- Stores generated coaching reports
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID UNIQUE NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    llm_report TEXT,
    report_type TEXT DEFAULT 'executive_presence',
    buckets JSONB DEFAULT '[]'::jsonb,
    key_takeaways JSONB DEFAULT '{}'::jsonb,
    recommendations JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_reports_assessment_id ON reports(assessment_id);
CREATE INDEX IF NOT EXISTS idx_reports_video_id ON reports(video_id);

-- 5. Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers to all tables
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_upload_sessions_updated_at BEFORE UPDATE ON upload_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 6. Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE upload_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Allow public read access (you can restrict this based on your needs)
CREATE POLICY "Allow public read access on videos" ON videos
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert on videos" ON videos
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update on videos" ON videos
    FOR UPDATE USING (true);

CREATE POLICY "Allow public read access on upload_sessions" ON upload_sessions
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert on upload_sessions" ON upload_sessions
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update on upload_sessions" ON upload_sessions
    FOR UPDATE USING (true);

CREATE POLICY "Allow public read access on assessments" ON assessments
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert on assessments" ON assessments
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update on assessments" ON assessments
    FOR UPDATE USING (true);

CREATE POLICY "Allow public read access on reports" ON reports
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert on reports" ON reports
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public update on reports" ON reports
    FOR UPDATE USING (true);

-- 7. Create views for easier querying
CREATE OR REPLACE VIEW video_assessment_view AS
SELECT 
    v.id as video_id,
    v.filename,
    v.original_filename,
    v.file_size,
    v.status as video_status,
    v.created_at as uploaded_at,
    a.id as assessment_id,
    a.overall_score,
    a.communication_score,
    a.appearance_score,
    a.storytelling_score,
    a.status as assessment_status,
    r.id as report_id,
    r.llm_report
FROM videos v
LEFT JOIN assessments a ON v.id = a.video_id
LEFT JOIN reports r ON a.id = r.assessment_id;

-- 8. Function to get complete video details
CREATE OR REPLACE FUNCTION get_video_details(video_uuid UUID)
RETURNS TABLE (
    video_id UUID,
    filename TEXT,
    file_size BIGINT,
    video_status TEXT,
    assessment_id UUID,
    overall_score NUMERIC,
    communication_score NUMERIC,
    appearance_score NUMERIC,
    storytelling_score NUMERIC,
    llm_report TEXT,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.id,
        v.filename,
        v.file_size,
        v.status,
        a.id,
        a.overall_score,
        a.communication_score,
        a.appearance_score,
        a.storytelling_score,
        r.llm_report,
        v.created_at
    FROM videos v
    LEFT JOIN assessments a ON v.id = a.video_id
    LEFT JOIN reports r ON a.id = r.assessment_id
    WHERE v.id = video_uuid;
END;
$$ LANGUAGE plpgsql;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Executive Presence Assessment database schema created successfully!';
END $$;
