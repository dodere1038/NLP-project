import re
from typing import List, Tuple

class N2PTokenizer:
    """Tokenizes text into words"""
    def __init__(self):
        self.word_pattern = re.compile(r"\w[\w'-]*\w|\w")
    
    def word_tokenize(self, text: str) -> List[str]:
        return self.word_pattern.findall(text.lower())