import string
from typing import List

class TextCleaner:
    """Cleans text"""
    def __init__(self):
        self.punct_table = str.maketrans('', '', string.punctuation)
    
    def clean(self, text: str) -> str:
        return text.lower().translate(self.punct_table)