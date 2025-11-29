/**
 * Alternative upload API using multi-request chunked upload
 * This bypasses ingress body size limits by splitting uploads into smaller chunks
 * 
 * Use this if you get 413 errors and cannot modify ingress configuration
 */
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/chunked-upload`;

const CHUNK_SIZE = 5 * 1024 * 1024; // 5MB chunks (safe for most proxies)

/**
 * Upload video using chunked upload (bypasses ingress limits)
 */
export const uploadVideoChunked = async (file, onProgress) => {
  try {
    // Step 1: Initialize upload session
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    
    const initResponse = await axios.post(`${API}/init`, {
      filename: file.name,
      file_size: file.size,
      total_chunks: totalChunks
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    
    const uploadId = initResponse.data.upload_id;
    
    // Step 2: Upload chunks
    for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
      const start = chunkIndex * CHUNK_SIZE;
      const end = Math.min(start + CHUNK_SIZE, file.size);
      const chunk = file.slice(start, end);
      
      const formData = new FormData();
      formData.append('upload_id', uploadId);
      formData.append('chunk_index', chunkIndex.toString());
      formData.append('chunk', chunk, `chunk_${chunkIndex}`);
      
      try {
        await axios.post(`${API}/chunk`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 60000 // 1 minute per chunk
        });
        
        // Update progress
        const progress = Math.round(((chunkIndex + 1) / totalChunks) * 95); // Save 5% for completion
        if (onProgress) {
          onProgress(progress);
        }
      } catch (error) {
        // Cancel upload on chunk failure
        await axios.delete(`${API}/cancel/${uploadId}`).catch(() => {});
        throw new Error(`Failed to upload chunk ${chunkIndex + 1}: ${error.message}`);
      }
    }
    
    // Step 3: Complete upload
    if (onProgress) {
      onProgress(95);
    }
    
    const completeResponse = await axios.post(`${API}/complete`, {
      upload_id: uploadId
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      timeout: 30000
    });
    
    if (onProgress) {
      onProgress(100);
    }
    
    return completeResponse.data;
    
  } catch (error) {
    if (error.response?.status === 413) {
      throw new Error('Chunk too large - this should not happen. Contact support.');
    }
    throw new Error(
      error.response?.data?.detail || error.message || 'Failed to upload video'
    );
  }
};

/**
 * Cancel an ongoing chunked upload
 */
export const cancelChunkedUpload = async (uploadId) => {
  try {
    await axios.delete(`${API}/cancel/${uploadId}`);
  } catch (error) {
    console.error('Failed to cancel upload:', error);
  }
};
