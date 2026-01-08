"""
Download Window - Microsoft Store inspired download dialog
"""

import requests
from io import BytesIO
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QWidget, QFrame,
    QSizePolicy, QSpacerItem, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QThread, pyqtSlot, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont, QPainter, QBrush, QColor, QPainterPath

from .styles import WINDOW_STYLE


class ThumbnailLoader(QThread):
    """Thread to load thumbnail from URL"""
    loaded = pyqtSignal(QPixmap)
    
    def __init__(self, url: str):
        super().__init__()
        self.url = url
    
    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                self.loaded.emit(pixmap)
        except Exception as e:
            print(f"Failed to load thumbnail: {e}")


class RoundedPixmapLabel(QLabel):
    """QLabel that displays pixmap with rounded corners"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self._radius = 6
    
    def setPixmap(self, pixmap: QPixmap):
        self._pixmap = pixmap
        self.update()
    
    def paintEvent(self, event):
        if self._pixmap is None:
            super().paintEvent(event)
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Scale pixmap to fit
        scaled = self._pixmap.scaled(
            self.size(), 
            Qt.KeepAspectRatioByExpanding, 
            Qt.SmoothTransformation
        )
        
        # Center the pixmap
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        
        # Create rounded path
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self._radius, self._radius)
        painter.setClipPath(path)
        
        painter.drawPixmap(x, y, scaled)


class DownloadWindow(QDialog):
    """
    Microsoft Store inspired download window
    Shows video thumbnail, title, and dual progress bars for video/audio
    """
    
    download_cancelled = pyqtSignal()
    
    def __init__(self, video_info: dict, parent=None):
        super().__init__(parent)
        self.video_info = video_info
        self.thumbnail_loader = None
        self._is_completed = False
        self._countdown = 5
        self._countdown_timer = None
        
        self.setup_ui()
        self.setStyleSheet(WINDOW_STYLE)
        self.load_thumbnail()
    
    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("YouTube Downloader")
        self.setFixedSize(500, 320)
        # Frameless window for clean look
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Container widget
        container = QWidget()
        container.setObjectName("downloadWindow")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Content area (no title bar)
        content = self._create_content_area()
        container_layout.addWidget(content)
        
        main_layout.addWidget(container)
    
    # Mouse drag support for frameless window
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    
    def _create_content_area(self) -> QWidget:
        """Create the main content area"""
        content = QWidget()
        content.setObjectName("contentArea")
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Video info section (thumbnail + title)
        info_layout = QHBoxLayout()
        info_layout.setSpacing(16)
        
        # Thumbnail
        self.thumbnail_label = RoundedPixmapLabel()
        self.thumbnail_label.setObjectName("thumbnailLabel")
        self.thumbnail_label.setFixedSize(100, 56)
        self.thumbnail_label.setStyleSheet(
            "background-color: #f0f0f0; border-radius: 6px;"
        )
        info_layout.addWidget(self.thumbnail_label)
        
        # Title and channel
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        # Video title - full text with word wrap
        title_text = self.video_info.get('title', 'Video')
        
        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("videoTitle")
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(50)  # Allow 2-3 lines
        text_layout.addWidget(self.title_label)
        
        # Channel name
        channel = self.video_info.get('uploader', 'YouTube')
        self.channel_label = QLabel(channel)
        self.channel_label.setObjectName("channelName")
        text_layout.addWidget(self.channel_label)
        
        text_layout.addStretch()
        info_layout.addLayout(text_layout)
        
        layout.addLayout(info_layout)
        
        # Separator
        layout.addSpacing(8)
        
        # Video progress section
        video_section = QLabel("Video indiriliyor... (1080p MP4)")
        video_section.setObjectName("sectionTitle")
        layout.addWidget(video_section)
        
        self.video_status = QLabel("Hazırlanıyor...")
        self.video_status.setObjectName("statusLabel")
        layout.addWidget(self.video_status)
        
        self.video_progress = QProgressBar()
        self.video_progress.setObjectName("videoProgressBar")
        self.video_progress.setRange(0, 100)
        self.video_progress.setValue(0)
        self.video_progress.setTextVisible(False)
        self.video_progress.setFixedHeight(4)
        layout.addWidget(self.video_progress)
        
        layout.addSpacing(12)
        
        # Audio progress section
        audio_section = QLabel("Audio indiriliyor... (MP3)")
        audio_section.setObjectName("sectionTitle")
        layout.addWidget(audio_section)
        
        self.audio_status = QLabel("Bekliyor...")
        self.audio_status.setObjectName("statusLabel")
        layout.addWidget(self.audio_status)
        
        self.audio_progress = QProgressBar()
        self.audio_progress.setObjectName("audioProgressBar")
        self.audio_progress.setRange(0, 100)
        self.audio_progress.setValue(0)
        self.audio_progress.setTextVisible(False)
        self.audio_progress.setFixedHeight(4)
        layout.addWidget(self.audio_progress)
        
        layout.addStretch()
        
        # Cancel button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("İptal Et")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        return content
    
    def load_thumbnail(self):
        """Load thumbnail from URL in background"""
        thumbnail_url = self.video_info.get('thumbnail', '')
        if thumbnail_url:
            self.thumbnail_loader = ThumbnailLoader(thumbnail_url)
            self.thumbnail_loader.loaded.connect(self._on_thumbnail_loaded)
            self.thumbnail_loader.start()
    
    @pyqtSlot(QPixmap)
    def _on_thumbnail_loaded(self, pixmap: QPixmap):
        """Handle thumbnail loaded"""
        if not pixmap.isNull():
            self.thumbnail_label.setPixmap(pixmap)
    
    def _on_cancel_clicked(self):
        """Handle cancel button click"""
        if self._is_completed:
            self.accept()
        else:
            self.download_cancelled.emit()
            self.reject()
    
    @pyqtSlot(str, float, str)
    def update_progress(self, download_type: str, percent: float, status: str):
        """Update progress bar based on download type"""
        if download_type == 'video':
            self.video_progress.setValue(int(percent))
            self.video_status.setText(status)
        elif download_type == 'audio':
            self.audio_progress.setValue(int(percent))
            self.audio_status.setText(status)
        
        # Force UI update
        QApplication.processEvents()
    
    def set_completed(self, success: bool = True, video_success: bool = True, audio_success: bool = True):
        """Mark download as completed and start countdown"""
        self._is_completed = True
        if success:
            if video_success:
                self.video_status.setText("✓ Tamamlandı - ~/Videos")
                self.video_status.setStyleSheet("color: #107c10;")
            if audio_success:
                self.audio_status.setText("✓ Tamamlandı - ~/Music")
                self.audio_status.setStyleSheet("color: #107c10;")
            
            # Start countdown timer
            self._countdown = 5
            self._update_countdown_button()
            self._countdown_timer = QTimer()
            self._countdown_timer.timeout.connect(self._on_countdown_tick)
            self._countdown_timer.start(1000)
        else:
            self.cancel_button.setText("Kapat")
    
    def _update_countdown_button(self):
        """Update button text with countdown"""
        self.cancel_button.setText(f"Kapat ({self._countdown})")
    
    def _on_countdown_tick(self):
        """Handle countdown timer tick"""
        self._countdown -= 1
        if self._countdown <= 0:
            self._countdown_timer.stop()
            self.accept()
        else:
            self._update_countdown_button()
    
    def closeEvent(self, event):
        """Handle window close"""
        if self._countdown_timer:
            self._countdown_timer.stop()
        if not self._is_completed:
            self.download_cancelled.emit()
        event.accept()
