#!/bin/bash
# Install system dependencies required for audio/video processing
# This script should be run during container startup

set -e

echo "Checking system dependencies..."

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "ffmpeg not found. Installing..."
    apt-get update -qq
    apt-get install -y ffmpeg -qq
    echo "✅ ffmpeg installed successfully"
else
    echo "✅ ffmpeg already installed: $(ffmpeg -version | head -1)"
fi

# Check if ffprobe is installed (comes with ffmpeg)
if ! command -v ffprobe &> /dev/null; then
    echo "❌ ffprobe not found after ffmpeg installation"
    exit 1
else
    echo "✅ ffprobe available: $(ffprobe -version | head -1)"
fi

echo "All system dependencies ready!"
