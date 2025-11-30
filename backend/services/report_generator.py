import os
from typing import Dict, List
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

class ReportGenerator:
    def __init__(self):
        self.api_key = os.getenv("EMERGENT_LLM_KEY")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.openai.com/v1"
        )
    
    async def generate_report(self, scores: Dict, audio_features: Dict, video_features: Dict, nlp_features: Dict) -> str:
        """Generate human-readable coaching report using LLM"""
        
        # Build context for LLM
        context = self._build_context(scores, audio_features, video_features, nlp_features)
        
        prompt = f"""You are an executive presence coach. Generate a professional, coaching-oriented assessment report based on the following data.

{context}

INSTRUCTIONS:
1. Start with a brief summary paragraph about overall executive presence
2. Then create three sections: Communication, Appearance & Nonverbal, and Storytelling
3. For each parameter, provide:
   - What you observed (with concrete numbers)
   - One sentence of actionable coaching advice
4. Use encouraging, professional tone
5. Focus on growth opportunities, not criticism
6. Keep each parameter feedback to 2-3 sentences max
7. End with a "Key Takeaways" section

CRITICAL FORMATTING RULES:
- DO NOT use ### for bucket titles (Communication, Appearance & Nonverbal, Storytelling)
- DO NOT use * for bullet points
- DO NOT use ** for bold text
- Format bucket titles as: "COMMUNICATION (Score: X/100)" on its own line
- Format parameters as numbered points (1., 2., 3.)
- Format Key Takeaways section title as: "KEY TAKEAWAYS" on its own line

FORMAT EXAMPLE:
[Summary paragraph about overall executive presence]

COMMUNICATION (Score: X/100)

1. Speaking Rate: You spoke at X words per minute. [Coaching advice].

2. Vocal Variety: Your pitch variation was X Hz. [Coaching advice].

[Continue for all Communication parameters]

APPEARANCE & NONVERBAL (Score: X/100)

1. Posture: You maintained upright posture X% of the time. [Coaching advice].

[Continue for all parameters]

STORYTELLING (Score: X/100)

1. Story Detection: [What you found]. [Coaching advice].

[Continue for all parameters]

KEY TAKEAWAYS

Your strengths include: [list].
Focus areas for growth: [list].

Generate the report now:"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert executive presence coach providing constructive, actionable feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            report_text = response.choices[0].message.content
            return report_text
        except Exception as e:
            print(f"LLM report generation failed: {str(e)}")
            # Fallback to template-based report
            return self._generate_template_report(scores, audio_features, video_features, nlp_features)
    
    def _build_context(self, scores: Dict, audio_features: Dict, video_features: Dict, nlp_features: Dict) -> str:
        """Build context string for LLM"""
        context = f"""
OVERALL SCORE: {scores['overall_score']}/100

BUCKET SCORES:
- Communication: {scores['communication_score']}/100
- Appearance & Nonverbal: {scores['appearance_score']}/100
- Storytelling: {scores['storytelling_score']}/100

COMMUNICATION PARAMETERS:
- Speaking Rate: {audio_features['speaking_rate']['wpm']} WPM (Score: {audio_features['speaking_rate']['score']})
- Vocal Pitch: {audio_features['pitch']['mean_pitch_hz']} Hz (Score: {audio_features['pitch']['pitch_score']})
- Vocal Variety: {audio_features['pitch']['pitch_std']} Hz std (Score: {audio_features['pitch']['variety_score']})
- Volume: {audio_features['volume']['mean_volume_db']} dB (Score: {audio_features['volume']['score']})
- Pauses: {audio_features['pauses']['pauses_per_minute']} per min (Score: {audio_features['pauses']['score']})
- Fillers: {audio_features['fillers']['fillers_per_100_words']} per 100 words (Score: {audio_features['fillers']['score']})
- Clarity: Avg {audio_features['clarity']['avg_sentence_length']} words/sentence (Score: {audio_features['clarity']['score']})
- Confidence: Ratio {audio_features['confidence']['confidence_ratio']} (Score: {audio_features['confidence']['score']})

APPEARANCE & NONVERBAL PARAMETERS:
- Posture: {video_features['posture']['upright_ratio']*100}% upright (Score: {video_features['posture']['score']})
- Body Expansiveness: {video_features['expansiveness']['avg_expansiveness']} (Score: {video_features['expansiveness']['score']})
- Eye Contact: {video_features['eye_contact']['eye_contact_ratio']*100}% (Score: {video_features['eye_contact']['score']})
- Facial Expressions: {video_features['expressions']['positive_expression_ratio']*100}% positive (Score: {video_features['expressions']['score']})
- Gestures: Amplitude {video_features['gestures']['avg_gesture_amplitude']} (Score: {video_features['gestures']['score']})
- First Impression: Score {video_features['first_impression']['score']}

STORYTELLING PARAMETERS:
"""
        
        if nlp_features['has_story']:
            context += f"""- Story Detected: Yes ({nlp_features['story_count']} segments)
- Narrative Structure: {'Complete' if nlp_features['narrative_structure']['structure_complete'] else 'Incomplete'} (Score: {nlp_features['narrative_structure']['score']})
- Cognitive Ease: Flesch {nlp_features['cognitive_ease']['flesch_score']} (Score: {nlp_features['cognitive_ease']['score']})
- Self-Disclosure: {nlp_features['self_disclosure']['first_person_ratio']}% first-person (Score: {nlp_features['self_disclosure']['score']})
- Memorability: {nlp_features['memorability']['specificity_ratio']}% specific details (Score: {nlp_features['memorability']['score']})
- Story Pacing: {nlp_features['story_metrics']['story_ratio_percent']}% of video (Score: {nlp_features['story_metrics']['score']})
- Story Placement: {nlp_features['story_placement']['position_ratio']*100}% through video (Score: {nlp_features['story_placement']['score']})
"""
        else:
            context += "- Story Detected: No clear story segment found\n"
        
        return context
    
    def _generate_template_report(self, scores: Dict, audio_features: Dict, video_features: Dict, nlp_features: Dict) -> str:
        """Fallback template-based report"""
        report = f"""Your overall executive presence score is {scores['overall_score']}/100. This assessment analyzes your communication style, nonverbal behavior, and storytelling ability from a 3-minute video sample.

COMMUNICATION (Score: {scores['communication_score']}/100)

1. Speaking Rate: You spoke at {audio_features['speaking_rate']['wpm']} words per minute. {"This is within the ideal range for business communication." if 130 <= audio_features['speaking_rate']['wpm'] <= 170 else "Consider adjusting your pace to 140-160 WPM for optimal clarity and engagement."}

2. Vocal Variety: Your pitch variation was {audio_features['pitch']['pitch_std']} Hz. {"Good vocal variety keeps your audience engaged." if audio_features['pitch']['variety_score'] >= 75 else "Try varying your pitch more to emphasize key points and maintain interest."}

3. Pauses: You used {audio_features['pauses']['pauses_per_minute']} pauses per minute. {"Strategic pauses help your message land." if audio_features['pauses']['score'] >= 75 else "Add more short pauses after important statements to let your audience absorb your message."}

4. Filler Words: You used {audio_features['fillers']['fillers_per_100_words']} filler words per 100 words. {"Minimal fillers project confidence." if audio_features['fillers']['score'] >= 80 else "Work on reducing 'um,' 'uh,' and 'like' to sound more polished and confident."}

APPEARANCE & NONVERBAL (Score: {scores['appearance_score']}/100)

1. Posture: You maintained upright posture {video_features['posture']['upright_ratio']*100:.0f}% of the time. {"Strong posture projects confidence and authority." if video_features['posture']['score'] >= 75 else "Focus on keeping your shoulders back and spine straight to command more presence."}

2. Eye Contact: You maintained camera eye contact {video_features['eye_contact']['eye_contact_ratio']*100:.0f}% of the time. {"Good eye contact builds trust." if video_features['eye_contact']['score'] >= 75 else "Aim for 60-80% eye contact with the camera to create stronger connection with your audience."}

3. Gestures: {"Your hand gestures were well-balanced and purposeful." if video_features['gestures']['score'] >= 75 else "Use more deliberate hand gestures to emphasize key points and add dynamism to your delivery."}

4. First Impression: Your first 10 seconds scored {video_features['first_impression']['score']}/100. The opening moments are critical - lead with strong posture, eye contact, and a confident tone.

STORYTELLING (Score: {scores['storytelling_score']}/100)

"""
        
        if nlp_features['has_story']:
            report += f"""1. Story Detection: You included {nlp_features['story_count']} story segment(s) in your video. {"Your story had a clear beginning, middle, and end structure." if nlp_features['narrative_structure']['structure_complete'] else "Strengthen your story with a clear setup, challenge, and resolution."} Stories make your message memorable and help your audience connect emotionally with your leadership.

2. Story Specificity: {"Great use of specific details and concrete examples." if nlp_features['memorability']['score'] >= 75 else "Add more specific names, dates, and concrete details to make your stories more vivid and memorable."}

3. Personal Connection: {"You effectively shared personal learning and reflection." if nlp_features['self_disclosure']['score'] >= 75 else "Share more about what you learned and how the experience shaped you to create deeper connection."}
"""
        else:
            report += """1. Story Detection: No clear story was detected in this video. Consider adding a brief personal or professional story to illustrate your points. Stories are powerful tools for executive presence - they make you memorable, build emotional connection, and demonstrate your experience and learning.
"""
        
        report += f"""

KEY TAKEAWAYS

Your strengths include: """
        
        # Identify top 3 scores
        all_scores = [
            ("Speaking Rate", audio_features['speaking_rate']['score']),
            ("Vocal Variety", audio_features['pitch']['variety_score']),
            ("Posture", video_features['posture']['score']),
            ("Eye Contact", video_features['eye_contact']['score'])
        ]
        top_strengths = sorted(all_scores, key=lambda x: x[1], reverse=True)[:3]
        report += ", ".join([s[0] for s in top_strengths]) + ".\n\n"
        
        report += "Focus areas for growth: Work on reducing filler words, maintaining consistent eye contact, and incorporating compelling stories into your communication."
        
        return report
