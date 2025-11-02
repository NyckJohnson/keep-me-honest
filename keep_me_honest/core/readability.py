"""Readability analysis for Keep Me Honest."""

import re
from typing import Dict, Tuple


class ReadabilityAnalyzer:
    """Analyzes text readability and provides metrics."""
    
    # Grade levels with descriptors
    GRADE_LEVELS = {
        'Elementary': (0, 6),
        'Middle School': (6, 9),
        'High School': (9, 13),
        'College': (13, 16),
        'Graduate': (16, float('inf'))
    }
    
    def __init__(self):
        pass
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze text readability.
        Returns dict with various metrics.
        """
        if not text or len(text.strip()) == 0:
            return self._empty_analysis()
        
        sentences = self._count_sentences(text)
        words = self._count_words(text)
        syllables = self._count_syllables(text)
        characters = len(text)
        
        if sentences == 0 or words == 0:
            return self._empty_analysis()
        
        # Calculate various readability scores
        flesch_kincaid_grade = self._flesch_kincaid_grade(sentences, words, syllables)
        flesch_reading_ease = self._flesch_reading_ease(sentences, words, syllables)
        gunning_fog = self._gunning_fog_index(sentences, words, text)
        
        # Average grade
        avg_grade = (flesch_kincaid_grade + gunning_fog) / 2
        
        # Determine difficulty level
        difficulty = self._get_difficulty_level(avg_grade)
        
        # Calculate other metrics
        avg_word_length = words / len(text) * 100 if text else 0
        avg_sentence_length = words / sentences if sentences > 0 else 0
        
        return {
            'sentences': sentences,
            'words': words,
            'syllables': syllables,
            'characters': characters,
            'flesch_kincaid_grade': round(flesch_kincaid_grade, 1),
            'flesch_reading_ease': round(flesch_reading_ease, 1),
            'gunning_fog': round(gunning_fog, 1),
            'avg_grade': round(avg_grade, 1),
            'difficulty': difficulty,
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 1),
        }
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis."""
        return {
            'sentences': 0,
            'words': 0,
            'syllables': 0,
            'characters': 0,
            'flesch_kincaid_grade': 0,
            'flesch_reading_ease': 0,
            'gunning_fog': 0,
            'avg_grade': 0,
            'difficulty': 'N/A',
            'avg_word_length': 0,
            'avg_sentence_length': 0,
        }
    
    def _count_sentences(self, text: str) -> int:
        """Count sentences (simplified)."""
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def _count_words(self, text: str) -> int:
        """Count words."""
        words = text.split()
        return len(words)
    
    def _count_syllables(self, text: str) -> int:
        """
        Estimate syllable count using vowel groups.
        Simplified but reasonably accurate.
        """
        text = text.lower()
        syllable_count = 0
        vowels = 'aeiouy'
        previous_was_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if text.endswith('e'):
            syllable_count -= 1
        
        # Ensure at least 1 syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return max(1, syllable_count)
    
    def _flesch_kincaid_grade(self, sentences: int, words: int, syllables: int) -> float:
        """
        Flesch-Kincaid Grade Level Formula.
        0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        """
        if sentences == 0 or words == 0:
            return 0
        
        grade = (0.39 * (words / sentences) + 
                11.8 * (syllables / words) - 15.59)
        
        return max(0, grade)  # Don't go below 0
    
    def _flesch_reading_ease(self, sentences: int, words: int, syllables: int) -> float:
        """
        Flesch Reading Ease Score.
        206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        Scores range from 0-100:
        90-100: Very Easy, 80-89: Easy, 70-79: Fairly Easy,
        60-69: Standard, 50-59: Fairly Difficult, 30-49: Difficult,
        0-29: Very Difficult
        """
        if sentences == 0 or words == 0:
            return 0
        
        score = (206.835 - 1.015 * (words / sentences) - 
                84.6 * (syllables / words))
        
        return max(0, min(100, score))  # Clamp 0-100
    
    def _gunning_fog_index(self, sentences: int, words: int, text: str) -> float:
        """
        Gunning Fog Index.
        0.4 * ((words/sentences) + 100 * (complex_words/words))
        Complex words are those with 3+ syllables.
        """
        if sentences == 0 or words == 0:
            return 0
        
        # Count complex words (3+ syllables)
        word_list = text.split()
        complex_words = 0
        
        for word in word_list:
            if self._count_syllables(word) >= 3:
                complex_words += 1
        
        index = (0.4 * ((words / sentences) + 
                100 * (complex_words / words)))
        
        return max(0, index)
    
    def _get_difficulty_level(self, grade: float) -> str:
        """Convert grade level to difficulty description."""
        for level, (min_grade, max_grade) in self.GRADE_LEVELS.items():
            if min_grade <= grade < max_grade:
                return level
        return 'Graduate'
    
    def get_flesch_description(self, score: float) -> str:
        """Get description of Flesch Reading Ease score."""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"
    
    def format_analysis(self, analysis: Dict) -> str:
        """
        Format analysis into readable string.
        Returns a formatted summary.
        """
        if analysis['words'] == 0:
            return "No text to analyze"
        
        return (
            f"📊 READABILITY ANALYSIS\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Difficulty: {analysis['difficulty']} (Grade {analysis['avg_grade']})\n"
            f"Flesch Reading Ease: {analysis['flesch_reading_ease']}/100 "
            f"({self.get_flesch_description(analysis['flesch_reading_ease'])})\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Words: {analysis['words']} | "
            f"Sentences: {analysis['sentences']}\n"
            f"Avg. Sentence: {analysis['avg_sentence_length']} words\n"
            f"Avg. Word Length: {analysis['avg_word_length']} characters\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Flesch-Kincaid: {analysis['flesch_kincaid_grade']}\n"
            f"Gunning Fog: {analysis['gunning_fog']}"
        )
    
    def format_analysis_compact(self, analysis: Dict) -> str:
        """Format analysis into compact single-line format."""
        if analysis['words'] == 0:
            return "No text"
        
        return (
            f"{analysis['difficulty']} (Grade {analysis['avg_grade']}) | "
            f"{analysis['words']} words | "
            f"Flesch: {analysis['flesch_reading_ease']}"
        )