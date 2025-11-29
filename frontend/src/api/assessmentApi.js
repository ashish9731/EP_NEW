import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/assessment`;

export const uploadVideo = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(`${API}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 300000, // 5 minutes timeout for large file uploads
      maxContentLength: Infinity,
      maxBodyLength: Infinity,
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        if (onProgress) {
          onProgress(percentCompleted);
        }
      },
    });
    return response.data;
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      throw new Error('Upload timeout - file may be too large or connection is slow');
    }
    if (error.response?.status === 413) {
      throw new Error('File is too large - maximum size is 500MB');
    }
    if (error.response?.status === 504) {
      throw new Error('Upload timeout - please try again with a smaller file');
    }
    throw new Error(
      error.response?.data?.detail || error.message || 'Failed to upload video'
    );
  }
};

export const getStatus = async (assessmentId) => {
  try {
    const response = await axios.get(`${API}/status/${assessmentId}`);
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 'Failed to get status'
    );
  }
};

export const getReport = async (assessmentId) => {
  try {
    const response = await axios.get(`${API}/report/${assessmentId}`);
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 'Failed to get report'
    );
  }
};

export const healthCheck = async () => {
  try {
    const response = await axios.get(`${API}/health`);
    return response.data;
  } catch (error) {
    return { status: 'unhealthy' };
  }
};
