"""
Simple Supabase table setup using REST API
"""
import requests
import json

SUPABASE_URL = "https://nlusqyznuvuqclzkugys.supabase.co"
SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdXNxeXpudXZ1cWNsemt1Z3lzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDQ3OTMyNSwiZXhwIjoyMDgwMDU1MzI1fQ.FJuDUZa1ISpeFww-0lUV5kd-btkrJCwGzoWzkC7K4Qs"

def execute_sql_file():
    """Execute the SQL schema file"""
    print("=" * 70)
    print("Supabase Table Setup")
    print("=" * 70)
    
    # Read SQL file
    with open('/app/supabase_schema.sql', 'r') as f:
        sql_content = f.read()
    
    print("\n📄 SQL Schema loaded")
    print(f"   Length: {len(sql_content)} characters")
    
    # Try to execute via Supabase REST API
    headers = {
        'apikey': SERVICE_ROLE_KEY,
        'Authorization': f'Bearer {SERVICE_ROLE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # Supabase SQL execution endpoint
    sql_url = f"{SUPABASE_URL}/rest/v1/rpc/exec"
    
    print(f"\n🔗 Attempting to execute SQL via REST API...")
    print(f"   URL: {sql_url}")
    
    try:
        response = requests.post(
            sql_url,
            headers=headers,
            json={'query': sql_content},
            timeout=30
        )
        
        print(f"\n   Response Status: {response.status_code}")
        
        if response.status_code in [200, 201, 204]:
            print("   ✅ SQL executed successfully!")
        else:
            print(f"   ⚠️  Unexpected response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("ALTERNATIVE METHOD (Recommended)")
    print("=" * 70)
    print("""
The Supabase Python/REST API has limitations for executing DDL statements.

✅ BEST METHOD - Use SQL Editor (2 minutes):

1. Open: https://nlusqyznuvuqclzkugys.supabase.co
2. Click: "SQL Editor" in left sidebar
3. Click: "+ New query" button
4. Copy ALL content from file: /app/supabase_schema.sql
5. Paste into SQL Editor
6. Click: "Run" button (or press Ctrl+Enter)

This will create:
  • videos table
  • upload_sessions table
  • assessments table
  • reports table
  • All indexes and triggers
  • Row Level Security policies

After running, tables will appear in "Table Editor" section.
""")
    
    print("=" * 70)
    print("Verification")
    print("=" * 70)
    
    # Try to verify tables exist
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SERVICE_ROLE_KEY)
    
    tables = ['videos', 'upload_sessions', 'assessments', 'reports']
    
    print("\nChecking if tables exist...\n")
    
    for table in tables:
        try:
            response = supabase.table(table).select("*").limit(0).execute()
            print(f"  ✅ {table} - EXISTS")
        except Exception as e:
            error_msg = str(e)
            if 'does not exist' in error_msg or 'relation' in error_msg:
                print(f"  ❌ {table} - NOT FOUND (needs to be created)")
            else:
                print(f"  ⚠️  {table} - {error_msg[:50]}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    execute_sql_file()
