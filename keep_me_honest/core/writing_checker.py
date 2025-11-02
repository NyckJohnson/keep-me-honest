"""Writing quality checker for Keep Me Honest."""

import re
from typing import List, Tuple, Dict
from .readability import ReadabilityAnalyzer


class WritingIssue:
    """Represents a writing issue found in text."""
    
    def __init__(self, issue_type: str, start: int, end: int, text: str, suggestion: str = ""):
        self.issue_type = issue_type
        self.start = start
        self.end = end
        self.text = text
        self.suggestion = suggestion
    
    def __repr__(self):
        return f"WritingIssue({self.issue_type}, {self.start}-{self.end}, '{self.text}')"


class WritingChecker:
    """Analyzes text for various writing issues."""
    
    # Passive voice patterns (simplified)
    PASSIVE_PATTERNS = [
        r'\b(am|is|are|was|were|be|been|being)\s+\w+ed\b',
        r'\bby\s+\w+\s+(was|were|is|are|am|been)\b'
    ]
    
    # Weak words and filler
    WEAK_WORDS = [
        'very', 'really', 'just', 'quite', 'rather', 'somewhat',
        'a bit', 'kind of', 'sort of', 'in my opinion', 'basically',
        'literally', 'actually', 'obviously', 'clearly'
    ]
    
    # Common jargon and complex words
    JARGON = {
        'utilize': 'use',
        'leverage': 'use',
        'synergy': 'teamwork',
        'paradigm': 'model',
        'methodology': 'method',
        'facilitate': 'help',
        'implement': 'do/start',
        'optimize': 'improve',
        'strategize': 'plan',
        'incentivize': 'encourage'
    }
    
    # Often confused synonyms
    CONFUSED_SYNONYMS = {
        'affect/effect': [
            (r'\baffect\s+\w+\s+effect\b', 'Usually: "affect" (verb) = influence, "effect" (noun) = result'),
            (r'\beffect\s+\w+\s+affect\b', 'Usually: "effect" (noun) = result, "affect" (verb) = influence'),
        ],
        'its/it\'s': [
            (r'\bits\s+', 'Did you mean "it\'s" (it is)?'),
            (r'\bit\'s\s+\w+\s+\w+(?!ing)', 'Did you mean "its" (possessive)?'),
        ],
        'there/their/they\'re': [
            (r'\bthere\s+', 'Did you mean "their" or "they\'re"?'),
        ]
    }
    
    # Cinnamon words (overused words - user customizable)
    CINNAMON_WORDS = [
        'really', 'very', 'just', 'nice', 'good', 'bad', 'thing', 'stuff'
    ]
    
    def __init__(self):
        self.enabled_checks = {
            'passive_voice': True,
            'weak_words': True,
            'long_sentences': True,
            'jargon': True,
            'adjectives_adverbs': True,
            'simple_alternatives': True,
            'confused_synonyms': True,
            'repeated_words': True,
            'cinnamon_words': True
        }
        self.cinnamon_words = self.CINNAMON_WORDS.copy()
        self.readability = ReadabilityAnalyzer()
    
    def add_cinnamon_word(self, word: str):
        """Add a word to the cinnamon words list."""
        if word.lower() not in self.cinnamon_words:
            self.cinnamon_words.append(word.lower())
    
    def remove_cinnamon_word(self, word: str):
        """Remove a word from the cinnamon words list."""
        if word.lower() in self.cinnamon_words:
            self.cinnamon_words.remove(word.lower())
    
    def set_check_enabled(self, check_type: str, enabled: bool):
        """Enable or disable a specific check."""
        if check_type in self.enabled_checks:
            self.enabled_checks[check_type] = enabled
    
    def check_text(self, text: str) -> Tuple[List[WritingIssue], Dict]:
        """
        Analyze text and return issues plus readability data.
        Returns: (issues, readability_dict)
        """
        issues = []
        
        if self.enabled_checks['passive_voice']:
            issues.extend(self._check_passive_voice(text))
        
        if self.enabled_checks['weak_words']:
            issues.extend(self._check_weak_words(text))
        
        if self.enabled_checks['long_sentences']:
            issues.extend(self._check_long_sentences(text))
        
        if self.enabled_checks['jargon']:
            issues.extend(self._check_jargon(text))
        
        if self.enabled_checks['adjectives_adverbs']:
            issues.extend(self._check_adjectives_adverbs(text))
        
        if self.enabled_checks['simple_alternatives']:
            issues.extend(self._check_simple_alternatives(text))
        
        if self.enabled_checks['confused_synonyms']:
            issues.extend(self._check_confused_synonyms(text))
        
        if self.enabled_checks['repeated_words']:
            issues.extend(self._check_repeated_words(text))
        
        if self.enabled_checks['cinnamon_words']:
            issues.extend(self._check_cinnamon_words(text))
        
        # Sort by position
        issues.sort(key=lambda x: x.start)
        
        # Get readability analysis
        readability_data = self.readability.analyze(text)
        
        return issues, readability_data
    
    def get_readability_compact(self, text: str) -> str:
        """Get compact readability analysis for selected text."""
        analysis = self.readability.analyze(text)
        return self.readability.format_analysis_compact(analysis)
    
    def _check_passive_voice(self, text: str) -> List[WritingIssue]:
        """Detect passive voice constructions."""
        issues = []
        for pattern in self.PASSIVE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                issues.append(WritingIssue(
                    'passive_voice',
                    match.start(),
                    match.end(),
                    match.group(),
                    'Consider using active voice instead'
                ))
        return issues
    
    def _check_weak_words(self, text: str) -> List[WritingIssue]:
        """Detect weak filler words."""
        issues = []
        for word in self.WEAK_WORDS:
            pattern = r'\b' + re.escape(word) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                issues.append(WritingIssue(
                    'weak_words',
                    match.start(),
                    match.end(),
                    match.group(),
                    f'Remove "{word}" or replace with stronger wording'
                ))
        return issues
    
    def _check_long_sentences(self, text: str) -> List[WritingIssue]:
        """Detect sentences longer than 20 words."""
        issues = []
        sentences = re.split(r'[.!?]+', text)
        pos = 0
        
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 20:
                issues.append(WritingIssue(
                    'long_sentences',
                    pos,
                    pos + len(sentence),
                    sentence.strip(),
                    f'Sentence is {len(words)} words. Consider breaking it up.'
                ))
            pos += len(sentence) + 1
        
        return issues
    
    def _check_jargon(self, text: str) -> List[WritingIssue]:
        """Detect jargon and complex words."""
        issues = []
        for jargon_word, simple_word in self.JARGON.items():
            pattern = r'\b' + re.escape(jargon_word) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                issues.append(WritingIssue(
                    'jargon',
                    match.start(),
                    match.end(),
                    match.group(),
                    f'Use "{simple_word}" instead'
                ))
        return issues
    
    def _check_adjectives_adverbs(self, text: str) -> List[WritingIssue]:
        """Detect excessive adjectives and adverbs ending in -ly."""
        issues = []
        # Find adverbs ending in -ly
        pattern = r'\b\w+ly\b'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            if match.group().lower() not in ['only', 'family', 'really', 'daily']:
                issues.append(WritingIssue(
                    'adjectives_adverbs',
                    match.start(),
                    match.end(),
                    match.group(),
                    'Consider removing or replacing this adverb'
                ))
        return issues
    
    def _check_simple_alternatives(self, text: str) -> List[WritingIssue]:
        """Suggest simpler alternatives for common phrases."""
        alternatives = {
            'at this point in time': 'now',
            'in the event that': 'if',
            'due to the fact that': 'because',
            'in order to': 'to',
            'for the purpose of': 'to',
        }
        
        issues = []
        for phrase, simple in alternatives.items():
            pattern = r'\b' + re.escape(phrase) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                issues.append(WritingIssue(
                    'simple_alternatives',
                    match.start(),
                    match.end(),
                    match.group(),
                    f'Replace with "{simple}"'
                ))
        return issues
    
    def _check_confused_synonyms(self, text: str) -> List[WritingIssue]:
        """Detect commonly confused word pairs."""
        issues = []
        for pair, patterns in self.CONFUSED_SYNONYMS.items():
            for pattern, suggestion in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    issues.append(WritingIssue(
                        'confused_synonyms',
                        match.start(),
                        match.end(),
                        match.group(),
                        suggestion
                    ))
        return issues
    
    def _check_repeated_words(self, text: str) -> List[WritingIssue]:
        """Detect repeated words close together."""
        issues = []
        words = text.split()
        
        for i in range(len(words) - 1):
            if words[i].lower() == words[i + 1].lower():
                # Find position in original text
                pos = text.lower().find(words[i].lower())
                if pos >= 0:
                    issues.append(WritingIssue(
                        'repeated_words',
                        pos,
                        pos + len(words[i] + ' ' + words[i + 1]),
                        f'{words[i]} {words[i + 1]}',
                        'Remove the repeated word'
                    ))
        
        return issues
    
    def _check_cinnamon_words(self, text: str) -> List[WritingIssue]:
        """Detect overused 'cinnamon' words."""
        issues = []
        for word in self.cinnamon_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            count = 0
            for match in re.finditer(pattern, text, re.IGNORECASE):
                count += 1
                issues.append(WritingIssue(
                    'cinnamon_words',
                    match.start(),
                    match.end(),
                    match.group(),
                    f'Overused word (used {count} times)'
                ))
        
        return issues