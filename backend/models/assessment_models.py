from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class VideoUploadResponse(BaseModel):
    assessment_id: str
    filename: str
    message: str

class ParameterScore(BaseModel):
    name: str
    score: float
    raw_value: Optional[float] = None
    unit: Optional[str] = None
    description: str

class BucketScore(BaseModel):
    name: str
    score: float
    parameters: List[ParameterScore]

class AssessmentReport(BaseModel):
    assessment_id: str
    overall_score: float
    communication_score: float
    appearance_score: float
    storytelling_score: float
    buckets: List[BucketScore]
    llm_report: str
    transcript_data: Optional[Dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AssessmentStatus(BaseModel):
    assessment_id: str
    status: str  # 'processing', 'completed', 'failed'
    progress: int  # 0-100
    message: str
    error: Optional[str] = None

class ProcessingResult(BaseModel):
    audio_features: Dict
    video_features: Dict
    nlp_features: Dict
    transcript: str
