#!/bin/bash
# Startup script for Executive Presence Assessment App
# This ensures all dependencies are installed before starting services

set -e

echo "=========================================="
echo "Executive Presence Assessment App Startup"
echo "=========================================="

# Install system dependencies (ffmpeg)
echo ""
echo "1. Installing system dependencies..."
if [ -f ./backend/install_system_deps.sh ]; then
    bash ./backend/install_system_deps.sh
else
    echo "Installing ffmpeg..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "Warning: Package manager not found. Please install ffmpeg manually."
    fi
fi

# Verify ffmpeg installation
echo ""
echo "2. Verifying ffmpeg installation..."
if command -v ffmpeg &> /dev/null && command -v ffprobe &> /dev/null; then
    echo "✅ ffmpeg: $(ffmpeg -version | head -1)"
    echo "✅ ffprobe: $(ffprobe -version | head -1)"
else
    echo "❌ ERROR: ffmpeg/ffprobe not installed properly"
    exit 1
fi

# Create necessary directories
echo ""
echo "3. Creating required directories..."
mkdir -p ./backend/uploads
mkdir -p ./backend/temp_chunks
echo "✅ Directories created"

# Check environment variables
echo ""
echo "4. Checking environment variables..."
if [ -z "$SUPABASE_URL" ]; then
    echo "⚠️  WARNING: SUPABASE_URL not set"
else
    echo "✅ SUPABASE_URL configured"
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo "⚠️  WARNING: SUPABASE_KEY not set"
else
    echo "✅ SUPABASE_KEY configured"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY not set"
else
    echo "✅ OPENAI_API_KEY configured"
fi

echo ""
echo "=========================================="
echo "Startup Complete - Services Starting..."
echo "=========================================="
