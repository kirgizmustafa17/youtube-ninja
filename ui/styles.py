"""
Modern CSS styles for YouTube Downloader
Windows 11 / Microsoft Store inspired design
"""

WINDOW_STYLE = """
QWidget {
    font-family: 'Segoe UI', 'Ubuntu', 'Noto Sans', sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #ffffff;
}

#downloadWindow {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
}

#titleBar {
    background-color: #f3f3f3;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 12px;
}

#titleLabel {
    color: #1a1a1a;
    font-size: 12px;
    font-weight: 500;
}

#closeButton {
    background-color: transparent;
    border: none;
    color: #666666;
    font-size: 16px;
    padding: 4px 8px;
    border-radius: 4px;
}

#closeButton:hover {
    background-color: #e81123;
    color: white;
}

#contentArea {
    padding: 20px;
    background-color: #ffffff;
}

#thumbnailLabel {
    border-radius: 6px;
    background-color: #f0f0f0;
}

#videoTitle {
    color: #1a1a1a;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 4px;
}

#channelName {
    color: #666666;
    font-size: 13px;
}

#sectionTitle {
    color: #1a1a1a;
    font-size: 13px;
    font-weight: 500;
    margin-top: 16px;
}

#statusLabel {
    color: #666666;
    font-size: 12px;
}

QProgressBar {
    border: none;
    background-color: #e6e6e6;
    border-radius: 2px;
    height: 4px;
    text-align: center;
}

QProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #0078d4,
        stop:1 #00a2ed
    );
    border-radius: 2px;
}

#videoProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #0078d4,
        stop:1 #00a2ed
    );
}

#audioProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #8764b8,
        stop:1 #c239b3
    );
}

#cancelButton {
    background-color: #f0f0f0;
    border: 1px solid #d0d0d0;
    border-radius: 4px;
    color: #1a1a1a;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 24px;
    min-width: 100px;
}

#cancelButton:hover {
    background-color: #e5e5e5;
    border-color: #c0c0c0;
}

#cancelButton:pressed {
    background-color: #d0d0d0;
}

#successIcon {
    color: #107c10;
    font-size: 18px;
}

#errorIcon {
    color: #d13438;
    font-size: 18px;
}

#completedLabel {
    color: #107c10;
    font-size: 14px;
    font-weight: 500;
}
"""


DARK_STYLE = """
QWidget {
    font-family: 'Segoe UI', 'Ubuntu', 'Noto Sans', sans-serif;
    font-size: 13px;
    color: #ffffff;
}

QMainWindow, QDialog {
    background-color: #1f1f1f;
}

#downloadWindow {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    border-radius: 8px;
}

#titleBar {
    background-color: #252525;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

#titleLabel {
    color: #ffffff;
}

#closeButton {
    color: #999999;
}

#closeButton:hover {
    background-color: #e81123;
    color: white;
}

#contentArea {
    background-color: #2d2d2d;
}

#thumbnailLabel {
    background-color: #3d3d3d;
}

#videoTitle {
    color: #ffffff;
}

#channelName {
    color: #999999;
}

#sectionTitle {
    color: #ffffff;
}

#statusLabel {
    color: #999999;
}

QProgressBar {
    background-color: #3d3d3d;
}

#cancelButton {
    background-color: #3d3d3d;
    border: 1px solid #4d4d4d;
    color: #ffffff;
}

#cancelButton:hover {
    background-color: #4d4d4d;
}
"""
