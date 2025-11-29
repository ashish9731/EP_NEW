import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadVideo } from '../api/assessmentApi';
import { Upload, Video, AlertCircle, CheckCircle } from 'lucide-react';

const UploadPage = ({ onUploadComplete }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile) => {
    setError(null);

    // Validate file type
    if (!selectedFile.name.match(/\.(mp4|mov)$/i)) {
      setError('Please upload an MP4 or MOV file');
      return;
    }

    // Validate file size (max 500MB)
    if (selectedFile.size > 500 * 1024 * 1024) {
      setError('File size must be less than 500MB');
      return;
    }

    setFile(selectedFile);
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const response = await uploadVideo(file, (progress) => {
        setUploadProgress(progress);
      });

      onUploadComplete(response.assessment_id);
      navigate(`/processing/${response.assessment_id}`);
    } catch (err) {
      setError(err.message);
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-white mb-4" data-testid="upload-page-title">
          Executive Presence Assessment
        </h1>
        <p className="text-xl text-gray-300 max-w-2xl mx-auto">
          Upload a 3-minute video to receive AI-powered coaching on your communication, body language, and storytelling
        </p>
      </div>

      {/* Upload Zone */}
      <div className="w-full max-w-2xl">
        <div
          className={`upload-zone relative border-4 border-dashed rounded-2xl p-12 text-center bg-slate-800/50 backdrop-blur-sm ${
            dragActive ? 'border-purple-500 bg-purple-900/20' : 'border-gray-600'
          } ${!uploading ? 'cursor-pointer' : 'cursor-not-allowed'}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => !uploading && fileInputRef.current?.click()}
          data-testid="video-upload-zone"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".mp4,.mov,.MP4,.MOV"
            onChange={handleFileInput}
            className="hidden"
            disabled={uploading}
            data-testid="video-file-input"
          />

          {!file ? (
            <div>
              <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-2xl font-semibold text-white mb-2">
                Upload Your Video
              </h3>
              <p className="text-gray-400 mb-4">
                Drag and drop or click to browse
              </p>
              <p className="text-sm text-gray-500">
                MP4 or MOV format • 2-4 minutes • Max 500MB
              </p>
            </div>
          ) : (
            <div>
              <Video className="w-16 h-16 mx-auto mb-4 text-purple-400" />
              <h3 className="text-xl font-semibold text-white mb-2">
                {file.name}
              </h3>
              <p className="text-gray-400 mb-4">
                {(file.size / (1024 * 1024)).toFixed(2)} MB
              </p>
              {!uploading && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setFile(null);
                  }}
                  className="text-sm text-red-400 hover:text-red-300"
                  data-testid="remove-video-button"
                >
                  Remove
                </button>
              )}
            </div>
          )}

          {uploading && (
            <div className="mt-6">
              <div className="w-full bg-gray-700 rounded-full h-3 mb-2">
                <div
                  className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                  data-testid="upload-progress-bar"
                ></div>
              </div>
              <p className="text-gray-300 text-sm">
                Uploading... {uploadProgress}%
              </p>
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-slate-800/30 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h4 className="text-lg font-semibold text-white mb-3">
            📹 Recording Guidelines:
          </h4>
          <ul className="space-y-2 text-gray-300 text-sm">
            <li className="flex items-start">
              <CheckCircle className="w-5 h-5 mr-2 mt-0.5 text-green-400 flex-shrink-0" />
              <span>Introduce yourself and your role (30-40 seconds)</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="w-5 h-5 mr-2 mt-0.5 text-green-400 flex-shrink-0" />
              <span>Explain a key initiative you're leading (60-90 seconds)</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="w-5 h-5 mr-2 mt-0.5 text-green-400 flex-shrink-0" />
              <span>Share a leadership challenge story (60-90 seconds)</span>
            </li>
            <li className="flex items-start">
              <CheckCircle className="w-5 h-5 mr-2 mt-0.5 text-green-400 flex-shrink-0" />
              <span>Ensure face and upper torso are visible throughout</span>
            </li>
          </ul>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 bg-red-900/20 border border-red-500 rounded-lg p-4 flex items-start" data-testid="upload-error-message">
            <AlertCircle className="w-5 h-5 mr-3 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}

        {/* Upload Button */}
        {file && !uploading && (
          <button
            onClick={handleUpload}
            className="w-full mt-6 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-semibold py-4 px-8 rounded-xl shadow-lg transform transition hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={uploading}
            data-testid="start-analysis-button"
          >
            Start Analysis →
          </button>
        )}
      </div>

      {/* Footer */}
      <div className="mt-12 text-center text-gray-400 text-sm">
        <p>Your video will be analyzed for ~2-3 minutes and then automatically deleted</p>
      </div>
    </div>
  );
};

export default UploadPage;
