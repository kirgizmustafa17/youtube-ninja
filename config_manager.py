"""
Config Manager for YouTube Downloader
Handles persistent settings storage in JSON format
"""

import json
from pathlib import Path
from typing import Any, Dict


# Default configuration
DEFAULT_CONFIG = {
    'download_mp3': True,
    'download_video': True,
    'video_quality': '1080',
    'audio_quality': '0',  # '0' = best
    'donate_url': 'https://buymeacoffee.com/',
    'output_video_dir': '',  # Empty = ~/Videos
    'output_audio_dir': '',  # Empty = ~/Music
    'language': 'tr',  # Default language: Turkish
}


class ConfigManager:
    """Manages application configuration with JSON file storage"""
    
    CONFIG_FILENAME = 'config.json'
    
    def __init__(self, app_dir: Path = None):
        if app_dir is None:
            app_dir = Path(__file__).parent.resolve()
        self.app_dir = app_dir
        self.config_file = self.app_dir / self.CONFIG_FILENAME
        self._config = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get current configuration, loading from file if needed"""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file, or return defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                # Merge with defaults (in case new settings were added)
                config = DEFAULT_CONFIG.copy()
                config.update(loaded)
                return config
            except Exception as e:
                print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a configuration value"""
        self.config[key] = value
        if save:
            self.save_config()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self._config = DEFAULT_CONFIG.copy()
        self.save_config()
    
    # Convenience properties
    @property
    def download_mp3(self) -> bool:
        return self.get('download_mp3', True)
    
    @download_mp3.setter
    def download_mp3(self, value: bool):
        self.set('download_mp3', value)
    
    @property
    def download_video(self) -> bool:
        return self.get('download_video', True)
    
    @download_video.setter
    def download_video(self, value: bool):
        self.set('download_video', value)
    
    @property
    def video_quality(self) -> str:
        return self.get('video_quality', '1080')
    
    @video_quality.setter
    def video_quality(self, value: str):
        self.set('video_quality', value)
    
    @property
    def audio_quality(self) -> str:
        return self.get('audio_quality', '0')
    
    @audio_quality.setter
    def audio_quality(self, value: str):
        self.set('audio_quality', value)
    
    @property
    def donate_url(self) -> str:
        return self.get('donate_url', 'https://buymeacoffee.com/')
    
    @property
    def output_video_dir(self) -> Path:
        custom = self.get('output_video_dir', '')
        if custom:
            return Path(custom)
        return Path.home() / 'Videos'
    
    @output_video_dir.setter
    def output_video_dir(self, value):
        self.set('output_video_dir', str(value) if value else '')
    
    @property
    def output_audio_dir(self) -> Path:
        custom = self.get('output_audio_dir', '')
        if custom:
            return Path(custom)
        return Path.home() / 'Music'
    
    @output_audio_dir.setter
    def output_audio_dir(self, value):
        self.set('output_audio_dir', str(value) if value else '')
    
    @property
    def language(self) -> str:
        return self.get('language', 'tr')
    
    @language.setter
    def language(self, value: str):
        self.set('language', value)
    
    @staticmethod
    def get_available_qualities() -> list:
        """Get all available video qualities"""
        return ['360', '480', '720', '1080', '1440', '2160', '4320']
    
    @staticmethod
    def get_quality_label(quality: str) -> str:
        """Get human-readable quality label"""
        labels = {
            '360': '360p (SD)',
            '480': '480p (SD)',
            '720': '720p (HD)',
            '1080': '1080p (Full HD)',
            '1440': '1440p (2K)',
            '2160': '2160p (4K)',
            '4320': '4320p (8K)',
        }
        return labels.get(quality, f'{quality}p')


# Global instance
_config_manager = None


def get_config_manager(app_dir: Path = None) -> ConfigManager:
    """Get or create the global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(app_dir)
    return _config_manager
