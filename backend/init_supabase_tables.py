"""
Script to initialize Supabase tables
Run this once to create all necessary tables
"""
from supabase import create_client
import sys

def init_supabase_tables():
    """Initialize all Supabase tables"""
    
    SUPABASE_URL = "https://nlusqyznuvuqclzkugys.supabase.co"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdXNxeXpudXZ1cWNsemt1Z3lzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0NzkzMjUsImV4cCI6MjA4MDA1NTMyNX0.aP9Rs7HV-Lcn8uRfRqx2glF7Q0cc97IiP1TauAUuXLw"
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        print("=" * 60)
        print("Initializing Supabase Tables")
        print("=" * 60)
        
        # Read SQL schema file
        with open('/app/supabase_schema.sql', 'r') as f:
            sql_schema = f.read()
        
        print("\n📋 SQL Schema loaded successfully")
        print("\n⚠️  IMPORTANT: Please execute the SQL schema manually in Supabase SQL Editor")
        print(f"\n1. Go to: {SUPABASE_URL}")
        print("2. Navigate to: SQL Editor (in left sidebar)")
        print("3. Click 'New Query'")
        print("4. Copy and paste the contents of /app/supabase_schema.sql")
        print("5. Click 'Run' to execute\n")
        
        # Test connection by trying to access tables
        print("Testing connection to Supabase...")
        
        try:
            # Try to query videos table (will fail if not created yet)
            response = supabase.table('videos').select("count").execute()
            print("✅ Videos table exists")
        except Exception as e:
            print(f"⚠️  Videos table not found - needs to be created: {str(e)[:100]}")
        
        try:
            response = supabase.table('assessments').select("count").execute()
            print("✅ Assessments table exists")
        except Exception as e:
            print(f"⚠️  Assessments table not found - needs to be created")
        
        try:
            response = supabase.table('upload_sessions').select("count").execute()
            print("✅ Upload sessions table exists")
        except Exception as e:
            print(f"⚠️  Upload sessions table not found - needs to be created")
        
        try:
            response = supabase.table('reports').select("count").execute()
            print("✅ Reports table exists")
        except Exception as e:
            print(f"⚠️  Reports table not found - needs to be created")
        
        print("\n" + "=" * 60)
        print("Setup Instructions Complete")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("1. Supabase URL is correct")
        print("2. Supabase API key is valid")
        print("3. Internet connection is working")
        return False

if __name__ == "__main__":
    success = init_supabase_tables()
    sys.exit(0 if success else 1)
