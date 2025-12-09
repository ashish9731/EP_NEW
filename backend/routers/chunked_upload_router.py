"""
Alternative upload endpoint using multi-request chunked upload
This bypasses ingress body size limits by splitting uploads into smaller chunks
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import os
import uuid
import aiofiles
import asyncio
import logging
from typing import Dict
from pydantic import BaseModel
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# Import from assessment router for processing
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from routers.assessment_router import (
    process_video_async,
    assessment_statuses,
    AssessmentStatus
)
from supabase_client import supabase_service

router = APIRouter(prefix="/chunked-upload", tags=["chunked-upload"])

# Directory paths
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
TEMP_CHUNK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_chunks")
os.makedirs(TEMP_CHUNK_DIR, exist_ok=True)

class InitUploadResponse(BaseModel):
    upload_id: str
    chunk_size: int
    message: str

class ChunkUploadResponse(BaseModel):
    upload_id: str
    chunk_index: int
    received_chunks: int
    total_chunks: int
    message: str

class CompleteUploadResponse(BaseModel):
    assessment_id: str
    filename: str
    message: str

@router.post("/init", response_model=InitUploadResponse)
async def init_upload(
    filename: str = Form(...),
    file_size: int = Form(...),
    total_chunks: int = Form(...)
):
    """Initialize a chunked upload session"""
    
    # Validate file type
    if not filename.endswith(('.mp4', '.mov', '.MP4', '.MOV')):
        raise HTTPException(status_code=400, detail="Only MP4 and MOV files are supported")
    
    # Validate file size
    if file_size > 1024 * 1024 * 1024:  # Increase limit to 1GB
        raise HTTPException(status_code=400, detail="File size must be less than 1GB")
    
    # Generate upload session ID
    upload_id = str(uuid.uuid4())
    chunk_dir = os.path.join(TEMP_CHUNK_DIR, upload_id)
    
    # Store session metadata in Supabase
    session_data = {
        "session_id": upload_id,
        "filename": filename,
        "file_size": file_size,
        "total_chunks": total_chunks,
        "chunk_data": [],  # List to track received chunks
        "chunk_dir": chunk_dir,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow().replace(year=datetime.utcnow().year + 1)).isoformat()  # Expire in 1 year
    }
    
    # Create session in Supabase
    session_record = supabase_service.create_upload_session(session_data)
    if not session_record:
        raise HTTPException(status_code=500, detail="Failed to create upload session")
    
    # Create directory for chunks
    os.makedirs(chunk_dir, exist_ok=True)
    
    logger.info(f"Initialized upload session {upload_id} for {filename} ({file_size} bytes, {total_chunks} chunks)")
    
    return InitUploadResponse(
        upload_id=upload_id,
        chunk_size=10 * 1024 * 1024,  # 10MB chunks for better performance
        message="Upload session initialized"
    )

@router.post("/chunk", response_model=ChunkUploadResponse)
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    chunk: UploadFile = File(...)
):
    """Upload a single chunk"""
    
    logger.info(f"Chunk upload request for session {upload_id}, chunk {chunk_index}")
    
    # Get session from Supabase
    session = supabase_service.get_upload_session(upload_id)
    
    if not session:
        logger.error(f"Upload session {upload_id} not found in database")
        raise HTTPException(status_code=404, detail=f"Upload session not found. Session ID: {upload_id}")
    
    if session.get("status") != "active":
        raise HTTPException(status_code=400, detail="Upload session is not active")
    
    # Validate chunk index
    if chunk_index >= session["total_chunks"] or chunk_index < 0:
        raise HTTPException(status_code=400, detail="Invalid chunk index")
    
    # Save chunk
    chunk_path = os.path.join(session["chunk_dir"], f"chunk_{chunk_index:04d}")
    
    try:
        async with aiofiles.open(chunk_path, 'wb') as out_file:
            content = await chunk.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save chunk: {str(e)}")
    
    # Mark chunk as received in Supabase
    chunk_data = session.get("chunk_data", [])
    if chunk_index not in chunk_data:
        chunk_data.append(chunk_index)
        update_data = {
            "chunk_data": chunk_data,
            "uploaded_chunks": len(chunk_data)
        }
        supabase_service.update_upload_session(upload_id, update_data)
    
    return ChunkUploadResponse(
        upload_id=upload_id,
        chunk_index=chunk_index,
        received_chunks=len(chunk_data),
        total_chunks=session["total_chunks"],
        message=f"Chunk {chunk_index + 1}/{session['total_chunks']} received"
    )

@router.post("/complete", response_model=CompleteUploadResponse)
async def complete_upload(upload_id: str = Form(...)):
    """Complete upload by reassembling chunks"""
    
    # Get session from Supabase
    session = supabase_service.get_upload_session(upload_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    if session.get("status") != "active":
        raise HTTPException(status_code=400, detail="Upload session is not active")
    
    # Verify all chunks received
    chunk_data = session.get("chunk_data", [])
    if len(chunk_data) != session["total_chunks"]:
        missing = set(range(session["total_chunks"])) - set(chunk_data)
        raise HTTPException(
            status_code=400,
            detail=f"Missing chunks: {sorted(missing)}"
        )
    
    # Generate assessment ID
    assessment_id = str(uuid.uuid4())
    
    # Reassemble file
    file_extension = os.path.splitext(session["filename"])[1]
    video_filename = f"{assessment_id}{file_extension}"
    video_path = os.path.join(UPLOAD_DIR, video_filename)
    
    try:
        async with aiofiles.open(video_path, 'wb') as out_file:
            for chunk_index in range(session["total_chunks"]):
                chunk_path = os.path.join(session["chunk_dir"], f"chunk_{chunk_index:04d}")
                async with aiofiles.open(chunk_path, 'rb') as chunk_file:
                    chunk_data = await chunk_file.read()
                    await out_file.write(chunk_data)
        
        # Clean up chunks
        for chunk_index in range(session["total_chunks"]):
            chunk_path = os.path.join(session["chunk_dir"], f"chunk_{chunk_index:04d}")
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
        os.rmdir(session["chunk_dir"])
        
        # Mark session as completed in Supabase
        update_data = {
            "status": "completed",
            "video_id": assessment_id
        }
        supabase_service.update_upload_session(upload_id, update_data)
        
        # Initialize status for processing
        assessment_statuses[assessment_id] = AssessmentStatus(
            assessment_id=assessment_id,
            status="processing",
            progress=0,
            message="Video uploaded, starting analysis..."
        )
        
        # Start processing in background (same as main upload)
        asyncio.create_task(process_video_async(assessment_id, video_path))
        
        return CompleteUploadResponse(
            assessment_id=assessment_id,
            filename=session["filename"],
            message="File uploaded and reassembled successfully. Processing started."
        )
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(video_path):
            os.remove(video_path)
        raise HTTPException(status_code=500, detail=f"Failed to reassemble file: {str(e)}")

@router.delete("/cancel/{upload_id}")
async def cancel_upload(upload_id: str):
    """Cancel an upload and clean up chunks"""
    
    # Get session from Supabase
    session = supabase_service.get_upload_session(upload_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    # Clean up chunks
    try:
        chunk_data = session.get("chunk_data", [])
        for chunk_index in chunk_data:
            chunk_path = os.path.join(session["chunk_dir"], f"chunk_{chunk_index:04d}")
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
        if os.path.exists(session["chunk_dir"]):
            os.rmdir(session["chunk_dir"])
        
        # Mark session as cancelled in Supabase
        update_data = {
            "status": "cancelled"
        }
        supabase_service.update_upload_session(upload_id, update_data)
        
        return {"message": "Upload cancelled and cleaned up"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clean up: {str(e)}")