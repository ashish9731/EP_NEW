import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getStatus } from '../api/assessmentApi';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';

const ProcessingPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) {
      navigate('/');
      return;
    }

    const checkStatus = async () => {
      try {
        const statusData = await getStatus(id);
        setStatus(statusData);

        if (statusData.status === 'completed') {
          // Wait a moment before redirecting
          setTimeout(() => {
            navigate(`/report/${id}`);
          }, 1000);
        } else if (statusData.status === 'failed') {
          setError(statusData.error || 'Processing failed');
        }
      } catch (err) {
        setError(err.message);
      }
    };

    // Initial check
    checkStatus();

    // Poll every 2 seconds
    const interval = setInterval(checkStatus, 2000);

    return () => clearInterval(interval);
  }, [id, navigate]);

  const getStepStatus = (stepProgress) => {
    if (!status) return 'pending';
    if (status.progress >= stepProgress) return 'complete';
    if (status.progress >= stepProgress - 20) return 'active';
    return 'pending';
  };

  const steps = [
    { name: 'Uploading Video', progress: 5, icon: '📤' },
    { name: 'Extracting Audio', progress: 20, icon: '🎵' },
    { name: 'Analyzing Speech', progress: 40, icon: '🗣️' },
    { name: 'Analyzing Video', progress: 60, icon: '🎥' },
    { name: 'Detecting Storytelling', progress: 80, icon: '📖' },
    { name: 'Calculating Scores', progress: 90, icon: '📊' },
    { name: 'Generating Report', progress: 95, icon: '📝' },
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-3xl">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-4" data-testid="processing-page-title">
            Analyzing Your Executive Presence
          </h1>
          <p className="text-lg text-gray-300">
            This will take about 2-3 minutes. Hang tight!
          </p>
        </div>

        {/* Progress Circle */}
        <div className="flex justify-center mb-12">
          <div className="relative w-48 h-48">
            <svg className="transform -rotate-90 w-48 h-48">
              <circle
                cx="96"
                cy="96"
                r="88"
                stroke="currentColor"
                strokeWidth="8"
                fill="transparent"
                className="text-gray-700"
              />
              <circle
                cx="96"
                cy="96"
                r="88"
                stroke="currentColor"
                strokeWidth="8"
                fill="transparent"
                strokeDasharray={`${2 * Math.PI * 88}`}
                strokeDashoffset={`${2 * Math.PI * 88 * (1 - (status?.progress || 0) / 100)}`}
                className="text-purple-500 transition-all duration-500"
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              {status?.status === 'completed' ? (
                <CheckCircle2 className="w-16 h-16 text-green-400" data-testid="processing-complete-icon" />
              ) : error ? (
                <XCircle className="w-16 h-16 text-red-400" data-testid="processing-error-icon" />
              ) : (
                <>
                  <Loader2 className="w-12 h-12 text-purple-400 animate-spin mb-2" data-testid="processing-spinner" />
                  <span className="text-3xl font-bold text-white" data-testid="processing-progress-percentage">
                    {status?.progress || 0}%
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Current Status Message */}
        <div className="text-center mb-8">
          <p className="text-xl text-gray-300 font-medium" data-testid="processing-status-message">
            {error ? error : status?.message || 'Initializing...'}
          </p>
        </div>

        {/* Processing Steps */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700">
          <div className="space-y-4">
            {steps.map((step, index) => {
              const stepStatus = getStepStatus(step.progress);
              return (
                <div
                  key={index}
                  className={`flex items-center space-x-4 p-4 rounded-lg transition-all ${
                    stepStatus === 'complete'
                      ? 'bg-green-900/20 border border-green-500/30'
                      : stepStatus === 'active'
                      ? 'bg-purple-900/20 border border-purple-500/30 animate-pulse-slow'
                      : 'bg-gray-800/30 border border-gray-700/30'
                  }`}
                  data-testid={`processing-step-${index}`}
                >
                  <div className="text-3xl">{step.icon}</div>
                  <div className="flex-1">
                    <h3 className={`font-semibold ${
                      stepStatus === 'complete' ? 'text-green-300' :
                      stepStatus === 'active' ? 'text-purple-300' :
                      'text-gray-500'
                    }`}>
                      {step.name}
                    </h3>
                  </div>
                  <div>
                    {stepStatus === 'complete' && (
                      <CheckCircle2 className="w-6 h-6 text-green-400" />
                    )}
                    {stepStatus === 'active' && (
                      <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mt-6 bg-red-900/20 border border-red-500 rounded-lg p-4 text-center" data-testid="processing-error-display">
            <p className="text-red-300">{error}</p>
            <button
              onClick={() => navigate('/')}
              className="mt-4 px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition"
              data-testid="back-to-home-button"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Fun Fact */}
        {!error && status?.status !== 'completed' && (
          <div className="mt-8 text-center text-gray-400 text-sm italic">
            <p>💡 Did you know? Studies show that 55% of communication impact comes from body language</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessingPage;
