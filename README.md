# Executive Presence Assessment Platform

An AI-powered platform that analyzes executive presence through video assessment. The system evaluates communication skills, nonverbal behavior, and storytelling ability to provide personalized coaching feedback.

## Features

- **Video Analysis**: Upload MP4/MOV files up to 1GB for comprehensive analysis
- **AI-Powered Assessment**: Uses OpenAI's Whisper for speech-to-text and GPT for coaching insights
- **Multi-Modal Analysis**: Evaluates audio, video, and textual content
- **Chunked Uploads**: Handles large files efficiently with 10MB chunked uploads
- **Real-time Feedback**: Detailed scoring and actionable recommendations
- **Secure Storage**: Data stored in Supabase with automatic cleanup

## Tech Stack

### Backend
- **Python/FastAPI**: High-performance API framework
- **OpenAI**: Speech-to-text (Whisper) and GPT-4 for report generation
- **LibROSA/Parselmouth**: Audio analysis for pitch, volume, speaking rate
- **MediaPipe/OpenCV**: Video analysis for posture, gestures, eye contact
- **Supabase**: PostgreSQL database for storing assessment data
- **FFmpeg**: Audio/video processing

### Frontend
- **React**: Modern UI framework
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client for API requests

## Prerequisites

- Python 3.8+
- Node.js 14+
- FFmpeg
- Supabase Account
- OpenAI API Key

## Installation

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd executive-presence-assessment
```

2. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Install system dependencies:
```bash
# On Ubuntu/Debian
sudo apt-get install ffmpeg

# On macOS with Homebrew
brew install ffmpeg
```

### Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
- `OPENAI_API_KEY`: Your OpenAI API key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase service key

## Database Setup

1. Create Supabase tables:
```bash
cd backend
python create_supabase_tables.py
```

## Running the Application

### Start Backend Server
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
cd frontend
npm start
```

## Deployment

### Vercel Deployment

1. Push to your GitHub repository
2. Connect Vercel to your repository
3. Set environment variables in Vercel dashboard:
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `REACT_APP_BACKEND_URL` (your backend URL)

### Docker Deployment (Optional)
```bash
# Build and run with Docker
docker-compose up -d
```

## API Endpoints

### Assessment
- `POST /api/assessment/upload` - Upload video for analysis
- `GET /api/assessment/status/{assessment_id}` - Get processing status
- `GET /api/assessment/report/{assessment_id}` - Get assessment report

### Chunked Upload (for large files)
- `POST /api/chunked-upload/init` - Initialize chunked upload
- `POST /api/chunked-upload/chunk` - Upload a single chunk
- `POST /api/chunked-upload/complete` - Complete upload and start processing
- `DELETE /api/chunked-upload/cancel/{upload_id}` - Cancel upload

## Large File Support

The platform supports video files up to 1GB using chunked uploads:
- Files are split into 10MB chunks
- Each chunk is uploaded separately
- Automatic reassembly on the backend
- Resume capability for failed uploads
- Session persistence using Supabase

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on the GitHub repository or contact the development team.