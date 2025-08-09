"""
Language and localization utilities
Author: Tasdid Tahsin
Email: tasdidtahsin@gmail.com
"""

import random
import os
from pathlib import Path

class LanguageManager:
    """Manages language support and motion generation"""
    
    def __init__(self):
        self.supported_languages = ['english', 'bangla']
        self.motions = {}
        self.load_motions()
    
    def load_motions(self):
        """Load motion files for different languages"""
        project_root = Path(__file__).parent.parent.parent
        
        for language in self.supported_languages:
            file_path = project_root / "data" / f"{language}.txt"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.motions[language] = [line.strip() for line in f.readlines() if line.strip()]
            else:
                self.motions[language] = []
    
    def get_random_motion(self, language='english'):
        """Get a random motion in the specified language"""
        if language not in self.motions or not self.motions[language]:
            return "No motions available for this language."
        
        return random.choice(self.motions[language])
    
    def get_available_languages(self):
        """Get list of available languages"""
        return [lang for lang in self.supported_languages if self.motions.get(lang)]
    
    def add_motion(self, language, motion):
        """Add a new motion to a language"""
        if language not in self.motions:
            self.motions[language] = []
        
        self.motions[language].append(motion)
    
    def get_motion_count(self, language):
        """Get the number of motions for a language"""
        return len(self.motions.get(language, []))

# Global language manager instance
language_manager = LanguageManager()
