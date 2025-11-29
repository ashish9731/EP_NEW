import os
import librosa
import numpy as np
import parselmouth
from parselmouth.praat import call
import soundfile as sf
from pydub import AudioSegment
from typing import Dict, List, Tuple
import re
from emergentintegrations.llm.openai import OpenAISpeechToText
from dotenv import load_dotenv
import tempfile

load_dotenv()

class AudioProcessor:
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        self.stt = OpenAISpeechToText(api_key=self.api_key)
        
        # Filler words to detect
        self.filler_words = [
            r'\bum\b', r'\buh\b', r'\blike\b', r'\byou know\b', 
            r'\bbasically\b', r'\bliterally\b', r'\bactually\b',
            r'\bkind of\b', r'\bsort of\b', r'\byeah\b', r'\bso\b'
        ]
        
        # Hedging phrases
        self.hedging_phrases = [
            r'i think', r'maybe', r'perhaps', r'possibly', r'might',
            r'could be', r'i guess', r'sort of', r'kind of'
        ]
        
        # Confidence phrases
        self.confidence_phrases = [
            r'i will', r'we will', r'definitely', r'certainly',
            r'i know', r'we know', r'clearly', r'obviously'
        ]
    
    async def extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio from video file and save as WAV"""
        # Handle both uppercase and lowercase extensions
        audio_path = video_path
        for ext in ['.mp4', '.MP4', '.mov', '.MOV']:
            audio_path = audio_path.replace(ext, '.wav')
        
        try:
            video = AudioSegment.from_file(video_path)
            video.export(audio_path, format="wav")
            return audio_path
        except Exception as e:
            raise Exception(f"Failed to extract audio: {str(e)}")
    
    async def transcribe_audio(self, audio_path: str) -> Dict:
        """Transcribe audio using OpenAI Whisper API"""
        try:
            with open(audio_path, "rb") as audio_file:
                response = await self.stt.transcribe(
                    file=audio_file,
                    model="whisper-1",
                    response_format="verbose_json",
                    timestamp_granularities=["segment", "word"]
                )
            
            transcript = response.text
            segments = response.segments if hasattr(response, 'segments') else []
            words = response.words if hasattr(response, 'words') else []
            
            return {
                "transcript": transcript,
                "segments": segments,
                "words": words
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def calculate_speaking_rate(self, transcript: str, duration: float) -> Dict:
        """Calculate words per minute"""
        words = transcript.split()
        word_count = len(words)
        duration_minutes = duration / 60.0
        
        wpm = word_count / duration_minutes if duration_minutes > 0 else 0
        
        # Ideal range: 130-170 WPM (140-160 preferred)
        if 140 <= wpm <= 160:
            score = 100
        elif 130 <= wpm < 140:
            score = 80 + ((wpm - 130) / 10) * 20
        elif 160 < wpm <= 170:
            score = 80 + ((170 - wpm) / 10) * 20
        elif 120 <= wpm < 130:
            score = 60 + ((wpm - 120) / 10) * 20
        elif 170 < wpm <= 180:
            score = 60 + ((180 - wpm) / 10) * 20
        else:
            score = max(0, 60 - abs(wpm - 150) / 2)
        
        return {
            "wpm": round(wpm, 1),
            "score": round(score, 1),
            "description": f"Speaking rate of {round(wpm, 1)} WPM"
        }
    
    def analyze_pitch(self, audio_path: str) -> Dict:
        """Analyze pitch using Parselmouth"""
        try:
            sound = parselmouth.Sound(audio_path)
            pitch = call(sound, "To Pitch", 0.0, 75, 500)
            
            # Extract pitch values
            pitch_values = pitch.selected_array['frequency']
            pitch_values = pitch_values[pitch_values > 0]  # Remove unvoiced
            
            if len(pitch_values) == 0:
                return {
                    "mean_pitch_hz": 0,
                    "pitch_range_hz": 0,
                    "pitch_std": 0,
                    "pitch_score": 50,
                    "variety_score": 50
                }
            
            mean_pitch = np.mean(pitch_values)
            pitch_std = np.std(pitch_values)
            pitch_range = np.max(pitch_values) - np.min(pitch_values)
            
            # Score based on typical ranges
            # Male: 100-150 Hz, Female: 180-250 Hz
            if 100 <= mean_pitch <= 150 or 180 <= mean_pitch <= 250:
                pitch_score = 100
            elif 90 <= mean_pitch < 100 or 150 < mean_pitch < 180 or 250 < mean_pitch <= 260:
                pitch_score = 80
            else:
                pitch_score = max(50, 100 - abs(mean_pitch - 150) / 3)
            
            # Vocal variety score (based on pitch modulation)
            # Good variety: std > 20 Hz
            if pitch_std > 25:
                variety_score = 100
            elif pitch_std > 20:
                variety_score = 90
            elif pitch_std > 15:
                variety_score = 75
            elif pitch_std > 10:
                variety_score = 60
            else:
                variety_score = 40
            
            return {
                "mean_pitch_hz": round(mean_pitch, 1),
                "pitch_range_hz": round(pitch_range, 1),
                "pitch_std": round(pitch_std, 1),
                "pitch_score": round(pitch_score, 1),
                "variety_score": round(variety_score, 1)
            }
        except Exception as e:
            return {
                "mean_pitch_hz": 0,
                "pitch_range_hz": 0,
                "pitch_std": 0,
                "pitch_score": 50,
                "variety_score": 50
            }
    
    def analyze_volume(self, audio_path: str) -> Dict:
        """Analyze loudness and volume control"""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            
            # Calculate RMS energy
            rms = librosa.feature.rms(y=y)[0]
            mean_volume = np.mean(rms)
            volume_std = np.std(rms)
            
            # Convert to dB
            mean_db = 20 * np.log10(mean_volume + 1e-6)
            
            # Score based on audibility and stability
            # Good: -20 to -10 dB, low std
            if -20 <= mean_db <= -10:
                volume_score = 100
            elif -25 <= mean_db < -20 or -10 < mean_db <= -5:
                volume_score = 80
            else:
                volume_score = max(40, 80 - abs(mean_db + 15) * 2)
            
            # Penalize high variance (inconsistent volume)
            if volume_std < 0.01:
                stability_score = 100
            elif volume_std < 0.02:
                stability_score = 85
            elif volume_std < 0.03:
                stability_score = 70
            else:
                stability_score = max(50, 70 - (volume_std - 0.03) * 500)
            
            final_score = (volume_score + stability_score) / 2
            
            return {
                "mean_volume_db": round(mean_db, 1),
                "volume_std": round(volume_std, 3),
                "score": round(final_score, 1)
            }
        except Exception as e:
            return {
                "mean_volume_db": 0,
                "volume_std": 0,
                "score": 50
            }
    
    def detect_pauses(self, audio_path: str, transcript_data: Dict) -> Dict:
        """Detect and analyze pauses"""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Detect non-silent intervals
            intervals = librosa.effects.split(y, top_db=30)
            
            # Calculate pauses
            pauses = []
            if len(intervals) > 1:
                for i in range(len(intervals) - 1):
                    pause_start = intervals[i][1] / sr
                    pause_end = intervals[i + 1][0] / sr
                    pause_duration = pause_end - pause_start
                    if 0.2 < pause_duration < 5:  # Filter out very short/long
                        pauses.append(pause_duration)
            
            if len(pauses) > 0:
                avg_pause = np.mean(pauses)
                pauses_per_min = (len(pauses) / duration) * 60
            else:
                avg_pause = 0
                pauses_per_min = 0
            
            # Ideal: frequent short pauses (0.3-1.5s, 8-15 per minute)
            if 0.5 <= avg_pause <= 1.2 and 8 <= pauses_per_min <= 15:
                score = 100
            elif 0.3 <= avg_pause <= 1.5 and 5 <= pauses_per_min <= 20:
                score = 80
            elif 0.2 <= avg_pause <= 2.0 and 3 <= pauses_per_min <= 25:
                score = 60
            else:
                score = 40
            
            return {
                "pause_count": len(pauses),
                "avg_pause_duration_s": round(avg_pause, 2),
                "pauses_per_minute": round(pauses_per_min, 1),
                "score": round(score, 1)
            }
        except Exception as e:
            return {
                "pause_count": 0,
                "avg_pause_duration_s": 0,
                "pauses_per_minute": 0,
                "score": 50
            }
    
    def detect_fillers(self, transcript: str) -> Dict:
        """Detect filler words"""
        transcript_lower = transcript.lower()
        word_count = len(transcript.split())
        
        filler_count = 0
        for pattern in self.filler_words:
            filler_count += len(re.findall(pattern, transcript_lower))
        
        fillers_per_100 = (filler_count / word_count) * 100 if word_count > 0 else 0
        
        # Ideal: < 3 fillers per 100 words
        if fillers_per_100 < 2:
            score = 100
        elif fillers_per_100 < 3:
            score = 90
        elif fillers_per_100 < 5:
            score = 75
        elif fillers_per_100 < 8:
            score = 60
        else:
            score = max(30, 60 - (fillers_per_100 - 8) * 5)
        
        return {
            "filler_count": filler_count,
            "fillers_per_100_words": round(fillers_per_100, 2),
            "score": round(score, 1)
        }
    
    def analyze_clarity(self, transcript: str) -> Dict:
        """Analyze verbal clarity and readability"""
        sentences = transcript.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) == 0:
            return {"avg_sentence_length": 0, "score": 50}
        
        words = transcript.split()
        avg_sentence_length = len(words) / len(sentences)
        
        # Ideal: 15-20 words per sentence
        if 15 <= avg_sentence_length <= 20:
            score = 100
        elif 12 <= avg_sentence_length < 15 or 20 < avg_sentence_length <= 25:
            score = 85
        elif 10 <= avg_sentence_length < 12 or 25 < avg_sentence_length <= 30:
            score = 70
        else:
            score = max(40, 70 - abs(avg_sentence_length - 17) * 2)
        
        return {
            "avg_sentence_length": round(avg_sentence_length, 1),
            "sentence_count": len(sentences),
            "score": round(score, 1)
        }
    
    def analyze_confidence(self, transcript: str) -> Dict:
        """Analyze confidence vs hedging language"""
        transcript_lower = transcript.lower()
        
        hedging_count = 0
        for pattern in self.hedging_phrases:
            hedging_count += len(re.findall(pattern, transcript_lower))
        
        confidence_count = 0
        for pattern in self.confidence_phrases:
            confidence_count += len(re.findall(pattern, transcript_lower))
        
        # Calculate ratio
        total = hedging_count + confidence_count
        if total == 0:
            confidence_ratio = 0.5
        else:
            confidence_ratio = confidence_count / total
        
        # Score based on higher confidence language
        if confidence_ratio >= 0.7:
            score = 100
        elif confidence_ratio >= 0.6:
            score = 90
        elif confidence_ratio >= 0.5:
            score = 75
        elif confidence_ratio >= 0.4:
            score = 60
        else:
            score = max(40, 60 - (0.4 - confidence_ratio) * 100)
        
        return {
            "hedging_count": hedging_count,
            "confidence_count": confidence_count,
            "confidence_ratio": round(confidence_ratio, 2),
            "score": round(score, 1)
        }
    
    async def process_audio(self, video_path: str) -> Dict:
        """Main audio processing pipeline"""
        # Extract audio
        audio_path = await self.extract_audio_from_video(video_path)
        
        # Get duration
        y, sr = librosa.load(audio_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        
        # Transcribe
        transcript_data = await self.transcribe_audio(audio_path)
        transcript = transcript_data["transcript"]
        
        # Analyze all parameters
        speaking_rate = self.calculate_speaking_rate(transcript, duration)
        pitch_analysis = self.analyze_pitch(audio_path)
        volume_analysis = self.analyze_volume(audio_path)
        pause_analysis = self.detect_pauses(audio_path, transcript_data)
        filler_analysis = self.detect_fillers(transcript)
        clarity_analysis = self.analyze_clarity(transcript)
        confidence_analysis = self.analyze_confidence(transcript)
        
        # Clean up audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return {
            "transcript": transcript,
            "duration": round(duration, 1),
            "speaking_rate": speaking_rate,
            "pitch": pitch_analysis,
            "volume": volume_analysis,
            "pauses": pause_analysis,
            "fillers": filler_analysis,
            "clarity": clarity_analysis,
            "confidence": confidence_analysis
        }
