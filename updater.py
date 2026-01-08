"""
Auto-Update Manager for YouTube Downloader
Handles yt-dlp updates and version checking
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple
from PyQt5.QtCore import QThread, pyqtSignal


class YtDlpUpdater(QThread):
    """Thread to update yt-dlp in the background"""
    
    update_progress = pyqtSignal(str)  # Status message
    update_complete = pyqtSignal(bool, str)  # Success, message
    
    def run(self):
        """Run yt-dlp update"""
        try:
            self.update_progress.emit("yt-dlp güncelleniyor...")
            
            # Update yt-dlp using pip
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # Get new version
                version = get_ytdlp_version()
                self.update_complete.emit(True, f"yt-dlp güncellendi: {version}")
            else:
                self.update_complete.emit(False, f"Güncelleme başarısız: {result.stderr[:200]}")
                
        except subprocess.TimeoutExpired:
            self.update_complete.emit(False, "Güncelleme zaman aşımına uğradı")
        except Exception as e:
            self.update_complete.emit(False, f"Güncelleme hatası: {str(e)}")


def get_ytdlp_version() -> str:
    """Get installed yt-dlp version"""
    try:
        import yt_dlp
        return yt_dlp.version.__version__
    except:
        return "bilinmiyor"


def check_ytdlp_update() -> Tuple[bool, str, str]:
    """
    Check if yt-dlp update is available
    
    Returns:
        Tuple of (update_available, current_version, latest_version)
    """
    try:
        current = get_ytdlp_version()
        
        # Check PyPI for latest version
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'index', 'versions', 'yt-dlp'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Parse output to get latest version
            output = result.stdout
            # Format: "yt-dlp (X.Y.Z)"
            import re
            match = re.search(r'yt-dlp \(([0-9.]+)\)', output)
            if match:
                latest = match.group(1)
                update_available = current != latest
                return (update_available, current, latest)
        
        # Fallback: just return current version
        return (False, current, current)
        
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return (False, get_ytdlp_version(), "bilinmiyor")


class AppVersionManager:
    """Manages application version and update checking"""
    
    APP_VERSION = "3.9"  # Current app version
    
    @classmethod
    def get_app_version(cls) -> str:
        """Get current app version"""
        return cls.APP_VERSION
    
    @classmethod
    def get_full_version_string(cls) -> str:
        """Get full version string with yt-dlp version"""
        ytdlp_version = get_ytdlp_version()
        return f"YouTube Ninja v{cls.APP_VERSION} (yt-dlp {ytdlp_version})"
