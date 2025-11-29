"""
Cleanup script for abandoned upload sessions
Run this periodically (e.g., via cron) to clean up old sessions
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import shutil

async def cleanup_old_sessions():
    """Clean up upload sessions older than 2 hours"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'executive_presence_prod')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    upload_sessions = db.upload_sessions
    
    # Find sessions older than 2 hours
    two_hours_ago = datetime.utcnow() - timedelta(hours=2)
    
    old_sessions = await upload_sessions.find({
        "created_at": {"$lt": two_hours_ago},
        "status": "active"  # Only clean up active (not completed/cancelled)
    }).to_list(None)
    
    print(f"Found {len(old_sessions)} old sessions to clean up")
    
    for session in old_sessions:
        try:
            upload_id = session["_id"]
            chunk_dir = session.get("chunk_dir")
            
            # Delete chunk files
            if chunk_dir and os.path.exists(chunk_dir):
                shutil.rmtree(chunk_dir)
                print(f"Deleted chunks for session {upload_id}")
            
            # Mark session as expired
            await upload_sessions.update_one(
                {"_id": upload_id},
                {"$set": {"status": "expired", "expired_at": datetime.utcnow()}}
            )
            print(f"Marked session {upload_id} as expired")
            
        except Exception as e:
            print(f"Error cleaning up session {session['_id']}: {e}")
    
    # Optionally delete very old expired/cancelled/completed sessions (older than 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    deleted = await upload_sessions.delete_many({
        "created_at": {"$lt": seven_days_ago},
        "status": {"$in": ["expired", "cancelled", "completed"]}
    })
    
    print(f"Deleted {deleted.deleted_count} old session records from database")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_old_sessions())
