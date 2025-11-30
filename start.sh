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
if [ -f /app/backend/install_system_deps.sh ]; then
    bash /app/backend/install_system_deps.sh
else
    echo "Installing ffmpeg..."
    apt-get update -qq && apt-get install -y ffmpeg -qq
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
mkdir -p /app/backend/uploads
mkdir -p /app/backend/temp_chunks
echo "✅ Directories created"

# Check environment variables
echo ""
echo "4. Checking environment variables..."
if [ -z "$MONGO_URL" ]; then
    echo "⚠️  WARNING: MONGO_URL not set"
else
    echo "✅ MONGO_URL configured"
fi

if [ -z "$DB_NAME" ]; then
    echo "⚠️  WARNING: DB_NAME not set"
else
    echo "✅ DB_NAME configured"
fi

if [ -z "$EMERGENT_LLM_KEY" ]; then
    echo "⚠️  WARNING: EMERGENT_LLM_KEY not set"
else
    echo "✅ EMERGENT_LLM_KEY configured"
fi

echo ""
echo "=========================================="
echo "Startup Complete - Services Starting..."
echo "=========================================="
