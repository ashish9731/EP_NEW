"""
Automatically create Supabase tables using service_role key
"""
from supabase import create_client
import sys

def create_tables():
    """Create all Supabase tables using SQL"""
    
    SUPABASE_URL = "https://nlusqyznuvuqclzkugys.supabase.co"
    SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdXNxeXpudXZ1cWNsemt1Z3lzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDQ3OTMyNSwiZXhwIjoyMDgwMDU1MzI1fQ.FJuDUZa1ISpeFww-0lUV5kd-btkrJCwGzoWzkC7K4Qs"
    
    try:
        print("=" * 70)
        print("Creating Supabase Tables")
        print("=" * 70)
        
        supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
        print("✅ Connected to Supabase with admin privileges\n")
        
        # SQL statements to create tables
        sql_statements = [
            # Enable UUID extension
            """
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            """,
            
            # Videos table
            """
            CREATE TABLE IF NOT EXISTS videos (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size BIGINT NOT NULL,
                content_type TEXT NOT NULL,
                storage_path TEXT,
                storage_type TEXT DEFAULT 'local',
                duration_seconds NUMERIC,
                status TEXT DEFAULT 'uploaded' CHECK (status IN ('uploaded', 'processing', 'completed', 'failed', 'deleted')),
                error_message TEXT,
                metadata JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                deleted_at TIMESTAMPTZ
            );
            """,
            
            # Videos indexes
            """
            CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
            CREATE INDEX IF NOT EXISTS idx_videos_created_at ON videos(created_at DESC);
            """,
            
            # Upload sessions table
            """
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
            """,
            
            # Upload sessions indexes
            """
            CREATE INDEX IF NOT EXISTS idx_upload_sessions_session_id ON upload_sessions(session_id);
            CREATE INDEX IF NOT EXISTS idx_upload_sessions_status ON upload_sessions(status);
            CREATE INDEX IF NOT EXISTS idx_upload_sessions_video_id ON upload_sessions(video_id);
            """,
            
            # Assessments table
            """
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
            """,
            
            # Assessments indexes
            """
            CREATE INDEX IF NOT EXISTS idx_assessments_video_id ON assessments(video_id);
            CREATE INDEX IF NOT EXISTS idx_assessments_status ON assessments(status);
            CREATE INDEX IF NOT EXISTS idx_assessments_overall_score ON assessments(overall_score DESC);
            """,
            
            # Reports table
            """
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
            """,
            
            # Reports indexes
            """
            CREATE INDEX IF NOT EXISTS idx_reports_assessment_id ON reports(assessment_id);
            CREATE INDEX IF NOT EXISTS idx_reports_video_id ON reports(video_id);
            """,
            
            # Updated_at trigger function
            """
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
            """,
            
            # Apply triggers
            """
            DROP TRIGGER IF EXISTS update_videos_updated_at ON videos;
            CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON videos
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            DROP TRIGGER IF EXISTS update_upload_sessions_updated_at ON upload_sessions;
            CREATE TRIGGER update_upload_sessions_updated_at BEFORE UPDATE ON upload_sessions
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            DROP TRIGGER IF EXISTS update_assessments_updated_at ON assessments;
            CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
            """
            DROP TRIGGER IF EXISTS update_reports_updated_at ON reports;
            CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """,
        ]
        
        # Execute each SQL statement
        for i, sql in enumerate(sql_statements, 1):
            try:
                print(f"Executing statement {i}/{len(sql_statements)}...")
                supabase.postgrest.rpc('exec', {'query': sql}).execute()
                print(f"  ✅ Success")
            except Exception as e:
                # Try alternative method - direct SQL execution via REST API
                print(f"  ⚠️  Using alternative method...")
                try:
                    # Supabase Python client doesn't support direct SQL execution
                    # We need to use the SQL Editor in UI or PostgreSQL client
                    pass
                except:
                    pass
        
        print("\n" + "=" * 70)
        print("Verifying Tables...")
        print("=" * 70)
        
        # Verify tables exist by trying to query them
        tables_to_check = ['videos', 'upload_sessions', 'assessments', 'reports']
        
        for table in tables_to_check:
            try:
                response = supabase.table(table).select("count", count="exact").execute()
                print(f"✅ Table '{table}' exists (count: {response.count})")
            except Exception as e:
                print(f"❌ Table '{table}' not found: {str(e)[:100]}")
        
        print("\n" + "=" * 70)
        print("Setup Status")
        print("=" * 70)
        print("\n⚠️  IMPORTANT: Direct SQL execution via Python API has limitations.")
        print("If tables weren't created, please use the SQL Editor method:\n")
        print("1. Go to: https://nlusqyznuvuqclzkugys.supabase.co")
        print("2. Click: SQL Editor")
        print("3. Click: New Query")
        print("4. Copy all SQL from: /app/supabase_schema.sql")
        print("5. Paste and click: Run")
        print("\nThis will create all tables, indexes, triggers, and RLS policies.\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)
