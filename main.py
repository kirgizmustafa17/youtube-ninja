#!/usr/bin/env python3
"""
YouTube Clipboard Downloader
Monitors clipboard for YouTube URLs and automatically downloads them
"""

import sys
import os
import signal
import platform
import tarfile
import zipfile
import webbrowser
import requests
from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox,
    QProgressDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QDesktopServices
from PyQt5.QtCore import QUrl

from downloader import YouTubeDownloader
from ui.download_window import DownloadWindow
from config_manager import get_config_manager, ConfigManager
from logger import log_info, log_error, log_warning, log_download_start, log_download_complete, log_download_error


class FFmpegDownloader(QThread):
    """Thread to download and extract FFmpeg"""
    
    progress = pyqtSignal(int, str)  # percent, status
    finished = pyqtSignal(bool, str)  # success, message
    
    FFMPEG_URLS = {
        'Linux': 'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz',
        'Windows': 'https://github.com/yt-dlp/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
    }
    
    def __init__(self, target_dir: Path):
        super().__init__()
        self.target_dir = target_dir
        self.system = platform.system()
    
    def run(self):
        try:
            url = self.FFMPEG_URLS.get(self.system)
            if not url:
                self.finished.emit(False, f"Desteklenmeyen sistem: {self.system}")
                return
            
            self.progress.emit(0, "FFmpeg indiriliyor...")
            
            # Download file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            # Determine filename
            if self.system == 'Windows':
                archive_path = self.target_dir / 'ffmpeg.zip'
            else:
                archive_path = self.target_dir / 'ffmpeg.tar.xz'
            
            with open(archive_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 80)
                            self.progress.emit(percent, f"İndiriliyor... {downloaded // (1024*1024)} MB")
            
            self.progress.emit(80, "Arşiv çıkartılıyor...")
            
            # Extract archive
            if self.system == 'Windows':
                with zipfile.ZipFile(archive_path, 'r') as zf:
                    zf.extractall(self.target_dir)
            else:
                with tarfile.open(archive_path, 'r:xz') as tf:
                    tf.extractall(self.target_dir)
            
            self.progress.emit(90, "Dosyalar düzenleniyor...")
            
            # Find and move ffmpeg binaries to target dir
            ffmpeg_found = False
            for root, dirs, files in os.walk(self.target_dir):
                for file in files:
                    if file in ('ffmpeg', 'ffmpeg.exe', 'ffprobe', 'ffprobe.exe'):
                        src = Path(root) / file
                        dst = self.target_dir / file
                        if src != dst:
                            if dst.exists():
                                dst.unlink()
                            src.rename(dst)
                            ffmpeg_found = True
                            # Make executable on Linux
                            if self.system != 'Windows':
                                os.chmod(dst, 0o755)
            
            # Clean up
            archive_path.unlink()
            
            # Remove extracted directory
            for item in self.target_dir.iterdir():
                if item.is_dir() and item.name.startswith('ffmpeg-'):
                    import shutil
                    shutil.rmtree(item)
            
            self.progress.emit(100, "Tamamlandı!")
            self.finished.emit(True, f"FFmpeg başarıyla indirildi: {self.target_dir}")
            
        except Exception as e:
            self.finished.emit(False, f"Hata: {str(e)}")


class ClipboardMonitor(QThread):
    """Thread to monitor clipboard for YouTube URLs"""
    
    youtube_url_detected = pyqtSignal(str)
    
    def __init__(self, clipboard):
        super().__init__()
        self.clipboard = clipboard
        self.last_text = ""
        self.running = True
        self.downloader = YouTubeDownloader()
    
    def run(self):
        """Main monitoring loop"""
        while self.running:
            try:
                current_text = self.clipboard.text().strip()
                
                # Check if text changed and is a YouTube URL
                if current_text and current_text != self.last_text:
                    if self.downloader.is_youtube_url(current_text):
                        self.last_text = current_text
                        self.youtube_url_detected.emit(current_text)
                    else:
                        self.last_text = current_text
                
                self.msleep(500)  # Check every 500ms
            except Exception as e:
                print(f"Clipboard monitor error: {e}")
                self.msleep(1000)
    
    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        self.wait(2000)


class DownloadWorker(QThread):
    """Worker thread for downloading videos"""
    
    progress_update = pyqtSignal(str, float, str)
    download_complete = pyqtSignal(dict)
    
    def __init__(self, url: str, downloader: YouTubeDownloader, 
                 download_video: bool = True, download_audio: bool = True,
                 video_quality: str = '1080', audio_quality: str = '0'):
        super().__init__()
        self.url = url
        self.downloader = downloader
        self.download_video = download_video
        self.download_audio = download_audio
        self.video_quality = video_quality
        self.audio_quality = audio_quality
    
    def run(self):
        """Execute the download"""
        results = self.downloader.download_video(
            self.url,
            progress_callback=self._on_progress,
            download_video=self.download_video,
            download_audio=self.download_audio,
            video_quality=self.video_quality,
            audio_quality=self.audio_quality
        )
        self.download_complete.emit(results)
    
    def _on_progress(self, download_type: str, percent: float, status: str):
        """Emit progress update signal"""
        self.progress_update.emit(download_type, percent, status)
    
    def cancel(self):
        """Cancel the download"""
        self.downloader.cancel_download()


def create_tray_icon() -> QPixmap:
    """Create a simple tray icon"""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Red circle background (YouTube style)
    painter.setBrush(QColor("#ff0000"))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 28, 28)
    
    # White play triangle
    painter.setBrush(QColor("#ffffff"))
    points = [
        (12, 8),
        (12, 24),
        (24, 16)
    ]
    from PyQt5.QtGui import QPolygon
    from PyQt5.QtCore import QPoint
    polygon = QPolygon([QPoint(x, y) for x, y in points])
    painter.drawPolygon(polygon)
    
    painter.end()
    return pixmap


class YouTubeDownloaderApp:
    """Main application class"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setApplicationName("YouTube Clipboard Downloader")
        
        # Initialize config manager
        self.config = get_config_manager(Path(__file__).parent.resolve())
        
        self.downloader = YouTubeDownloader()
        self.current_window: Optional[DownloadWindow] = None
        self.download_worker: Optional[DownloadWorker] = None
        self.processed_urls = set()  # Track processed URLs to avoid duplicates
        
        self.setup_tray_icon()
        self.setup_clipboard_monitor()
        
        # Check for FFmpeg at startup
        self._check_ffmpeg_startup()
        
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Timer to allow signal handling
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(500)
        
        log_info("Application started")
    
    def _check_ffmpeg_startup(self):
        """Check if FFmpeg is available at startup"""
        import shutil
        app_dir = Path(__file__).parent.resolve()
        
        # Check in app directory first
        ffmpeg_local = app_dir / ('ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg')
        
        # Check in system PATH
        ffmpeg_system = shutil.which('ffmpeg')
        
        if not ffmpeg_local.exists() and not ffmpeg_system:
            # FFmpeg not found - ask user to download
            reply = QMessageBox.question(
                None,
                "FFmpeg Bulunamadı",
                "FFmpeg bulunamadı. Video işleme için FFmpeg gereklidir.\n\n"
                "FFmpeg'i şimdi indirmek ister misiniz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                # Trigger FFmpeg download after app starts
                QTimer.singleShot(1000, self._download_ffmpeg)
        else:
            log_info("FFmpeg found")
    
    def setup_tray_icon(self):
        """Setup system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setIcon(QIcon(create_tray_icon()))
        self.tray_icon.setToolTip("YouTube Downloader\nClipboard izleniyor...")
        
        # Create tray menu
        tray_menu = QMenu()
        
        status_action = QAction("📋 Clipboard izleniyor...", self.app)
        status_action.setEnabled(False)
        tray_menu.addAction(status_action)
        
        tray_menu.addSeparator()
        
        # Download options section
        options_label = QAction("🛠️ İndirme Seçenekleri:", self.app)
        options_label.setEnabled(False)
        tray_menu.addAction(options_label)
        
        # MP3 download toggle
        self.mp3_action = QAction("🎵 MP3 İndir", self.app)
        self.mp3_action.setCheckable(True)
        self.mp3_action.setChecked(self.config.download_mp3)
        self.mp3_action.triggered.connect(self._toggle_mp3)
        tray_menu.addAction(self.mp3_action)
        
        # Video download toggle
        self.video_action = QAction("📹 Video İndir", self.app)
        self.video_action.setCheckable(True)
        self.video_action.setChecked(self.config.download_video)
        self.video_action.triggered.connect(self._toggle_video)
        tray_menu.addAction(self.video_action)
        
        # Video quality submenu - all qualities available
        self.quality_menu = QMenu("🎬 Video Kalitesi", tray_menu)
        self.quality_actions = {}
        
        for quality in ConfigManager.get_available_qualities():
            label = ConfigManager.get_quality_label(quality)
            action = QAction(label, self.app)
            action.setCheckable(True)
            action.setChecked(quality == self.config.video_quality)
            action.triggered.connect(lambda checked, q=quality: self._set_quality(q))
            self.quality_actions[quality] = action
            self.quality_menu.addAction(action)
        
        tray_menu.addMenu(self.quality_menu)
        self._update_quality_menu_state()
        
        tray_menu.addSeparator()
        
        videos_action = QAction("📁 Videos klasörünü aç", self.app)
        videos_action.triggered.connect(self._open_videos_folder)
        tray_menu.addAction(videos_action)
        
        music_action = QAction("🎵 Music klasörünü aç", self.app)
        music_action.triggered.connect(self._open_music_folder)
        tray_menu.addAction(music_action)
        
        tray_menu.addSeparator()
        
        ffmpeg_action = QAction("⬇️ FFmpeg İndir", self.app)
        ffmpeg_action.triggered.connect(self._download_ffmpeg)
        tray_menu.addAction(ffmpeg_action)
        
        tray_menu.addSeparator()
        
        # Donate button
        donate_action = QAction("☕ Bağış Yap (Buy Me a Coffee)", self.app)
        donate_action.triggered.connect(self._open_donate)
        tray_menu.addAction(donate_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("❌ Çıkış", self.app)
        quit_action.triggered.connect(self.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Show notification
        self.tray_icon.showMessage(
            "YouTube Downloader",
            "Uygulama başlatıldı. Clipboard izleniyor...",
            QSystemTrayIcon.Information,
            3000
        )
    
    def _toggle_mp3(self, checked: bool):
        """Toggle MP3 download option"""
        self.config.download_mp3 = checked
        # Ensure at least one option is selected
        if not self.config.download_mp3 and not self.config.download_video:
            self.config.download_video = True
            self.video_action.setChecked(True)
        self._update_quality_menu_state()
    
    def _toggle_video(self, checked: bool):
        """Toggle video download option"""
        self.config.download_video = checked
        # Ensure at least one option is selected
        if not self.config.download_mp3 and not self.config.download_video:
            self.config.download_mp3 = True
            self.mp3_action.setChecked(True)
        self._update_quality_menu_state()
    
    def _set_quality(self, quality: str):
        """Set video quality"""
        self.config.video_quality = quality
        # Update checkmarks
        for q, action in self.quality_actions.items():
            action.setChecked(q == quality)
    
    def _update_quality_menu_state(self):
        """Enable/disable quality menu based on video download state"""
        self.quality_menu.setEnabled(self.config.download_video)
        for action in self.quality_actions.values():
            action.setEnabled(self.config.download_video)
    
    def _open_donate(self):
        """Open donate URL in browser"""
        QDesktopServices.openUrl(QUrl(self.config.donate_url))
    
    def setup_clipboard_monitor(self):
        """Setup clipboard monitoring"""
        clipboard = self.app.clipboard()
        self.monitor = ClipboardMonitor(clipboard)
        self.monitor.youtube_url_detected.connect(self._on_youtube_url_detected)
        self.monitor.start()
    
    def _on_youtube_url_detected(self, url: str):
        """Handle detected YouTube URL"""
        # Skip if already processing this URL
        if url in self.processed_urls:
            return
        
        # Skip if a download is in progress
        if self.current_window is not None and self.current_window.isVisible():
            self.tray_icon.showMessage(
                "İndirme Devam Ediyor",
                "Zaten bir indirme işlemi devam ediyor.",
                QSystemTrayIcon.Warning,
                2000
            )
            return
        
        self.processed_urls.add(url)
        
        # Get video info
        self.tray_icon.showMessage(
            "YouTube Linki Algılandı",
            "Video bilgileri alınıyor...",
            QSystemTrayIcon.Information,
            2000
        )
        
        video_info = self.downloader.get_video_info(url)
        if not video_info:
            self.tray_icon.showMessage(
                "Hata",
                "Video bilgileri alınamadı.",
                QSystemTrayIcon.Critical,
                3000
            )
            self.processed_urls.discard(url)
            return
        
        # Show download window
        self._start_download(url, video_info)
    
    def _start_download(self, url: str, video_info: dict):
        """Start the download process"""
        self.current_window = DownloadWindow(
            video_info,
            video_quality=self.config.video_quality,
            download_video=self.config.download_video,
            download_audio=self.config.download_mp3
        )
        self.current_window.download_cancelled.connect(self._on_download_cancelled)
        
        # Update window labels based on options
        if not self.config.download_video:
            self.current_window.video_status.setText("Devre dışı")
            self.current_window.video_status.setStyleSheet("color: #888888;")
        if not self.config.download_mp3:
            self.current_window.audio_status.setText("Devre dışı")
            self.current_window.audio_status.setStyleSheet("color: #888888;")
        
        # Create download worker with options
        self.download_worker = DownloadWorker(
            url, 
            self.downloader,
            download_video=self.config.download_video,
            download_audio=self.config.download_mp3,
            video_quality=self.config.video_quality,
            audio_quality=self.config.audio_quality
        )
        self.download_worker.progress_update.connect(self.current_window.update_progress)
        self.download_worker.download_complete.connect(self._on_download_complete)
        
        # Show window and start download
        self.current_window.show()
        self.download_worker.start()
    
    def _on_download_cancelled(self):
        """Handle download cancellation"""
        if self.download_worker:
            self.download_worker.cancel()
            self.download_worker.wait(3000)
        
        self.tray_icon.showMessage(
            "İndirme İptal Edildi",
            "İndirme işlemi kullanıcı tarafından iptal edildi.",
            QSystemTrayIcon.Warning,
            2000
        )
    
    def _on_download_complete(self, results: dict):
        """Handle download completion"""
        if self.current_window:
            video_success = results.get('video', False)
            audio_success = results.get('audio', False)
            success = video_success or audio_success
            
            self.current_window.set_completed(
                success, 
                video_success=video_success and self.config.download_video,
                audio_success=audio_success and self.config.download_mp3
            )
            
            if success:
                log_download_complete(
                    self.current_window.video_info.get('title', 'Unknown'),
                    video_success, audio_success
                )
                msg = "İndirme tamamlandı!\n"
                if video_success:
                    msg += "📹 Video: ~/Videos\n"
                if audio_success:
                    msg += "🎵 Audio: ~/Music"
                
                self.tray_icon.showMessage(
                    "İndirme Tamamlandı",
                    msg,
                    QSystemTrayIcon.Information,
                    3000
                )
            else:
                log_download_error(
                    self.current_window.video_info.get('title', 'Unknown'),
                    "Download failed"
                )
                self.tray_icon.showMessage(
                    "İndirme Başarısız",
                    "Video indirilemedi. Lütfen tekrar deneyin.",
                    QSystemTrayIcon.Critical,
                    3000
                )
    
    def _open_videos_folder(self):
        """Open Videos folder in file manager"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.downloader.videos_dir)))
    
    def _open_music_folder(self):
        """Open Music folder in file manager"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.downloader.music_dir)))
    
    def _download_ffmpeg(self):
        """Download FFmpeg from GitHub"""
        app_dir = Path(__file__).parent.resolve()
        
        # Check if FFmpeg already exists
        ffmpeg_path = app_dir / ('ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg')
        if ffmpeg_path.exists():
            reply = QMessageBox.question(
                None,
                "FFmpeg Mevcut",
                "FFmpeg zaten mevcut. Yeniden indirmek ister misiniz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Create progress dialog
        self.ffmpeg_progress = QProgressDialog("FFmpeg indiriliyor...", "İptal", 0, 100)
        self.ffmpeg_progress.setWindowTitle("FFmpeg İndirme")
        self.ffmpeg_progress.setWindowModality(Qt.WindowModal)
        self.ffmpeg_progress.setAutoClose(True)
        self.ffmpeg_progress.show()
        
        # Start download
        self.ffmpeg_downloader = FFmpegDownloader(app_dir)
        self.ffmpeg_downloader.progress.connect(self._on_ffmpeg_progress)
        self.ffmpeg_downloader.finished.connect(self._on_ffmpeg_finished)
        self.ffmpeg_downloader.start()
    
    def _on_ffmpeg_progress(self, percent: int, status: str):
        """Handle FFmpeg download progress"""
        if hasattr(self, 'ffmpeg_progress'):
            self.ffmpeg_progress.setValue(percent)
            self.ffmpeg_progress.setLabelText(status)
    
    def _on_ffmpeg_finished(self, success: bool, message: str):
        """Handle FFmpeg download completion"""
        if hasattr(self, 'ffmpeg_progress'):
            self.ffmpeg_progress.close()
        
        if success:
            self.tray_icon.showMessage(
                "FFmpeg İndirildi",
                message,
                QSystemTrayIcon.Information,
                3000
            )
        else:
            self.tray_icon.showMessage(
                "FFmpeg İndirme Hatası",
                message,
                QSystemTrayIcon.Critical,
                3000
            )
    
    def _signal_handler(self, signum, frame):
        """Handle system signals"""
        self.quit()
    
    def quit(self):
        """Clean shutdown"""
        # Save config before quitting
        self.config.save_config()
        
        if self.monitor:
            self.monitor.stop()
        
        if self.download_worker:
            self.download_worker.cancel()
            self.download_worker.wait(2000)
        
        if self.current_window:
            self.current_window.close()
        
        self.tray_icon.hide()
        self.app.quit()
    
    def run(self):
        """Run the application"""
        return self.app.exec_()


def main():
    """Entry point"""
    print("YouTube Clipboard Downloader başlatılıyor...")
    print("Clipboard izleniyor. YouTube linklerini kopyalayın.")
    print("Çıkmak için system tray ikonuna sağ tıklayıp 'Çıkış' seçin.")
    print("-" * 50)
    
    app = YouTubeDownloaderApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
