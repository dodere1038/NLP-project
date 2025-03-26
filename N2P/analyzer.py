from collections import Counter
from typing import Dict, List

class FrequencyAnalyzer:
    """Analyzes word frequencies"""
    def __init__(self):
        self.counter = Counter()
    
    def word_freq(self, tokens: List[str]) -> Dict[str, int]:
        self.counter.update(tokens)
        return dict(self.counter)