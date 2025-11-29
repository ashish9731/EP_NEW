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
from typing import Dict
from pydantic import BaseModel

# Import from assessment router for processing
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from routers.assessment_router import (
    process_video_async,
    assessment_statuses,
    AssessmentStatus
)

router = APIRouter(prefix="/chunked-upload", tags=["chunked-upload"])

# Temporary storage for chunk metadata
upload_sessions: Dict[str, dict] = {}

UPLOAD_DIR = "/app/backend/uploads"
TEMP_CHUNK_DIR = "/app/backend/temp_chunks"
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
    if file_size > 500 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 500MB")
    
    # Generate upload session ID
    upload_id = str(uuid.uuid4())
    
    # Store session metadata
    upload_sessions[upload_id] = {
        "filename": filename,
        "file_size": file_size,
        "total_chunks": total_chunks,
        "received_chunks": set(),
        "chunk_dir": os.path.join(TEMP_CHUNK_DIR, upload_id)
    }
    
    # Create directory for chunks
    os.makedirs(upload_sessions[upload_id]["chunk_dir"], exist_ok=True)
    
    return InitUploadResponse(
        upload_id=upload_id,
        chunk_size=5 * 1024 * 1024,  # 5MB chunks recommended
        message="Upload session initialized"
    )

@router.post("/chunk", response_model=ChunkUploadResponse)
async def upload_chunk(
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    chunk: UploadFile = File(...)
):
    """Upload a single chunk"""
    
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    session = upload_sessions[upload_id]
    
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
    
    # Mark chunk as received
    session["received_chunks"].add(chunk_index)
    
    return ChunkUploadResponse(
        upload_id=upload_id,
        chunk_index=chunk_index,
        received_chunks=len(session["received_chunks"]),
        total_chunks=session["total_chunks"],
        message=f"Chunk {chunk_index + 1}/{session['total_chunks']} received"
    )

@router.post("/complete", response_model=CompleteUploadResponse)
async def complete_upload(upload_id: str = Form(...)):
    """Complete upload by reassembling chunks"""
    
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    session = upload_sessions[upload_id]
    
    # Verify all chunks received
    if len(session["received_chunks"]) != session["total_chunks"]:
        missing = set(range(session["total_chunks"])) - session["received_chunks"]
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
        
        # Clean up session
        del upload_sessions[upload_id]
        
        # TODO: Start processing like in main upload endpoint
        # For now, just return success
        
        return CompleteUploadResponse(
            assessment_id=assessment_id,
            filename=session["filename"],
            message="File uploaded and reassembled successfully"
        )
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(video_path):
            os.remove(video_path)
        raise HTTPException(status_code=500, detail=f"Failed to reassemble file: {str(e)}")

@router.delete("/cancel/{upload_id}")
async def cancel_upload(upload_id: str):
    """Cancel an upload and clean up chunks"""
    
    if upload_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Upload session not found")
    
    session = upload_sessions[upload_id]
    
    # Clean up chunks
    try:
        for chunk_index in session["received_chunks"]:
            chunk_path = os.path.join(session["chunk_dir"], f"chunk_{chunk_index:04d}")
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
        if os.path.exists(session["chunk_dir"]):
            os.rmdir(session["chunk_dir"])
        
        del upload_sessions[upload_id]
        
        return {"message": "Upload cancelled and cleaned up"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clean up: {str(e)}")
