# Alternative Upload Solution: Multi-Request Chunked Upload

## When to Use This

Use this alternative upload method if:
- ❌ You **cannot modify** Kubernetes ingress configuration
- ❌ Getting persistent 413 errors
- ❌ Using cloud load balancers with hard body size limits (AWS ALB, GCP LB)

## How It Works

Instead of one large request:
```
Client ----[500MB]----> Ingress ❌ 413 Error
```

We use multiple small requests:
```
Client ----[5MB chunk 1]----> ✅ Ingress --> Backend
Client ----[5MB chunk 2]----> ✅ Ingress --> Backend
Client ----[5MB chunk 3]----> ✅ Ingress --> Backend
... (reassemble on backend)
```

## Implementation Steps

### 1. Register New Router in Backend

Edit `/app/backend/server.py`:

```python
# Add import at top
from routers.chunked_upload_router import router as chunked_upload_router

# Add after existing router includes (around line 75)
api_router.include_router(chunked_upload_router)
```

### 2. Update Frontend Upload Component

Edit `/app/frontend/src/pages/UploadPage.js`:

```javascript
// Change import at top
import { uploadVideo } from '../api/assessmentApi';
// TO:
import { uploadVideoChunked } from '../api/chunkedUploadApi';

// Change in handleUpload function (line 66)
const response = await uploadVideo(file, (progress) => {
// TO:
const response = await uploadVideoChunked(file, (progress) => {
```

### 3. Restart Services

```bash
sudo supervisorctl restart backend frontend
```

## How the Chunked Upload Works

### Backend Flow

1. **Init**: Client requests upload session with file metadata
   ```
   POST /api/chunked-upload/init
   → Returns upload_id
   ```

2. **Upload Chunks**: Client uploads file in 5MB pieces
   ```
   POST /api/chunked-upload/chunk (100 times for 500MB)
   → Each chunk stored separately
   ```

3. **Complete**: Client signals all chunks uploaded
   ```
   POST /api/chunked-upload/complete
   → Backend reassembles chunks into final file
   → Returns assessment_id
   ```

4. **Processing**: Normal video processing begins

### Advantages
- ✅ Works with any ingress body size limit
- ✅ Resumable (can retry failed chunks)
- ✅ Progress tracking per chunk
- ✅ Better error recovery

### Disadvantages
- ⚠️ More complex code
- ⚠️ More HTTP requests (overhead)
- ⚠️ Slightly slower for small files
- ⚠️ Requires temporary storage for chunks

## Testing

Test with a large file:

```javascript
// In browser console on upload page
const testFile = new File([new ArrayBuffer(50 * 1024 * 1024)], 'test.mp4');
// Try uploading - should work without 413 errors
```

## Cleanup

The chunked upload automatically:
- Deletes chunks after successful reassembly
- Cleans up on cancellation
- Cleans up on error

## Monitoring

Check chunk storage:
```bash
ls -lh /app/backend/temp_chunks/
```

If chunks accumulate (from failed uploads), clean manually:
```bash
find /app/backend/temp_chunks -type d -mtime +1 -exec rm -rf {} \;
```

## Fallback Strategy

You can implement a smart fallback:

1. Try normal upload first
2. If 413 error, automatically retry with chunked upload

```javascript
export const smartUpload = async (file, onProgress) => {
  try {
    return await uploadVideo(file, onProgress);
  } catch (error) {
    if (error.message.includes('413') || error.message.includes('too large')) {
      console.log('Falling back to chunked upload...');
      return await uploadVideoChunked(file, onProgress);
    }
    throw error;
  }
};
```

## Production Considerations

### Storage
- Each concurrent upload uses temporary disk space
- 10 concurrent 500MB uploads = 5GB temp storage
- Monitor disk usage on backend pods

### Concurrency
- Limit concurrent chunked uploads to prevent storage exhaustion
- Implement queue system for high traffic

### Timeout
- Each chunk has 1-minute timeout
- 100 chunks = max 100 minutes total upload time
- Adjust based on your needs

## Files Created

- `/app/backend/routers/chunked_upload_router.py` - Backend chunked upload API
- `/app/frontend/src/api/chunkedUploadApi.js` - Frontend chunked upload client
- This documentation

## Still Recommended: Fix Ingress

While this solution works, **fixing the ingress configuration is still the better long-term solution**:
- Simpler code
- Better performance
- Less complexity

See `/app/INGRESS_FIX_REQUIRED.md` for instructions.
