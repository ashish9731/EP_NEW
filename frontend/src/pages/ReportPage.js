import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getReport } from '../api/assessmentApi';
import { ChevronDown, ChevronUp, ArrowLeft, Download, TrendingUp, MessageSquare, User, BookOpen } from 'lucide-react';

const ReportPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedBucket, setExpandedBucket] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const reportData = await getReport(id);
        setReport(reportData);
        // Expand first bucket by default
        if (reportData.buckets && reportData.buckets.length > 0) {
          setExpandedBucket(reportData.buckets[0].name);
        }
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

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreGradient = (score) => {
    if (score >= 80) return 'from-green-500 to-emerald-600';
    if (score >= 60) return 'from-yellow-500 to-orange-600';
    return 'from-red-500 to-pink-600';
  };

  const getBucketIcon = (name) => {
    if (name.includes('Communication')) return <MessageSquare className="w-6 h-6" />;
    if (name.includes('Appearance')) return <User className="w-6 h-6" />;
    if (name.includes('Storytelling')) return <BookOpen className="w-6 h-6" />;
    return <TrendingUp className="w-6 h-6" />;
  };

  const formatReport = (reportText) => {
    if (!reportText) return null;

    const lines = reportText.split('\n');
    const elements = [];
    let currentSection = null;

    lines.forEach((line, index) => {
      const trimmedLine = line.trim();
      
      // Skip empty lines
      if (!trimmedLine) return;

      // Check if it's a bucket heading (COMMUNICATION, APPEARANCE & NONVERBAL, STORYTELLING)
      if (trimmedLine.match(/^(COMMUNICATION|APPEARANCE & NONVERBAL|STORYTELLING)\s*\(Score:/i)) {
        elements.push(
          <div key={index} className="mt-8 mb-4">
            <div className="flex items-center gap-3 border-l-4 border-blue-500 pl-4 py-3 bg-slate-900/50 rounded-r-lg">
              <div className="text-xl font-bold text-blue-400">{trimmedLine}</div>
            </div>
          </div>
        );
        currentSection = 'bucket';
      }
      // Check if it's KEY TAKEAWAYS
      else if (trimmedLine.match(/^KEY TAKEAWAYS$/i)) {
        elements.push(
          <div key={index} className="mt-8 mb-4">
            <div className="flex items-center gap-3 border-l-4 border-purple-500 pl-4 py-3 bg-slate-900/50 rounded-r-lg">
              <div className="text-xl font-bold text-purple-400">{trimmedLine}</div>
            </div>
          </div>
        );
        currentSection = 'takeaways';
      }
      // Check if it's a numbered point (1. 2. 3.)
      else if (trimmedLine.match(/^\d+\.\s+/)) {
        const content = trimmedLine.replace(/^\d+\.\s+/, '');
        const [title, ...rest] = content.split(':');
        
        elements.push(
          <div key={index} className="ml-6 mb-4">
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 text-sm font-bold">
                {trimmedLine.match(/^\d+/)[0]}
              </div>
              <div className="flex-1">
                {title && rest.length > 0 ? (
                  <>
                    <span className="font-semibold text-gray-200">{title}:</span>
                    <span className="text-gray-300"> {rest.join(':')}</span>
                  </>
                ) : (
                  <span className="text-gray-300">{content}</span>
                )}
              </div>
            </div>
          </div>
        );
      }
      // Regular paragraph text
      else {
        elements.push(
          <p key={index} className="text-gray-300 leading-relaxed mb-4">
            {trimmedLine}
          </p>
        );
      }
    });

    return elements;
  };

  const handleDownload = React.useCallback(() => {
    console.log('=== DOWNLOAD BUTTON CLICKED ===');
    console.log('Report exists:', !!report);
    console.log('Report data:', report);
    
    if (!report) {
      alert('⚠️ Report not loaded yet. Please wait...');
      return;
    }

    try {
      const reportText = `EXECUTIVE PRESENCE ASSESSMENT REPORT
====================================

Overall Score: ${report.overall_score || 'N/A'}/100

BUCKET SCORES:
--------------
Communication: ${report.communication_score || 'N/A'}/100
Appearance & Nonverbal: ${report.appearance_score || 'N/A'}/100
Storytelling: ${report.storytelling_score || 'N/A'}/100

DETAILED REPORT:
----------------
${report.llm_report || 'No report available'}

PARAMETER DETAILS:
------------------
${(report.buckets || []).map(bucket => `
${(bucket.name || 'Unknown').toUpperCase()}:
${(bucket.parameters || []).map(param => `  - ${param.name || 'Unknown'}: ${param.score || 0}/100
    ${param.description || 'No description'}`).join('\n')}
`).join('\n')}

Generated: ${new Date().toLocaleString()}
`;

      const blob = new Blob([reportText], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `report-${report.assessment_id || Date.now()}.txt`;
      link.style.display = 'none';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      console.log('✅ Download triggered successfully');
      alert('✅ Report downloaded!');
    } catch (error) {
      console.error('❌ Download error:', error);
      alert(`❌ Download failed: ${error.message}`);
    }
  }, [report]);

  const handlePrint = React.useCallback(() => {
    console.log('=== PRINT BUTTON CLICKED ===');
    console.log('Report exists:', !!report);
    
    if (!report) {
      alert('⚠️ Report not loaded yet. Please wait...');
      return;
    }

    try {
      console.log('Opening print dialog...');
      window.print();
      console.log('✅ Print dialog opened');
    } catch (error) {
      console.error('❌ Print error:', error);
      alert(`❌ Print failed: ${error.message}\nTry: Ctrl+P (Windows) or Cmd+P (Mac)`);
    }
  }, [report]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white text-xl">Loading report...</div>
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

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={() => navigate('/')}
            className="flex items-center space-x-2 text-gray-300 hover:text-white transition"
            data-testid="back-button"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>New Assessment</span>
          </button>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => navigate(`/transcript/${id}`)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition shadow-lg"
              data-testid="view-transcript-button"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span>View Transcript</span>
            </button>
            <button
              onClick={handleDownload}
              type="button"
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition shadow-lg cursor-pointer"
              style={{ pointerEvents: 'auto' }}
              data-testid="download-report-button"
            >
              <Download className="w-5 h-5" />
              <span>Download</span>
            </button>
            <button
              onClick={handlePrint}
              type="button"
              className="flex items-center space-x-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition cursor-pointer"
              style={{ pointerEvents: 'auto' }}
              data-testid="print-report-button"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
              <span>Print</span>
            </button>
          </div>
        </div>

        {/* Overall Score */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6" data-testid="report-title">
            Your Executive Presence Report
          </h1>
          <div className="flex justify-center mb-8">
            <div className="relative w-56 h-56 score-circle">
              <svg className="transform -rotate-90 w-56 h-56">
                <circle
                  cx="112"
                  cy="112"
                  r="100"
                  stroke="currentColor"
                  strokeWidth="12"
                  fill="transparent"
                  className="text-gray-700"
                />
                <circle
                  cx="112"
                  cy="112"
                  r="100"
                  stroke="url(#gradient)"
                  strokeWidth="12"
                  fill="transparent"
                  strokeDasharray={`${2 * Math.PI * 100}`}
                  strokeDashoffset={`${2 * Math.PI * 100 * (1 - report.overall_score / 100)}`}
                  strokeLinecap="round"
                />
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#667eea" />
                    <stop offset="100%" stopColor="#764ba2" />
                  </linearGradient>
                </defs>
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-6xl font-bold text-white" data-testid="overall-score">
                  {report.overall_score}
                </span>
                <span className="text-gray-400 text-lg">/ 100</span>
              </div>
            </div>
          </div>

          {/* Bucket Scores Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto mb-8">
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700" data-testid="communication-bucket-card">
              <div className="flex items-center justify-center mb-2">
                <MessageSquare className="w-8 h-8 text-blue-400" />
              </div>
              <h3 className="text-gray-300 text-sm font-medium mb-1">Communication</h3>
              <p className={`text-3xl font-bold ${getScoreColor(report.communication_score)}`} data-testid="communication-score">
                {report.communication_score}
              </p>
            </div>
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700" data-testid="appearance-bucket-card">
              <div className="flex items-center justify-center mb-2">
                <User className="w-8 h-8 text-purple-400" />
              </div>
              <h3 className="text-gray-300 text-sm font-medium mb-1">Appearance & Nonverbal</h3>
              <p className={`text-3xl font-bold ${getScoreColor(report.appearance_score)}`} data-testid="appearance-score">
                {report.appearance_score}
              </p>
            </div>
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700" data-testid="storytelling-bucket-card">
              <div className="flex items-center justify-center mb-2">
                <BookOpen className="w-8 h-8 text-pink-400" />
              </div>
              <h3 className="text-gray-300 text-sm font-medium mb-1">Storytelling</h3>
              <p className={`text-3xl font-bold ${getScoreColor(report.storytelling_score)}`} data-testid="storytelling-score">
                {report.storytelling_score}
              </p>
            </div>
          </div>
        </div>

        {/* LLM Report */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 border border-gray-700 mb-8" data-testid="llm-report-section">
          <h2 className="text-2xl font-bold text-white mb-6">Your Executive Presence Insights</h2>
          <div className="space-y-6" data-testid="llm-report-content">
            {formatReport(report.llm_report)}
          </div>
        </div>

        {/* Detailed Parameters */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-white mb-4">Detailed Scores</h2>
          {report.buckets.map((bucket, index) => (
            <div
              key={index}
              className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-gray-700 overflow-hidden"
              data-testid={`bucket-${index}`}
            >
              <button
                onClick={() => setExpandedBucket(expandedBucket === bucket.name ? null : bucket.name)}
                className="w-full flex items-center justify-between p-6 hover:bg-slate-700/30 transition"
                data-testid={`bucket-toggle-${index}`}
              >
                <div className="flex items-center space-x-4">
                  <div className="text-purple-400">
                    {getBucketIcon(bucket.name)}
                  </div>
                  <div className="text-left">
                    <h3 className="text-xl font-semibold text-white">{bucket.name}</h3>
                    <p className="text-gray-400 text-sm">{bucket.parameters.length} parameters</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <span className={`text-3xl font-bold ${getScoreColor(bucket.score)}`}>
                    {bucket.score}
                  </span>
                  {expandedBucket === bucket.name ? (
                    <ChevronUp className="w-6 h-6 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-6 h-6 text-gray-400" />
                  )}
                </div>
              </button>

              {expandedBucket === bucket.name && (
                <div className="px-6 pb-6 space-y-4" data-testid={`bucket-details-${index}`}>
                  {bucket.parameters.map((param, paramIndex) => (
                    <div
                      key={paramIndex}
                      className="bg-slate-900/50 rounded-lg p-4 border border-gray-700"
                      data-testid={`parameter-${paramIndex}`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="text-lg font-semibold text-white">{param.name}</h4>
                        <span className={`text-2xl font-bold ${getScoreColor(param.score)}`}>
                          {param.score}
                        </span>
                      </div>
                      <p className="text-gray-400 text-sm mb-2">{param.description}</p>
                      {param.raw_value !== null && param.raw_value !== undefined && (
                        <p className="text-gray-500 text-xs">
                          Raw Value: {param.raw_value} {param.unit}
                        </p>
                      )}
                      {/* Progress Bar */}
                      <div className="mt-3 w-full bg-gray-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full bg-gradient-to-r ${getScoreGradient(param.score)}`}
                          style={{ width: `${param.score}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-400 text-sm">
          <p>This assessment is based on a single 3-minute video sample and provides a point-in-time view of your executive presence.</p>
          <p className="mt-2">For best results, record multiple samples over time to track your progress.</p>
        </div>
      </div>
    </div>
  );
};

export default ReportPage;
