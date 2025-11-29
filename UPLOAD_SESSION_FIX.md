# Upload Session Error Fix

## Error
```
{"detail":"Upload session not found"}
```

## Root Cause

The frontend was sending the init request with **JSON content** but declaring `Content-Type: application/x-www-form-urlencoded`. This caused the backend to not parse the parameters correctly, and the session wasn't being created properly.

Additionally, the complete endpoint had the same issue.

## Fix Applied

### Frontend Changes (`/app/frontend/src/api/chunkedUploadApi.js`)

**Before:**
```javascript
const initResponse = await axios.post(`${API}/init`, {
  filename: file.name,
  file_size: file.size,
  total_chunks: totalChunks
}, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
});
```

**After:**
```javascript
const initFormData = new URLSearchParams();
initFormData.append('filename', file.name);
initFormData.append('file_size', file.size.toString());
initFormData.append('total_chunks', totalChunks.toString());

const initResponse = await axios.post(`${API}/init`, initFormData, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
});
```

Same fix applied to the complete endpoint.

### Backend Changes (`/app/backend/routers/chunked_upload_router.py`)

Added comprehensive logging to track session lifecycle:

```python
logger.info(f"Initialized upload session {upload_id} for {filename}")
logger.info(f"Active sessions: {list(upload_sessions.keys())}")
logger.info(f"Chunk upload request for session {upload_id}, chunk {chunk_index}")
```

## Testing

The chunked upload has been tested end-to-end:

```bash
# Test results:
✅ Init: Session created successfully
✅ Chunk 0: Uploaded successfully
✅ Chunk 1: Uploaded successfully  
✅ Complete: File reassembled and processing started
```

## How Chunked Upload Works Now

### Full Flow

1. **Initialize Upload Session**
   ```
   POST /api/chunked-upload/init
   Content-Type: application/x-www-form-urlencoded
   Body: filename=video.mp4&file_size=10485760&total_chunks=2
   
   Response: { "upload_id": "...", "chunk_size": 5242880, "message": "..." }
   ```

2. **Upload Each Chunk**
   ```
   POST /api/chunked-upload/chunk
   Content-Type: multipart/form-data
   Body (FormData):
     - upload_id: "..."
     - chunk_index: 0
     - chunk: [binary data]
   
   Response: { "upload_id": "...", "chunk_index": 0, "received_chunks": 1, ... }
   ```

3. **Complete Upload**
   ```
   POST /api/chunked-upload/complete
   Content-Type: application/x-www-form-urlencoded
   Body: upload_id=...
   
   Response: { "assessment_id": "...", "filename": "...", "message": "..." }
   ```

4. **Backend Processing**
   - Chunks are reassembled into final video file
   - Temporary chunks are deleted
   - Video processing starts automatically
   - Session is cleaned up

## Common Issues & Solutions

### Issue: "Upload session not found"
**Cause:** Session ID not being passed correctly or session expired  
**Solution:** Ensure upload_id is properly extracted from init response and passed to subsequent requests

### Issue: "Invalid chunk index"
**Cause:** Chunk index out of range  
**Solution:** Verify totalChunks calculation matches actual chunks being uploaded

### Issue: "Missing chunks"
**Cause:** Not all chunks were uploaded before calling complete  
**Solution:** Ensure all chunks (0 to totalChunks-1) are uploaded successfully

## Session Management

- Sessions are stored **in-memory** (Dict)
- Sessions persist until:
  - Upload is completed successfully
  - Upload is explicitly cancelled
  - Backend restarts (sessions lost - THIS IS A LIMITATION)

### Production Consideration

For production with multiple backend pods or auto-scaling, consider:
1. **Redis** for session storage (shared across pods)
2. **Sticky sessions** on ingress (route same upload_id to same pod)
3. **Database** for session persistence

## Monitoring

Check backend logs for session activity:
```bash
tail -f /var/log/supervisor/backend.out.log | grep session
```

View active sessions (requires adding debug endpoint):
```python
@router.get("/sessions")
async def get_active_sessions():
    return {"active_sessions": len(upload_sessions), "session_ids": list(upload_sessions.keys())}
```

## Testing Locally

Use the test script:
```bash
bash /tmp/test_chunked_upload.sh
```

Or test via frontend (after fixes):
1. Go to upload page
2. Select a video file
3. Click "Start Analysis"
4. Watch progress bar (chunked upload in action)
5. Check backend logs for session lifecycle

## Status

✅ **FIXED AND TESTED**  
The upload session error has been resolved. Chunked uploads now work correctly.
