import re
import nltk
from typing import Dict, List
import textstat

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

class NLPProcessor:
    def __init__(self):
        self.story_indicators = [
            r'\b(story|time|remember|once|when i|happened|experience|situation)\b',
            r'\b(challenge|problem|issue|faced|difficult)\b',
            r'\b(learned|realized|understood|discovered)\b'
        ]
        
        self.temporal_connectors = [
            'then', 'next', 'after', 'before', 'when', 'while',
            'during', 'finally', 'eventually', 'first', 'second'
        ]
        
        self.causal_connectors = [
            'because', 'so', 'therefore', 'thus', 'as a result',
            'consequently', 'due to', 'since', 'leading to'
        ]
    
    def detect_story_segments(self, transcript: str) -> List[Dict]:
        """Detect story segments in transcript"""
        sentences = nltk.sent_tokenize(transcript)
        
        story_segments = []
        current_segment = []
        in_story = False
        
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            
            # Check for story indicators
            has_indicator = any(re.search(pattern, sentence_lower) for pattern in self.story_indicators)
            
            if has_indicator or in_story:
                current_segment.append(sentence)
                in_story = True
                
                # Check if story ends (new topic or conclusion)
                if i < len(sentences) - 1:
                    next_sentence = sentences[i + 1].lower()
                    # End story if transition to different topic
                    if any(word in next_sentence for word in ['now', 'today', 'currently', 'in summary']):
                        story_segments.append({
                            "text": " ".join(current_segment),
                            "start_sentence": i - len(current_segment) + 1,
                            "end_sentence": i
                        })
                        current_segment = []
                        in_story = False
            else:
                if current_segment:
                    story_segments.append({
                        "text": " ".join(current_segment),
                        "start_sentence": i - len(current_segment),
                        "end_sentence": i - 1
                    })
                    current_segment = []
                in_story = False
        
        # Add last segment if exists
        if current_segment:
            story_segments.append({
                "text": " ".join(current_segment),
                "start_sentence": len(sentences) - len(current_segment),
                "end_sentence": len(sentences) - 1
            })
        
        return story_segments
    
    def analyze_narrative_structure(self, story_text: str) -> Dict:
        """Analyze beginning-middle-end structure"""
        story_lower = story_text.lower()
        
        # Look for setup phrases
        setup_markers = ['when i', 'i was', 'we were', 'situation', 'time', 'once']
        has_setup = any(marker in story_lower for marker in setup_markers)
        
        # Look for conflict/challenge
        conflict_markers = ['challenge', 'problem', 'difficult', 'issue', 'struggled', 'failed']
        has_conflict = any(marker in story_lower for marker in conflict_markers)
        
        # Look for resolution
        resolution_markers = ['so i', 'then i', 'we decided', 'result', 'learned', 'realized', 'eventually']
        has_resolution = any(marker in story_lower for marker in resolution_markers)
        
        # Score based on presence of elements
        structure_score = 0
        if has_setup:
            structure_score += 33
        if has_conflict:
            structure_score += 34
        if has_resolution:
            structure_score += 33
        
        return {
            "has_setup": has_setup,
            "has_conflict": has_conflict,
            "has_resolution": has_resolution,
            "structure_complete": has_setup and has_conflict and has_resolution,
            "score": structure_score
        }
    
    def analyze_cognitive_ease(self, story_text: str) -> Dict:
        """Analyze readability and flow"""
        # Readability score
        flesch_score = textstat.flesch_reading_ease(story_text)
        
        # Count connectors
        story_lower = story_text.lower()
        temporal_count = sum(story_lower.count(word) for word in self.temporal_connectors)
        causal_count = sum(story_lower.count(word) for word in self.causal_connectors)
        
        total_connectors = temporal_count + causal_count
        word_count = len(story_text.split())
        connector_ratio = (total_connectors / word_count * 100) if word_count > 0 else 0
        
        # Score: good readability (60-80 Flesch) + decent connectors (5-15%)
        if 60 <= flesch_score <= 80 and 5 <= connector_ratio <= 15:
            score = 100
        elif 50 <= flesch_score <= 90 and 3 <= connector_ratio <= 20:
            score = 80
        else:
            score = 60
        
        return {
            "flesch_score": round(flesch_score, 1),
            "temporal_connectors": temporal_count,
            "causal_connectors": causal_count,
            "connector_ratio": round(connector_ratio, 2),
            "score": round(score, 1)
        }
    
    def analyze_self_disclosure(self, story_text: str) -> Dict:
        """Detect personal storytelling and learning"""
        story_lower = story_text.lower()
        
        # First-person markers
        first_person_count = story_lower.count(' i ') + story_lower.count(' my ') + story_lower.count(' we ')
        
        # Learning statements
        learning_markers = ['learned', 'realized', 'understood', 'discovered', 'taught me']
        learning_count = sum(story_lower.count(marker) for marker in learning_markers)
        
        word_count = len(story_text.split())
        first_person_ratio = (first_person_count / word_count * 100) if word_count > 0 else 0
        
        # Score based on personal narrative
        if first_person_ratio >= 5 and learning_count >= 1:
            score = 100
        elif first_person_ratio >= 3 and learning_count >= 1:
            score = 85
        elif first_person_ratio >= 2:
            score = 70
        else:
            score = 50
        
        return {
            "first_person_count": first_person_count,
            "first_person_ratio": round(first_person_ratio, 2),
            "learning_statements": learning_count,
            "score": round(score, 1)
        }
    
    def analyze_memorability(self, story_text: str) -> Dict:
        """Analyze specificity and imagery"""
        # Named entity detection (simple)
        words = story_text.split()
        
        # Detect capitalized words (proper nouns)
        capitalized = sum(1 for word in words if word[0].isupper() and len(word) > 2)
        
        # Detect numbers
        numbers = sum(1 for word in words if any(char.isdigit() for char in word))
        
        # Concrete nouns (simplified - look for common concrete words)
        concrete_words = ['team', 'project', 'meeting', 'client', 'product', 'office', 'data']
        concrete_count = sum(story_text.lower().count(word) for word in concrete_words)
        
        specificity_score = capitalized + numbers + concrete_count
        word_count = len(words)
        specificity_ratio = (specificity_score / word_count * 100) if word_count > 0 else 0
        
        # Good: 10-20% specificity
        if 10 <= specificity_ratio <= 20:
            score = 100
        elif 7 <= specificity_ratio < 10 or 20 < specificity_ratio <= 25:
            score = 85
        elif 5 <= specificity_ratio < 7 or 25 < specificity_ratio <= 30:
            score = 70
        else:
            score = 60
        
        return {
            "capitalized_words": capitalized,
            "numbers_count": numbers,
            "concrete_words": concrete_count,
            "specificity_ratio": round(specificity_ratio, 2),
            "score": round(score, 1)
        }
    
    def analyze_story_metrics(self, story_text: str, total_duration: float) -> Dict:
        """Analyze story length and pacing"""
        word_count = len(story_text.split())
        
        # Estimate story duration (assuming 150 WPM)
        estimated_duration = (word_count / 150) * 60  # in seconds
        story_ratio = (estimated_duration / total_duration * 100) if total_duration > 0 else 0
        
        # Ideal: 15-30% of total time on story
        if 15 <= story_ratio <= 30:
            score = 100
        elif 10 <= story_ratio < 15 or 30 < story_ratio <= 40:
            score = 85
        elif 5 <= story_ratio < 10 or 40 < story_ratio <= 50:
            score = 70
        else:
            score = 50
        
        return {
            "word_count": word_count,
            "estimated_duration_s": round(estimated_duration, 1),
            "story_ratio_percent": round(story_ratio, 1),
            "score": round(score, 1)
        }
    
    def process_nlp(self, transcript: str, duration: float) -> Dict:
        """Main NLP processing pipeline"""
        # Detect story segments
        story_segments = self.detect_story_segments(transcript)
        
        if len(story_segments) == 0:
            return {
                "has_story": False,
                "story_count": 0,
                "narrative_structure": {"score": 0},
                "cognitive_ease": {"score": 50},
                "self_disclosure": {"score": 50},
                "memorability": {"score": 50},
                "story_metrics": {"score": 0},
                "story_placement": {"score": 50}
            }
        
        # Analyze the best story (longest segment)
        best_story = max(story_segments, key=lambda s: len(s["text"]))
        
        # Run all analyses
        narrative = self.analyze_narrative_structure(best_story["text"])
        cognitive = self.analyze_cognitive_ease(best_story["text"])
        disclosure = self.analyze_self_disclosure(best_story["text"])
        memorability = self.analyze_memorability(best_story["text"])
        metrics = self.analyze_story_metrics(best_story["text"], duration)
        
        # Analyze placement
        sentences_count = len(nltk.sent_tokenize(transcript))
        story_position = best_story["start_sentence"] / sentences_count if sentences_count > 0 else 0
        
        # Ideal: story in middle or end (30-80% through)
        if 0.3 <= story_position <= 0.8:
            placement_score = 100
        elif 0.2 <= story_position < 0.3 or 0.8 < story_position <= 0.9:
            placement_score = 80
        else:
            placement_score = 60
        
        return {
            "has_story": True,
            "story_count": len(story_segments),
            "best_story_text": best_story["text"][:200] + "...",  # Preview
            "narrative_structure": narrative,
            "cognitive_ease": cognitive,
            "self_disclosure": disclosure,
            "memorability": memorability,
            "story_metrics": metrics,
            "story_placement": {
                "position_ratio": round(story_position, 2),
                "score": round(placement_score, 1)
            }
        }
