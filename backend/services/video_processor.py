import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List
import os

class VideoProcessor:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_face_detection = mp.solutions.face_detection
        
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            min_detection_confidence=0.5
        )
        
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5
        )
    
    def extract_frames(self, video_path: str, fps: int = 2) -> List[np.ndarray]:
        """Extract frames from video at specified FPS"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(video_fps / fps)
        
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            frame_count += 1
        
        cap.release()
        return frames
    
    def analyze_posture(self, frames: List[np.ndarray]) -> Dict:
        """Analyze posture using pose landmarks"""
        upright_count = 0
        open_posture_count = 0
        total_frames = len(frames)
        
        for frame in frames:
            results = self.pose.process(frame)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Check spine angle (shoulders to hips)
                left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
                left_hip = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP]
                
                # Calculate vertical alignment
                shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
                hip_y = (left_hip.y + right_hip.y) / 2
                
                # Upright if shoulders above hips with good margin
                if shoulder_y < hip_y - 0.1:
                    upright_count += 1
                
                # Check shoulder openness
                shoulder_width = abs(right_shoulder.x - left_shoulder.x)
                if shoulder_width > 0.25:  # Open posture threshold
                    open_posture_count += 1
        
        upright_ratio = upright_count / total_frames if total_frames > 0 else 0
        open_ratio = open_posture_count / total_frames if total_frames > 0 else 0
        
        # Score based on both metrics
        posture_score = (upright_ratio * 0.6 + open_ratio * 0.4) * 100
        
        return {
            "upright_ratio": round(upright_ratio, 2),
            "open_posture_ratio": round(open_ratio, 2),
            "score": round(posture_score, 1)
        }
    
    def analyze_body_expansiveness(self, frames: List[np.ndarray]) -> Dict:
        """Measure body expansiveness (dominance cues)"""
        expansiveness_scores = []
        
        for frame in frames:
            results = self.pose.process(frame)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                # Calculate bounding box width (shoulders + arms)
                left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
                left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
                right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
                
                # Width from outermost points
                min_x = min(left_shoulder.x, right_shoulder.x, left_wrist.x, right_wrist.x)
                max_x = max(left_shoulder.x, right_shoulder.x, left_wrist.x, right_wrist.x)
                
                width = max_x - min_x
                expansiveness_scores.append(width)
        
        if len(expansiveness_scores) > 0:
            avg_expansiveness = np.mean(expansiveness_scores)
            std_expansiveness = np.std(expansiveness_scores)
            
            # Ideal: moderate expansiveness (0.35-0.55), stable
            if 0.35 <= avg_expansiveness <= 0.55 and std_expansiveness < 0.1:
                score = 100
            elif 0.3 <= avg_expansiveness <= 0.6 and std_expansiveness < 0.15:
                score = 85
            elif 0.25 <= avg_expansiveness <= 0.65:
                score = 70
            else:
                score = 50
        else:
            avg_expansiveness = 0
            score = 50
        
        return {
            "avg_expansiveness": round(avg_expansiveness, 2),
            "score": round(score, 1)
        }
    
    def analyze_eye_contact(self, frames: List[np.ndarray]) -> Dict:
        """Estimate eye contact with camera using head pose"""
        eye_contact_frames = 0
        total_frames = len(frames)
        
        for frame in frames:
            results = self.face_mesh.process(frame)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # Use nose tip and eye landmarks to estimate gaze
                nose_tip = face_landmarks.landmark[1]
                left_eye = face_landmarks.landmark[33]
                right_eye = face_landmarks.landmark[263]
                
                # Check if face is frontal (rough approximation)
                eye_center_x = (left_eye.x + right_eye.x) / 2
                nose_offset = abs(nose_tip.x - eye_center_x)
                
                # Eye contact if face is relatively frontal
                if nose_offset < 0.05:
                    eye_contact_frames += 1
        
        eye_contact_ratio = eye_contact_frames / total_frames if total_frames > 0 else 0
        
        # Ideal: 60-80% eye contact
        if 0.6 <= eye_contact_ratio <= 0.8:
            score = 100
        elif 0.5 <= eye_contact_ratio < 0.6 or 0.8 < eye_contact_ratio <= 0.9:
            score = 85
        elif 0.4 <= eye_contact_ratio < 0.5 or eye_contact_ratio > 0.9:
            score = 70
        else:
            score = max(40, 70 - abs(eye_contact_ratio - 0.7) * 100)
        
        return {
            "eye_contact_ratio": round(eye_contact_ratio, 2),
            "eye_contact_frames": eye_contact_frames,
            "total_frames": total_frames,
            "score": round(score, 1)
        }
    
    def analyze_facial_expressions(self, frames: List[np.ndarray]) -> Dict:
        """Analyze facial expressions (simplified - detect smile)"""
        positive_frames = 0
        total_frames = len(frames)
        
        for frame in frames:
            results = self.face_mesh.process(frame)
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # Detect smile using mouth corners
                left_mouth = face_landmarks.landmark[61]
                right_mouth = face_landmarks.landmark[291]
                upper_lip = face_landmarks.landmark[13]
                lower_lip = face_landmarks.landmark[14]
                
                # Calculate mouth width vs height ratio
                mouth_width = abs(right_mouth.x - left_mouth.x)
                mouth_height = abs(lower_lip.y - upper_lip.y)
                
                # Smile detection (wide mouth)
                if mouth_width / (mouth_height + 0.01) > 3.5:
                    positive_frames += 1
        
        positive_ratio = positive_frames / total_frames if total_frames > 0 else 0
        
        # Ideal: 20-40% smiling (context-appropriate)
        if 0.2 <= positive_ratio <= 0.4:
            score = 100
        elif 0.15 <= positive_ratio < 0.2 or 0.4 < positive_ratio <= 0.5:
            score = 85
        elif 0.1 <= positive_ratio < 0.15 or 0.5 < positive_ratio <= 0.6:
            score = 70
        else:
            score = max(50, 70 - abs(positive_ratio - 0.3) * 100)
        
        return {
            "positive_expression_ratio": round(positive_ratio, 2),
            "smile_frames": positive_frames,
            "score": round(score, 1)
        }
    
    def analyze_gestures(self, frames: List[np.ndarray]) -> Dict:
        """Analyze hand gestures and movement"""
        gesture_frames = []
        
        for i, frame in enumerate(frames):
            results = self.pose.process(frame)
            
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                
                left_wrist = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST]
                right_wrist = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST]
                
                gesture_frames.append({
                    "frame": i,
                    "left_wrist_y": left_wrist.y,
                    "right_wrist_y": right_wrist.y
                })
        
        if len(gesture_frames) > 1:
            # Calculate movement amplitude
            movements = []
            for i in range(1, len(gesture_frames)):
                left_movement = abs(gesture_frames[i]["left_wrist_y"] - gesture_frames[i-1]["left_wrist_y"])
                right_movement = abs(gesture_frames[i]["right_wrist_y"] - gesture_frames[i-1]["right_wrist_y"])
                movements.append(max(left_movement, right_movement))
            
            avg_movement = np.mean(movements)
            gesture_count = sum(1 for m in movements if m > 0.05)  # Significant movements
            
            # Ideal: moderate gesturing
            if 0.02 <= avg_movement <= 0.08:
                score = 100
            elif 0.01 <= avg_movement < 0.02 or 0.08 < avg_movement <= 0.12:
                score = 80
            else:
                score = 60
        else:
            avg_movement = 0
            gesture_count = 0
            score = 50
        
        return {
            "avg_gesture_amplitude": round(avg_movement, 3),
            "gesture_count": gesture_count,
            "score": round(score, 1)
        }
    
    def analyze_first_impression(self, frames: List[np.ndarray], fps: int = 2) -> Dict:
        """Analyze first 7-10 seconds"""
        # Take first 20 frames (10 seconds at 2fps)
        first_frames = frames[:20]
        
        if len(first_frames) < 5:
            return {"score": 50, "message": "Insufficient frames"}
        
        # Run mini-analysis
        posture = self.analyze_posture(first_frames)
        eye_contact = self.analyze_eye_contact(first_frames)
        expressions = self.analyze_facial_expressions(first_frames)
        
        # Combine scores
        first_impression_score = (
            posture["score"] * 0.4 +
            eye_contact["score"] * 0.4 +
            expressions["score"] * 0.2
        )
        
        return {
            "score": round(first_impression_score, 1),
            "posture_score": posture["score"],
            "eye_contact_score": eye_contact["score"],
            "expression_score": expressions["score"]
        }
    
    def process_video(self, video_path: str) -> Dict:
        """Main video processing pipeline"""
        # Extract frames
        frames = self.extract_frames(video_path, fps=2)
        
        if len(frames) < 10:
            raise Exception("Video too short or failed to extract frames")
        
        # Analyze all parameters
        posture = self.analyze_posture(frames)
        expansiveness = self.analyze_body_expansiveness(frames)
        eye_contact = self.analyze_eye_contact(frames)
        expressions = self.analyze_facial_expressions(frames)
        gestures = self.analyze_gestures(frames)
        first_impression = self.analyze_first_impression(frames)
        
        return {
            "frame_count": len(frames),
            "posture": posture,
            "expansiveness": expansiveness,
            "eye_contact": eye_contact,
            "expressions": expressions,
            "gestures": gestures,
            "first_impression": first_impression
        }
