"""
Supabase client configuration and database operations
"""
from supabase import create_client, Client
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        self.url = "https://nlusqyznuvuqclzkugys.supabase.co"
        self.key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5sdXNxeXpudXZ1cWNsemt1Z3lzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0NzkzMjUsImV4cCI6MjA4MDA1NTMyNX0.aP9Rs7HV-Lcn8uRfRqx2glF7Q0cc97IiP1TauAUuXLw"
        self.client: Client = create_client(self.url, self.key)
        logger.info("Supabase client initialized")

    # Videos table operations
    def create_video_record(self, video_data: Dict) -> Dict:
        """Create a new video record in Supabase"""
        try:
            response = self.client.table('videos').insert(video_data).execute()
            logger.info(f"Created video record: {response.data}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating video record: {e}")
            return None

    def get_video_by_id(self, video_id: str) -> Optional[Dict]:
        """Retrieve video record by ID"""
        try:
            response = self.client.table('videos').select('*').eq('id', video_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error retrieving video: {e}")
            return None

    def update_video_status(self, video_id: str, status: str, metadata: Dict = None) -> Dict:
        """Update video processing status"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            if metadata:
                update_data.update(metadata)
            
            response = self.client.table('videos').update(update_data).eq('id', video_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating video status: {e}")
            return None

    def list_videos(self, limit: int = 50) -> List[Dict]:
        """List all videos"""
        try:
            response = self.client.table('videos').select('*').order('created_at', desc=True).limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error listing videos: {e}")
            return []

    # Assessment results operations
    def create_assessment(self, assessment_data: Dict) -> Dict:
        """Create a new assessment record"""
        try:
            response = self.client.table('assessments').insert(assessment_data).execute()
            logger.info(f"Created assessment record: {response.data}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating assessment: {e}")
            return None

    def get_assessment_by_video_id(self, video_id: str) -> Optional[Dict]:
        """Retrieve assessment by video ID"""
        try:
            response = self.client.table('assessments').select('*').eq('video_id', video_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error retrieving assessment: {e}")
            return None

    def update_assessment_scores(self, assessment_id: str, scores: Dict) -> Dict:
        """Update assessment scores"""
        try:
            update_data = {
                'overall_score': scores.get('overall_score'),
                'communication_score': scores.get('communication_score'),
                'appearance_score': scores.get('appearance_score'),
                'storytelling_score': scores.get('storytelling_score'),
                'scores_data': scores,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            response = self.client.table('assessments').update(update_data).eq('id', assessment_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating assessment scores: {e}")
            return None

    # Upload sessions operations
    def create_upload_session(self, session_data: Dict) -> Dict:
        """Create a new upload session"""
        try:
            response = self.client.table('upload_sessions').insert(session_data).execute()
            logger.info(f"Created upload session: {response.data}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating upload session: {e}")
            return None

    def update_upload_session(self, session_id: str, update_data: Dict) -> Dict:
        """Update upload session"""
        try:
            update_data['updated_at'] = datetime.utcnow().isoformat()
            response = self.client.table('upload_sessions').update(update_data).eq('session_id', session_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating upload session: {e}")
            return None

    def get_upload_session(self, session_id: str) -> Optional[Dict]:
        """Get upload session by ID"""
        try:
            response = self.client.table('upload_sessions').select('*').eq('session_id', session_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error retrieving upload session: {e}")
            return None

    # Reports operations
    def create_report(self, report_data: Dict) -> Dict:
        """Create a new report record"""
        try:
            response = self.client.table('reports').insert(report_data).execute()
            logger.info(f"Created report record: {response.data}")
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            return None

    def get_report_by_assessment_id(self, assessment_id: str) -> Optional[Dict]:
        """Get report by assessment ID"""
        try:
            response = self.client.table('reports').select('*').eq('assessment_id', assessment_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error retrieving report: {e}")
            return None

# Singleton instance
supabase_service = SupabaseService()
