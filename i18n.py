"""
Internationalization (i18n) Module
Simple JSON-based translation system for cross-platform support
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class I18n:
    """Internationalization manager for the application"""
    
    # Supported languages
    LANGUAGES = {
        'tr': 'Türkçe',
        'en': 'English',
    }
    
    DEFAULT_LANGUAGE = 'tr'
    
    def __init__(self, locales_dir: Path = None):
        self.locales_dir = locales_dir or Path(__file__).parent / 'locales'
        self.current_language = self.DEFAULT_LANGUAGE
        self.translations: Dict[str, str] = {}
        self._load_translations(self.current_language)
    
    def _load_translations(self, lang: str) -> bool:
        """Load translations from JSON file"""
        locale_file = self.locales_dir / f"{lang}.json"
        
        if not locale_file.exists():
            print(f"[i18n] Locale file not found: {locale_file}")
            return False
        
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
            self.current_language = lang
            print(f"[i18n] Loaded language: {lang}")
            return True
        except Exception as e:
            print(f"[i18n] Error loading translations: {e}")
            return False
    
    def set_language(self, lang: str) -> bool:
        """Change the current language"""
        if lang not in self.LANGUAGES:
            print(f"[i18n] Unsupported language: {lang}")
            return False
        return self._load_translations(lang)
    
    def get(self, key: str, default: str = None) -> str:
        """Get a translation by key"""
        return self.translations.get(key, default or key)
    
    def __call__(self, key: str, default: str = None) -> str:
        """Shorthand for get() - allows _('key') syntax"""
        return self.get(key, default)
    
    @classmethod
    def get_available_languages(cls) -> Dict[str, str]:
        """Return dict of available languages {code: name}"""
        return cls.LANGUAGES


# Global instance
_i18n: Optional[I18n] = None


def init_i18n(lang: str = None):
    """Initialize the i18n system"""
    global _i18n
    _i18n = I18n()
    if lang:
        _i18n.set_language(lang)
    return _i18n


def get_i18n() -> I18n:
    """Get the global i18n instance"""
    global _i18n
    if _i18n is None:
        _i18n = I18n()
    return _i18n


def _(key: str, default: str = None) -> str:
    """Translation function - use as _('key')"""
    return get_i18n().get(key, default)


def set_language(lang: str) -> bool:
    """Change the current language"""
    return get_i18n().set_language(lang)
