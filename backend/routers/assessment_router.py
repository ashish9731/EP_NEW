from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import aiofiles
from datetime import datetime
from typing import Dict
import asyncio

from services.audio_processor import AudioProcessor
from services.video_processor import VideoProcessor
from services.nlp_processor import NLPProcessor
from services.scoring_engine import ScoringEngine
from services.report_generator import ReportGenerator
from models.assessment_models import (
    VideoUploadResponse,
    AssessmentStatus,
    AssessmentReport
)

router = APIRouter(prefix="/assessment", tags=["assessment"])

# Initialize processors
audio_processor = AudioProcessor()
video_processor = VideoProcessor()
nlp_processor = NLPProcessor()
scoring_engine = ScoringEngine()
report_generator = ReportGenerator()

# Storage for assessment status (in production, use database)
assessment_statuses: Dict[str, AssessmentStatus] = {}
assessment_reports: Dict[str, AssessmentReport] = {}

UPLOAD_DIR = "/app/backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Upload video and start processing"""
    
    # Validate file type
    if not file.filename.endswith(('.mp4', '.mov', '.MP4', '.MOV')):
        raise HTTPException(status_code=400, detail="Only MP4 and MOV files are supported")
    
    # Generate assessment ID
    assessment_id = str(uuid.uuid4())
    
    # Save file
    file_extension = os.path.splitext(file.filename)[1]
    video_filename = f"{assessment_id}{file_extension}"
    video_path = os.path.join(UPLOAD_DIR, video_filename)
    
    try:
        async with aiofiles.open(video_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Initialize status
    assessment_statuses[assessment_id] = AssessmentStatus(
        assessment_id=assessment_id,
        status="processing",
        progress=0,
        message="Video uploaded, starting analysis..."
    )
    
    # Start processing in background
    asyncio.create_task(process_video_async(assessment_id, video_path))
    
    return VideoUploadResponse(
        assessment_id=assessment_id,
        filename=file.filename,
        message="Video uploaded successfully. Processing started."
    )

async def process_video_async(assessment_id: str, video_path: str):
    """Background task to process video"""
    try:
        # Update status: Audio processing
        assessment_statuses[assessment_id].progress = 10
        assessment_statuses[assessment_id].message = "Extracting and analyzing audio..."
        
        audio_features = await audio_processor.process_audio(video_path)
        
        # Update status: Video processing
        assessment_statuses[assessment_id].progress = 40
        assessment_statuses[assessment_id].message = "Analyzing video (pose, expressions, gestures)..."
        
        video_features = video_processor.process_video(video_path)
        
        # Update status: NLP processing
        assessment_statuses[assessment_id].progress = 70
        assessment_statuses[assessment_id].message = "Analyzing storytelling and narrative..."
        
        nlp_features = nlp_processor.process_nlp(
            audio_features["transcript"],
            audio_features["duration"]
        )
        
        # Update status: Scoring
        assessment_statuses[assessment_id].progress = 85
        assessment_statuses[assessment_id].message = "Calculating scores..."
        
        scores = scoring_engine.generate_scores(audio_features, video_features, nlp_features)
        
        # Update status: Report generation
        assessment_statuses[assessment_id].progress = 95
        assessment_statuses[assessment_id].message = "Generating coaching report..."
        
        llm_report = await report_generator.generate_report(
            scores, audio_features, video_features, nlp_features
        )
        
        # Create final report
        report = AssessmentReport(
            assessment_id=assessment_id,
            overall_score=scores["overall_score"],
            communication_score=scores["communication_score"],
            appearance_score=scores["appearance_score"],
            storytelling_score=scores["storytelling_score"],
            buckets=scores["buckets"],
            llm_report=llm_report
        )
        
        # Store report
        assessment_reports[assessment_id] = report
        
        # Update status: Complete
        assessment_statuses[assessment_id].status = "completed"
        assessment_statuses[assessment_id].progress = 100
        assessment_statuses[assessment_id].message = "Assessment complete!"
        
        # Delete video file
        if os.path.exists(video_path):
            os.remove(video_path)
        
    except Exception as e:
        assessment_statuses[assessment_id].status = "failed"
        assessment_statuses[assessment_id].message = "Processing failed"
        assessment_statuses[assessment_id].error = str(e)
        
        # Clean up on error
        if os.path.exists(video_path):
            os.remove(video_path)

@router.get("/status/{assessment_id}", response_model=AssessmentStatus)
async def get_status(assessment_id: str):
    """Get processing status"""
    if assessment_id not in assessment_statuses:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return assessment_statuses[assessment_id]

@router.get("/report/{assessment_id}", response_model=AssessmentReport)
async def get_report(assessment_id: str):
    """Get assessment report"""
    if assessment_id not in assessment_reports:
        # Check if still processing
        if assessment_id in assessment_statuses:
            status = assessment_statuses[assessment_id]
            if status.status == "processing":
                raise HTTPException(status_code=202, detail="Assessment still processing")
            elif status.status == "failed":
                raise HTTPException(status_code=500, detail=f"Assessment failed: {status.error}")
        
        raise HTTPException(status_code=404, detail="Report not found")
    
    return assessment_reports[assessment_id]

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Executive Presence Assessment API"}
