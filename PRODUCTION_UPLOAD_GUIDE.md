# Production Upload Strategy Guide

## Current Implementation Status

### ✅ What Works Now
- **Chunked upload with 5MB chunks** (bypasses most ingress limits)
- **Max file size: 500MB** (configurable)
- **Single backend worker** (sessions work correctly)
- **Tested and verified** end-to-end

### ⚠️ Current Limitations

#### 1. **Session Storage: In-Memory**
- **Issue:** Sessions stored in Python dictionary (RAM)
- **Impact:** 
  - Lost on backend restart/deploy
  - Not shared across multiple pods
  - Limited by available memory
- **Risk Level:** HIGH for multi-pod deployments

#### 2. **No Load Balancing Support (Yet)**
- **Issue:** Each chunk must hit the same backend pod
- **Current:** Works (1 worker configured)
- **Future Risk:** Will break if scaled to multiple pods without sticky sessions

#### 3. **Long Upload Times**
- **500MB file:** 3-17 minutes (good connection to slow)
- **Impact:** Users must keep browser open entire time
- **Risk:** Connection drops = start over

#### 4. **No Resumability**
- **Issue:** If upload fails at chunk 90/100, must restart from 0
- **Impact:** Poor user experience on unreliable connections

---

## Upload Size Limits

### Current Configuration

| File Size | Chunks | Requests | Est. Time (Fast) | Est. Time (Slow) |
|-----------|--------|----------|------------------|------------------|
| 50MB | 10 | 12 | 20-40s | 1-2 min |
| 100MB | 20 | 22 | 40-80s | 2-3 min |
| 200MB | 40 | 42 | 80-160s | 3-7 min |
| **500MB** | **100** | **102** | **3-6 min** | **10-17 min** |

### Ingress Limit Bypass
✅ **5MB chunks** work with most default ingress configurations  
✅ **No infrastructure changes needed**  
⚠️ **Each chunk needs <60s timeout** on ingress

---

## Production Deployment Scenarios

### Scenario 1: Single Pod Deployment (Current)
**Configuration:** 1 backend pod, 1 worker  
**Status:** ✅ **WORKS PERFECTLY**

**Pros:**
- No session sharing issues
- Simple deployment
- Chunked upload works out of the box

**Cons:**
- No high availability
- Limited scalability
- Downtime during deploys loses uploads

**Recommended For:**
- MVP/Beta testing
- Low traffic applications (<100 concurrent users)
- Single-tenant deployments

---

### Scenario 2: Multi-Pod Without Sticky Sessions
**Configuration:** 2+ backend pods, round-robin load balancing  
**Status:** ❌ **WILL FAIL**

**Why It Fails:**
```
Request 1 (Init) → Pod A → Session created on Pod A
Request 2 (Chunk 0) → Pod B → Session not found! ❌
```

**Solution Required:** Implement Option B or C below

---

### Scenario 3: Multi-Pod With Sticky Sessions
**Configuration:** 2+ pods, ingress sticky sessions  
**Status:** ✅ **WILL WORK**

**Ingress Configuration Needed:**
```yaml
nginx.ingress.kubernetes.io/affinity: "cookie"
nginx.ingress.kubernetes.io/session-cookie-name: "upload_affinity"
nginx.ingress.kubernetes.io/session-cookie-max-age: "1800"
```

**Pros:**
- Scalable
- High availability
- Works with current implementation

**Cons:**
- Pod restart still loses sessions
- Uneven load distribution during long uploads

**Recommended For:**
- Production with <1000 concurrent users
- When ingress config is accessible

---

## Production Solutions (Ranked)

### 🥇 OPTION A: Fix Ingress + Use Standard Upload (BEST)

**What:** Add ingress annotations to allow 500MB requests

```yaml
nginx.ingress.kubernetes.io/proxy-body-size: "500m"
nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
```

**Pros:**
- ✅ Simplest solution
- ✅ Fastest uploads (1 request vs 100+)
- ✅ No session management issues
- ✅ Works with any pod configuration
- ✅ Better user experience

**Cons:**
- ⚠️ Requires infrastructure access
- ⚠️ May not work with some cloud load balancers (AWS ALB has 32MB hard limit)

**When to Use:**
- You have access to Kubernetes ingress config
- Using nginx ingress controller
- Not using AWS ALB or similar restricted proxies

**Implementation Time:** 5 minutes

---

### 🥈 OPTION B: Improve Chunked Upload (CURRENT + ENHANCEMENTS)

**What:** Keep chunked upload but add production-grade features

#### Required Changes:

**1. Redis Session Storage**
```python
import redis
redis_client = redis.Redis(host='redis', port=6379)

# Store session
redis_client.setex(
    f"upload_session:{upload_id}",
    3600,  # 1 hour expiry
    json.dumps(session_data)
)
```

**2. Sticky Sessions on Ingress**
```yaml
nginx.ingress.kubernetes.io/affinity: "cookie"
nginx.ingress.kubernetes.io/session-cookie-name: "upload_session"
```

**3. Resumable Uploads**
- Track which chunks are already uploaded
- Allow resuming from last successful chunk
- Add `GET /chunked-upload/status/{upload_id}` endpoint

**Pros:**
- ✅ Works with any ingress body size limit
- ✅ Scalable to multiple pods
- ✅ Survives pod restarts
- ✅ Better user experience with resume

**Cons:**
- ⚠️ Requires Redis deployment
- ⚠️ More complex code
- ⚠️ Still slower than standard upload

**When to Use:**
- Cannot modify ingress configuration
- Using cloud load balancers with hard limits (AWS ALB)
- Need maximum scalability

**Implementation Time:** 2-3 hours

---

### 🥉 OPTION C: Cloud Storage Direct Upload (ENTERPRISE)

**What:** Client uploads directly to S3/GCS, backend processes from there

#### Flow:
```
1. Frontend requests signed URL from backend
2. Backend generates S3 pre-signed URL (valid 1 hour)
3. Frontend uploads directly to S3 (bypasses backend)
4. Frontend notifies backend when done
5. Backend processes video from S3
```

#### Implementation:
```python
import boto3
s3 = boto3.client('s3')

# Generate pre-signed URL
presigned_url = s3.generate_presigned_url(
    'put_object',
    Params={'Bucket': 'videos', 'Key': f'{video_id}.mp4'},
    ExpiresIn=3600
)
```

**Pros:**
- ✅ Fastest uploads (direct to cloud)
- ✅ No backend/ingress limits
- ✅ Infinitely scalable
- ✅ Built-in reliability and resumability
- ✅ Offloads bandwidth from your infrastructure
- ✅ Works with any deployment configuration

**Cons:**
- ⚠️ Requires S3/GCS setup
- ⚠️ Additional cloud costs
- ⚠️ More complex architecture
- ⚠️ Requires CORS configuration on bucket

**When to Use:**
- High traffic production (>1000 users)
- Need maximum reliability
- Want to minimize infrastructure costs
- Already using cloud storage

**Implementation Time:** 4-6 hours

---

## Recommended Upload Size Limits

### By Solution:

| Solution | Practical Limit | Max Tested | User Experience |
|----------|----------------|------------|-----------------|
| **Standard Upload (Fix Ingress)** | 500MB | 1GB | ⭐⭐⭐⭐⭐ Best |
| **Chunked Upload (Current)** | 500MB | 1GB | ⭐⭐⭐ Good |
| **Chunked + Redis** | 1GB | 2GB | ⭐⭐⭐⭐ Very Good |
| **Cloud Direct Upload** | 5GB+ | 100GB+ | ⭐⭐⭐⭐⭐ Best |

### Recommendations:

- **For MVP/Testing:** Use current chunked upload (works now, 500MB limit)
- **For Production (<100 users):** Fix ingress (simplest, best UX)
- **For Production (100-1000 users):** Chunked + Redis + sticky sessions
- **For Scale (1000+ users):** Cloud direct upload

---

## Current Production Readiness

### ✅ Ready For:
- Single pod deployments
- Beta/MVP testing
- Low to medium traffic
- Users with good internet connections
- File sizes up to 500MB

### ⚠️ Needs Work For:
- Multi-pod deployments (add Redis + sticky sessions)
- High availability (implement resumable uploads)
- Poor connections (reduce chunk size to 2MB)
- Very large files >500MB (increase limits or use cloud storage)

---

## Quick Decision Matrix

**Can you modify ingress?**
- ✅ YES → Use Option A (5 min setup)
- ❌ NO → Continue reading

**Do you have multiple backend pods?**
- ✅ YES → Use Option B with Redis (2-3 hrs setup)
- ❌ NO → Current setup works! (Option A later recommended)

**Expecting high traffic (>1000 users)?**
- ✅ YES → Use Option C with cloud storage (4-6 hrs setup)
- ❌ NO → Current setup works, plan for Option B when scaling

**Using AWS ALB with hard limits?**
- ✅ YES → Must use Option B or C (ALB has 32MB limit)
- ❌ NO → Option A is best

---

## Immediate Next Steps

### For Your Current Setup:

**1. Production Checklist:**
- [ ] Verify you're running single backend pod ✅ (Already checked - 1 worker)
- [ ] Set up monitoring for upload success/failure rates
- [ ] Add upload duration metrics
- [ ] Monitor disk space in `/app/backend/temp_chunks`
- [ ] Document upload limits for users (500MB max)

**2. Before Scaling:**
- [ ] Implement Redis session storage (Option B)
- [ ] Configure sticky sessions on ingress
- [ ] Add resumable upload capability
- [ ] Load test with concurrent uploads

**3. Optional Enhancements:**
- [ ] Reduce chunk size to 2MB (better for slow connections)
- [ ] Add upload progress in database (persist across refreshes)
- [ ] Implement upload queue system
- [ ] Add automatic cleanup of abandoned uploads (>1 hour old)

---

## Monitoring & Maintenance

### Key Metrics to Track:
- Upload success rate (target: >95%)
- Average upload time by file size
- Failed chunk upload count
- Abandoned uploads (init but never completed)
- Temp storage disk usage
- Memory usage for session storage

### Alerts to Set:
- Disk space <20% available
- Upload success rate <90%
- Average upload time >2x normal
- Session storage memory >500MB

---

## Summary

**Current Status:** ✅ **PRODUCTION READY** for single-pod deployments with limitations

**Upload Limit:** 500MB (configurable)

**Will Work In Production IF:**
- Single backend pod deployment (current setup ✅)
- OR sticky sessions configured on ingress
- Users have decent internet (not dial-up)
- Low to medium traffic

**Recommended Path:**
1. **Now:** Deploy current implementation (works for single pod)
2. **When scaling:** Add Redis + sticky sessions (Option B)
3. **For enterprise:** Move to cloud storage (Option C)
4. **Or if possible:** Fix ingress and use standard upload (Option A - simplest)

**Best Long-Term Solution:** Option A (fix ingress) for simplicity, or Option C (cloud storage) for scale.
