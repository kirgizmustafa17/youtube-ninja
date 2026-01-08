"""
Download History Manager
Tracks downloaded videos to avoid re-downloading
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class HistoryManager:
    """Manages download history in JSON format"""
    
    HISTORY_FILENAME = 'history.json'
    MAX_HISTORY_SIZE = 500  # Maximum entries to keep
    
    def __init__(self, app_dir: Path = None):
        if app_dir is None:
            app_dir = Path(__file__).parent.resolve()
        self.app_dir = app_dir
        self.history_file = self.app_dir / self.HISTORY_FILENAME
        self._history = None
    
    @property
    def history(self) -> List[Dict[str, Any]]:
        """Get history list, loading from file if needed"""
        if self._history is None:
            self._history = self._load_history()
        return self._history
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load history from file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
        return []
    
    def _save_history(self) -> bool:
        """Save history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False
    
    def add_download(
        self,
        url: str,
        title: str,
        video_success: bool = False,
        audio_success: bool = False,
        video_quality: str = '1080',
        thumbnail: str = ''
    ) -> None:
        """Add a download to history"""
        entry = {
            'url': url,
            'title': title,
            'video': video_success,
            'audio': audio_success,
            'quality': video_quality,
            'thumbnail': thumbnail,
            'timestamp': datetime.now().isoformat(),
        }
        
        # Remove existing entry with same URL if exists
        self._history = [h for h in self.history if h.get('url') != url]
        
        # Add new entry at beginning
        self._history.insert(0, entry)
        
        # Trim to max size
        if len(self._history) > self.MAX_HISTORY_SIZE:
            self._history = self._history[:self.MAX_HISTORY_SIZE]
        
        self._save_history()
    
    def is_downloaded(self, url: str) -> bool:
        """Check if URL was already downloaded"""
        for entry in self.history:
            if entry.get('url') == url:
                return True
        return False
    
    def get_entry(self, url: str) -> Optional[Dict[str, Any]]:
        """Get history entry for URL"""
        for entry in self.history:
            if entry.get('url') == url:
                return entry
        return None
    
    def get_recent(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent downloads"""
        return self.history[:count]
    
    def clear_history(self) -> None:
        """Clear all history"""
        self._history = []
        self._save_history()
    
    def remove_entry(self, url: str) -> bool:
        """Remove specific entry from history"""
        original_len = len(self.history)
        self._history = [h for h in self.history if h.get('url') != url]
        if len(self._history) < original_len:
            self._save_history()
            return True
        return False


# Global instance
_history_manager = None


def get_history_manager(app_dir: Path = None) -> HistoryManager:
    """Get or create the global history manager instance"""
    global _history_manager
    if _history_manager is None:
        _history_manager = HistoryManager(app_dir)
    return _history_manager
