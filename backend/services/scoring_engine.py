from typing import Dict, List
from models.assessment_models import ParameterScore, BucketScore

class ScoringEngine:
    def calculate_parameter_scores(self, audio_features: Dict, video_features: Dict, nlp_features: Dict) -> Dict:
        """Calculate individual parameter scores"""
        
        # Communication parameters
        communication_params = [
            ParameterScore(
                name="Speaking Rate",
                score=audio_features["speaking_rate"]["score"],
                raw_value=audio_features["speaking_rate"]["wpm"],
                unit="WPM",
                description=audio_features["speaking_rate"]["description"]
            ),
            ParameterScore(
                name="Vocal Pitch",
                score=audio_features["pitch"]["pitch_score"],
                raw_value=audio_features["pitch"]["mean_pitch_hz"],
                unit="Hz",
                description=f"Mean pitch of {audio_features['pitch']['mean_pitch_hz']} Hz"
            ),
            ParameterScore(
                name="Vocal Variety",
                score=audio_features["pitch"]["variety_score"],
                raw_value=audio_features["pitch"]["pitch_std"],
                unit="Hz std",
                description=f"Pitch variation: {audio_features['pitch']['pitch_std']} Hz"
            ),
            ParameterScore(
                name="Volume Control",
                score=audio_features["volume"]["score"],
                raw_value=audio_features["volume"]["mean_volume_db"],
                unit="dB",
                description=f"Average volume: {audio_features['volume']['mean_volume_db']} dB"
            ),
            ParameterScore(
                name="Pauses",
                score=audio_features["pauses"]["score"],
                raw_value=audio_features["pauses"]["pauses_per_minute"],
                unit="per min",
                description=f"{audio_features['pauses']['pauses_per_minute']} pauses per minute"
            ),
            ParameterScore(
                name="Filler Words",
                score=audio_features["fillers"]["score"],
                raw_value=audio_features["fillers"]["fillers_per_100_words"],
                unit="per 100 words",
                description=f"{audio_features['fillers']['fillers_per_100_words']} fillers per 100 words"
            ),
            ParameterScore(
                name="Verbal Clarity",
                score=audio_features["clarity"]["score"],
                raw_value=audio_features["clarity"]["avg_sentence_length"],
                unit="words/sentence",
                description=f"Average sentence length: {audio_features['clarity']['avg_sentence_length']} words"
            ),
            ParameterScore(
                name="Confidence Language",
                score=audio_features["confidence"]["score"],
                raw_value=audio_features["confidence"]["confidence_ratio"],
                unit="ratio",
                description=f"Confidence ratio: {audio_features['confidence']['confidence_ratio']}"
            )
        ]
        
        # Appearance & Nonverbal parameters
        appearance_params = [
            ParameterScore(
                name="Posture",
                score=video_features["posture"]["score"],
                raw_value=video_features["posture"]["upright_ratio"],
                unit="ratio",
                description=f"Upright posture: {video_features['posture']['upright_ratio']*100}% of time"
            ),
            ParameterScore(
                name="Body Expansiveness",
                score=video_features["expansiveness"]["score"],
                raw_value=video_features["expansiveness"]["avg_expansiveness"],
                unit="ratio",
                description=f"Body width ratio: {video_features['expansiveness']['avg_expansiveness']}"
            ),
            ParameterScore(
                name="Eye Contact",
                score=video_features["eye_contact"]["score"],
                raw_value=video_features["eye_contact"]["eye_contact_ratio"],
                unit="ratio",
                description=f"Eye contact: {video_features['eye_contact']['eye_contact_ratio']*100}% of time"
            ),
            ParameterScore(
                name="Facial Expressions",
                score=video_features["expressions"]["score"],
                raw_value=video_features["expressions"]["positive_expression_ratio"],
                unit="ratio",
                description=f"Positive expressions: {video_features['expressions']['positive_expression_ratio']*100}%"
            ),
            ParameterScore(
                name="Gestures",
                score=video_features["gestures"]["score"],
                raw_value=video_features["gestures"]["avg_gesture_amplitude"],
                unit="amplitude",
                description=f"Gesture amplitude: {video_features['gestures']['avg_gesture_amplitude']}"
            ),
            ParameterScore(
                name="First Impression",
                score=video_features["first_impression"]["score"],
                raw_value=video_features["first_impression"]["score"],
                unit="score",
                description="First 10 seconds composite score"
            )
        ]
        
        # Storytelling parameters
        if nlp_features["has_story"]:
            storytelling_params = [
                ParameterScore(
                    name="Narrative Structure",
                    score=nlp_features["narrative_structure"]["score"],
                    raw_value=1 if nlp_features["narrative_structure"]["structure_complete"] else 0,
                    unit="complete",
                    description="Beginning-middle-end structure"
                ),
                ParameterScore(
                    name="Cognitive Ease",
                    score=nlp_features["cognitive_ease"]["score"],
                    raw_value=nlp_features["cognitive_ease"]["flesch_score"],
                    unit="Flesch score",
                    description=f"Readability: {nlp_features['cognitive_ease']['flesch_score']}"
                ),
                ParameterScore(
                    name="Self-Disclosure",
                    score=nlp_features["self_disclosure"]["score"],
                    raw_value=nlp_features["self_disclosure"]["first_person_ratio"],
                    unit="%",
                    description=f"Personal narrative: {nlp_features['self_disclosure']['first_person_ratio']}%"
                ),
                ParameterScore(
                    name="Memorability",
                    score=nlp_features["memorability"]["score"],
                    raw_value=nlp_features["memorability"]["specificity_ratio"],
                    unit="%",
                    description=f"Specificity: {nlp_features['memorability']['specificity_ratio']}%"
                ),
                ParameterScore(
                    name="Story Pacing",
                    score=nlp_features["story_metrics"]["score"],
                    raw_value=nlp_features["story_metrics"]["story_ratio_percent"],
                    unit="%",
                    description=f"Story length: {nlp_features['story_metrics']['story_ratio_percent']}% of video"
                ),
                ParameterScore(
                    name="Story Placement",
                    score=nlp_features["story_placement"]["score"],
                    raw_value=nlp_features["story_placement"]["position_ratio"],
                    unit="position",
                    description=f"Story position: {nlp_features['story_placement']['position_ratio']*100}% through"
                )
            ]
        else:
            storytelling_params = []
        
        return {
            "communication": communication_params,
            "appearance": appearance_params,
            "storytelling": storytelling_params
        }
    
    def calculate_bucket_scores(self, parameter_scores: Dict) -> List[BucketScore]:
        """Aggregate parameter scores into bucket scores"""
        buckets = []
        
        # Communication bucket
        comm_scores = [p.score for p in parameter_scores["communication"]]
        comm_avg = sum(comm_scores) / len(comm_scores) if comm_scores else 0
        buckets.append(BucketScore(
            name="Communication",
            score=round(comm_avg, 1),
            parameters=parameter_scores["communication"]
        ))
        
        # Appearance & Nonverbal bucket
        appear_scores = [p.score for p in parameter_scores["appearance"]]
        appear_avg = sum(appear_scores) / len(appear_scores) if appear_scores else 0
        buckets.append(BucketScore(
            name="Appearance & Nonverbal",
            score=round(appear_avg, 1),
            parameters=parameter_scores["appearance"]
        ))
        
        # Storytelling bucket
        if parameter_scores["storytelling"]:
            story_scores = [p.score for p in parameter_scores["storytelling"]]
            story_avg = sum(story_scores) / len(story_scores) if story_scores else 0
            buckets.append(BucketScore(
                name="Storytelling",
                score=round(story_avg, 1),
                parameters=parameter_scores["storytelling"]
            ))
        else:
            buckets.append(BucketScore(
                name="Storytelling",
                score=0,
                parameters=[]
            ))
        
        return buckets
    
    def calculate_overall_score(self, bucket_scores: List[BucketScore]) -> float:
        """Calculate weighted overall EP score"""
        weights = {
            "Communication": 0.40,
            "Appearance & Nonverbal": 0.35,
            "Storytelling": 0.25
        }
        
        weighted_sum = 0
        for bucket in bucket_scores:
            if bucket.name in weights:
                weighted_sum += bucket.score * weights[bucket.name]
        
        return round(weighted_sum, 1)
    
    def generate_scores(self, audio_features: Dict, video_features: Dict, nlp_features: Dict) -> Dict:
        """Main scoring pipeline"""
        # Calculate parameter scores
        parameter_scores = self.calculate_parameter_scores(audio_features, video_features, nlp_features)
        
        # Calculate bucket scores
        bucket_scores = self.calculate_bucket_scores(parameter_scores)
        
        # Calculate overall score
        overall_score = self.calculate_overall_score(bucket_scores)
        
        # Extract individual bucket scores
        comm_score = next((b.score for b in bucket_scores if b.name == "Communication"), 0)
        appear_score = next((b.score for b in bucket_scores if b.name == "Appearance & Nonverbal"), 0)
        story_score = next((b.score for b in bucket_scores if b.name == "Storytelling"), 0)
        
        return {
            "overall_score": overall_score,
            "communication_score": comm_score,
            "appearance_score": appear_score,
            "storytelling_score": story_score,
            "buckets": bucket_scores
        }
