import React, { useState } from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import ProcessingPage from './pages/ProcessingPage';
import ReportPage from './pages/ReportPage';
import TranscriptPage from './pages/TranscriptPage';

function App() {
  const [assessmentId, setAssessmentId] = useState(null);

  return (
    <div className="App min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <BrowserRouter>
        <Routes>
          <Route
            path="/"
            element={<UploadPage onUploadComplete={setAssessmentId} />}
          />
          <Route
            path="/processing/:id"
            element={<ProcessingPage assessmentId={assessmentId} />}
          />
          <Route
            path="/report/:id"
            element={<ReportPage />}
          />
          <Route
            path="/transcript/:id"
            element={<TranscriptPage />}
          />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
