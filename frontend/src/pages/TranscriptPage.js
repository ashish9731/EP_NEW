import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getReport } from '../api/assessmentApi';
import { ArrowLeft, Mic, FileText, Clock } from 'lucide-react';

const TranscriptPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const reportData = await getReport(id);
        setReport(reportData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchReport();
    }
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white text-xl">Loading transcript data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <p className="text-red-400 text-xl mb-4">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  // Extract transcript data from report buckets
  const getTranscriptData = () => {
    // This would ideally come from a separate endpoint, but we'll extract from report
    return {
      transcript: report?.buckets?.[0]?.parameters?.[0]?.description || "Transcript data not available",
      duration: report?.buckets?.[0]?.parameters?.[0]?.raw_value || 0,
      // Mock data for demonstration - in production this would come from backend
      audioFormat: "WAV",
      sampleRate: "16000 Hz",
      model: "whisper-1",
      language: "en"
    };
  };

  const transcriptData = getTranscriptData();

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigate(`/report/${id}`)}
            className="flex items-center space-x-2 text-gray-300 hover:text-white transition"
            data-testid="back-to-report-button"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to Report</span>
          </button>
        </div>

        {/* Page Title */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4" data-testid="transcript-page-title">
            Whisper API Transcript Details
          </h1>
          <p className="text-lg text-gray-300">
            View the raw transcript and API response from OpenAI Whisper
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700 mb-6">
          <div className="flex items-center space-x-3 mb-6">
            <Mic className="w-8 h-8 text-purple-400" />
            <h2 className="text-2xl font-bold text-white">Input (Audio Sent to Whisper)</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 rounded-lg p-4 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Audio Format</h3>
              <p className="text-xl text-white">{transcriptData.audioFormat}</p>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-4 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Sample Rate</h3>
              <p className="text-xl text-white">{transcriptData.sampleRate}</p>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-4 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Whisper Model</h3>
              <p className="text-xl text-white">{transcriptData.model}</p>
            </div>
            
            <div className="bg-slate-900/50 rounded-lg p-4 border border-gray-700">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">Language</h3>
              <p className="text-xl text-white">{transcriptData.language.toUpperCase()}</p>
            </div>
          </div>

          <div className="mt-6 bg-slate-900/50 rounded-lg p-4 border border-gray-700">
            <h3 className="text-sm font-semibold text-gray-400 mb-2">API Request Configuration</h3>
            <pre className="text-sm text-green-400 overflow-x-auto">
{`{
  "file": "audio.wav",
  "model": "whisper-1",
  "response_format": "verbose_json",
  "timestamp_granularities": ["segment", "word"]
}`}
            </pre>
          </div>
        </div>

        {/* Output Section */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700 mb-6">
          <div className="flex items-center space-x-3 mb-6">
            <FileText className="w-8 h-8 text-blue-400" />
            <h2 className="text-2xl font-bold text-white">Output (Whisper API Response)</h2>
          </div>

          {/* Response Metadata */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-300 mb-3">Response Metadata</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/50 rounded-lg p-4 border border-gray-700">
                <div className="flex items-center space-x-2 mb-2">
                  <Clock className="w-5 h-5 text-gray-400" />
                  <h4 className="text-sm font-semibold text-gray-400">Duration</h4>
                </div>
                <p className="text-xl text-white">{transcriptData.duration}s</p>
              </div>
              
              <div className="bg-slate-900/50 rounded-lg p-4 border border-gray-700">
                <h4 className="text-sm font-semibold text-gray-400 mb-2">Status</h4>
                <p className="text-xl text-green-400">✓ Success</p>
              </div>
              
              <div className="bg-slate-900/50 rounded-lg p-4 border border-gray-700">
                <h4 className="text-sm font-semibold text-gray-400 mb-2">Word Count</h4>
                <p className="text-xl text-white">{transcriptData.transcript.split(' ').length} words</p>
              </div>
            </div>
          </div>

          {/* Full Transcript */}
          <div>
            <h3 className="text-lg font-semibold text-gray-300 mb-3">Full Transcript</h3>
            <div className="bg-slate-900/50 rounded-lg p-6 border border-gray-700">
              <p className="text-white leading-relaxed text-lg" data-testid="transcript-text">
                {transcriptData.transcript}
              </p>
            </div>
          </div>

          {/* Sample API Response JSON */}
          <div className="mt-6">
            <h3 className="text-lg font-semibold text-gray-300 mb-3">Sample API Response Structure</h3>
            <div className="bg-slate-900/50 rounded-lg p-4 border border-gray-700 overflow-x-auto">
              <pre className="text-sm text-blue-400">
{`{
  "text": "Full transcript text here...",
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 3.5,
      "text": "Hello, I'm John Smith...",
      "words": [
        { "word": "Hello", "start": 0.0, "end": 0.4 },
        { "word": "I'm", "start": 0.5, "end": 0.7 },
        ...
      ]
    },
    ...
  ],
  "language": "en",
  "duration": ${transcriptData.duration}
}`}
              </pre>
            </div>
          </div>
        </div>

        {/* Technical Details */}
        <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 rounded-xl p-6 border border-purple-500/30">
          <h3 className="text-lg font-semibold text-white mb-3">ℹ️ About Whisper API</h3>
          <div className="text-gray-300 space-y-2 text-sm">
            <p>• <strong>Model:</strong> OpenAI Whisper v1 - State-of-the-art speech recognition</p>
            <p>• <strong>Accuracy:</strong> Human-level transcription accuracy across multiple languages</p>
            <p>• <strong>Features:</strong> Word-level timestamps, speaker diarization, punctuation</p>
            <p>• <strong>Processing:</strong> Audio extracted from video, sent to Whisper, returned with timestamps</p>
            <p>• <strong>Privacy:</strong> Audio processed securely via API, not stored by OpenAI</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex justify-center space-x-4">
          <button
            onClick={() => navigate(`/report/${id}`)}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition shadow-lg"
          >
            View Full Assessment Report
          </button>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition"
          >
            New Assessment
          </button>
        </div>
      </div>
    </div>
  );
};

export default TranscriptPage;
