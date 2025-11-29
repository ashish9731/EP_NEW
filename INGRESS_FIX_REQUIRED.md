# 🚨 CRITICAL: Kubernetes Ingress Configuration Required for File Uploads

## Error You're Seeing
```
413 Payload Too Large
Failed to load resource: the server responded with a status of 413
```

## Root Cause
The Kubernetes nginx ingress controller has a default **1MB request body size limit**. Video uploads (up to 500MB) are being blocked at the ingress level BEFORE reaching your backend.

## ✅ SOLUTION: Update Ingress Annotations

### Required Ingress Configuration

Add these annotations to your Kubernetes Ingress resource:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: your-ingress-name
  annotations:
    # CRITICAL: Increase max body size for video uploads
    nginx.ingress.kubernetes.io/proxy-body-size: "500m"
    
    # Increase timeouts for large file uploads
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "300"
    
    # Buffer size for chunked uploads
    nginx.ingress.kubernetes.io/client-body-buffer-size: "1m"
    
    # Disable buffering for streaming uploads
    nginx.ingress.kubernetes.io/proxy-buffering: "off"
    nginx.ingress.kubernetes.io/proxy-request-buffering: "off"
```

### How to Apply (Choose based on your deployment method)

#### Option A: Using kubectl
```bash
kubectl annotate ingress <your-ingress-name> \
  nginx.ingress.kubernetes.io/proxy-body-size=500m \
  nginx.ingress.kubernetes.io/proxy-read-timeout=300 \
  nginx.ingress.kubernetes.io/proxy-send-timeout=300 \
  nginx.ingress.kubernetes.io/proxy-connect-timeout=300 \
  nginx.ingress.kubernetes.io/client-body-buffer-size=1m \
  nginx.ingress.kubernetes.io/proxy-buffering=off \
  nginx.ingress.kubernetes.io/proxy-request-buffering=off
```

#### Option B: Update Ingress YAML
Edit your ingress YAML file to include the annotations above, then apply:
```bash
kubectl apply -f ingress.yaml
```

#### Option C: Using Helm (if using Helm charts)
Add to your `values.yaml`:
```yaml
ingress:
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "500m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "300"
    nginx.ingress.kubernetes.io/client-body-buffer-size: "1m"
    nginx.ingress.kubernetes.io/proxy-buffering: "off"
    nginx.ingress.kubernetes.io/proxy-request-buffering: "off"
```

Then upgrade:
```bash
helm upgrade <release-name> <chart> -f values.yaml
```

### Verification

After applying the changes:

1. **Wait 30-60 seconds** for ingress controller to reload
2. **Test upload** with a small video file first
3. Check ingress annotations were applied:
   ```bash
   kubectl describe ingress <your-ingress-name>
   ```

### Troubleshooting

If 413 error persists after applying annotations:

1. **Check annotation format**: Some ingress controllers use different annotation prefixes
   - nginx: `nginx.ingress.kubernetes.io/`
   - traefik: `traefik.ingress.kubernetes.io/`
   - AWS ALB: `alb.ingress.kubernetes.io/`

2. **Check ingress controller logs**:
   ```bash
   kubectl logs -n ingress-nginx <ingress-controller-pod>
   ```

3. **Verify ingress class**: Ensure your ingress is using the correct ingress class:
   ```bash
   kubectl get ingress <name> -o yaml | grep ingressClassName
   ```

4. **Check if using cloud load balancer**: Some cloud providers have their own body size limits:
   - **AWS ALB**: Default 1MB, no way to increase via annotations (need to use S3 pre-signed URLs)
   - **GCP Load Balancer**: 32MB limit (can't be increased)
   - **Azure**: Configurable via annotations

## Alternative: Implement Multi-Request Chunked Upload

If you **cannot modify ingress** (e.g., using cloud ALB with hard limits), you'll need to implement a different upload strategy:

### Resumable Upload Pattern
1. Client splits file into 5MB chunks
2. Uploads each chunk separately (multiple requests)
3. Backend reassembles chunks
4. Uses `tus` protocol or custom implementation

This requires significant code changes. See `/app/ALTERNATIVE_UPLOAD_SOLUTION.md` if needed.

## Current Application Changes Already Made

✅ Backend uses chunked file writing (no memory issues)
✅ Frontend has 5-minute timeout
✅ Better error handling
❌ **Ingress configuration blocking uploads** ← YOU ARE HERE

## Priority
**HIGH - BLOCKING PRODUCTION UPLOADS**

Without fixing the ingress configuration, **NO video uploads will work** in production.
