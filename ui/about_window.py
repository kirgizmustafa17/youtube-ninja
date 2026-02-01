"""
About Window - Application information and quick actions
"""

import platform
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QWidget, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from .styles import WINDOW_STYLE
from i18n import _


class AboutWindow(QDialog):
    """About window with app info, stats, and quick actions"""
    
    update_clicked = pyqtSignal()
    donate_clicked = pyqtSignal()
    ffmpeg_clicked = pyqtSignal()
    
    def __init__(self, app_version: str, ytdlp_version: str, 
                 download_count: int = 0, ffmpeg_installed: bool = False, parent=None):
        super().__init__(parent)
        self.app_version = app_version
        self.ytdlp_version = ytdlp_version
        self.download_count = download_count
        self.ffmpeg_installed = ffmpeg_installed
        
        self.setup_ui()
        self.setStyleSheet(WINDOW_STYLE)
    
    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(_("about.title"))
        self.setFixedSize(450, 420)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(15)
        
        # Logo - YouTube style play button
        logo_label = QLabel("▶")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ff0000, stop:1 #cc0000);
                border-radius: 40px;
                min-width: 80px; max-width: 80px;
                min-height: 80px; max-height: 80px;
                color: white; font-size: 36px;
            }
        """)
        
        logo_container = QHBoxLayout()
        logo_container.addStretch()
        logo_container.addWidget(logo_label)
        logo_container.addStretch()
        layout.addLayout(logo_container)
        
        # App name
        name_label = QLabel("YouTube Ninja")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        name_label.setStyleSheet("color: #1a1a1a;")
        layout.addWidget(name_label)
        
        layout.addSpacing(5)
        
        # Version info
        info_items = [
            (_("about.app_version"), self.app_version),
            (_("about.ytdlp_version"), self.ytdlp_version),
            (_("about.python_version"), f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
            (_("about.os"), f"Windows {platform.version()}"),
            (_("about.arch"), platform.machine()),
        ]
        
        for label, value in info_items:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #666; font-size: 12px;")
            val = QLabel(value)
            val.setStyleSheet("color: #1a1a1a; font-weight: bold; font-size: 12px;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            layout.addLayout(row)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #e0e0e0;")
        line.setFixedHeight(1)
        layout.addWidget(line)
        
        # Stats
        stats_items = [
            (_("about.total_downloads"), str(self.download_count)),
            ("FFmpeg:", _("about.installed") if self.ffmpeg_installed else _("about.not_installed")),
        ]
        
        for label, value in stats_items:
            row = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #666; font-size: 12px;")
            val = QLabel(value)
            color = "#107c10" if "✓" in value else ("#d83b01" if "✗" in value else "#1a1a1a")
            val.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            layout.addLayout(row)
        
        # Copyright
        copyright_label = QLabel(_("about.copyright"))
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #999; font-size: 10px;")
        layout.addWidget(copyright_label)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        close_btn = QPushButton(_("about.btn.close"))
        close_btn.setFixedHeight(32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0; border: 1px solid #d0d0d0;
                border-radius: 4px; padding: 0 16px; color: #333; font-size: 12px;
            }
            QPushButton:hover { background-color: #e5e5e5; }
        """)
        close_btn.clicked.connect(self.close)
        
        ffmpeg_btn = QPushButton(f"⬇️ {_('about.check_ffmpeg')}")
        ffmpeg_btn.setFixedHeight(32)
        ffmpeg_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0; border: 1px solid #d0d0d0;
                border-radius: 4px; padding: 0 12px; color: #333; font-size: 12px;
            }
            QPushButton:hover { background-color: #e5e5e5; }
        """)
        ffmpeg_btn.clicked.connect(lambda: (self.ffmpeg_clicked.emit(), self.close()))
        
        update_btn = QPushButton(_("about.btn.update"))
        update_btn.setFixedHeight(32)
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4; border: none;
                border-radius: 4px; padding: 0 12px; color: white; font-size: 12px;
            }
            QPushButton:hover { background-color: #106ebe; }
        """)
        update_btn.clicked.connect(lambda: (self.update_clicked.emit(), self.close()))
        
        donate_btn = QPushButton(_("about.btn.donate"))
        donate_btn.setFixedHeight(32)
        donate_btn.setStyleSheet("""
            QPushButton {
                background-color: #d83b01; border: none;
                border-radius: 4px; padding: 0 12px; color: white; font-size: 12px;
            }
            QPushButton:hover { background-color: #c43501; }
        """)
        donate_btn.clicked.connect(lambda: (self.donate_clicked.emit(), self.close()))
        
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ffmpeg_btn)
        btn_layout.addWidget(update_btn)
        btn_layout.addWidget(donate_btn)
        
        layout.addLayout(btn_layout)
