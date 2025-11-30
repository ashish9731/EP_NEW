"""
Ensure ffmpeg is installed before starting the application
This is a Python-based check that runs during application import
"""
import subprocess
import sys
import os

def check_command(cmd):
    """Check if a command is available"""
    try:
        subprocess.run([cmd, '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_ffmpeg():
    """Install ffmpeg via apt-get"""
    print("⚠️  ffmpeg not found. Attempting to install...")
    try:
        # Update package list
        subprocess.run(['apt-get', 'update', '-qq'], check=True)
        # Install ffmpeg
        subprocess.run(['apt-get', 'install', '-y', 'ffmpeg', '-qq'], check=True)
        print("✅ ffmpeg installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install ffmpeg: {e}")
        return False
    except FileNotFoundError:
        print("❌ apt-get not available. Please install ffmpeg manually.")
        return False

def ensure_ffmpeg():
    """Ensure ffmpeg and ffprobe are available"""
    
    # Check if running in a writeable environment (skip in some restricted environments)
    if os.environ.get('SKIP_FFMPEG_CHECK') == '1':
        return True
    
    # Check ffmpeg
    if not check_command('ffmpeg'):
        print("⚠️  ffmpeg not found")
        if not install_ffmpeg():
            print("❌ CRITICAL: ffmpeg is required for audio processing")
            print("   Please install ffmpeg: apt-get install -y ffmpeg")
            sys.exit(1)
    
    # Check ffprobe
    if not check_command('ffprobe'):
        print("❌ CRITICAL: ffprobe not found (should come with ffmpeg)")
        print("   Please install ffmpeg: apt-get install -y ffmpeg")
        sys.exit(1)
    
    print("✅ ffmpeg and ffprobe are available")
    return True

if __name__ == "__main__":
    ensure_ffmpeg()
