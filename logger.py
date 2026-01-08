"""
Logger module for YouTube Downloader
Handles logging to file and console
"""

import logging
import os
from pathlib import Path
from datetime import datetime


def setup_logger(app_dir: Path = None) -> logging.Logger:
    """Setup and return the application logger"""
    
    if app_dir is None:
        app_dir = Path(__file__).parent.resolve()
    
    # Create logs directory
    logs_dir = app_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)
    
    # Log file with date
    log_file = logs_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
    
    # Create logger
    logger = logging.getLogger('YouTubeDownloader')
    logger.setLevel(logging.DEBUG)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # File handler - detailed logs
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    
    # Console handler - errors only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instance
_logger = None


def get_logger() -> logging.Logger:
    """Get the global logger instance"""
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


def log_info(message: str):
    """Log info message"""
    get_logger().info(message)


def log_error(message: str, exc_info: bool = False):
    """Log error message"""
    get_logger().error(message, exc_info=exc_info)


def log_warning(message: str):
    """Log warning message"""
    get_logger().warning(message)


def log_debug(message: str):
    """Log debug message"""
    get_logger().debug(message)


def log_download_start(url: str, title: str):
    """Log download start"""
    log_info(f"Download started: {title}")
    log_debug(f"URL: {url}")


def log_download_complete(title: str, video: bool, audio: bool):
    """Log download completion"""
    results = []
    if video:
        results.append("video")
    if audio:
        results.append("audio")
    log_info(f"Download complete: {title} ({', '.join(results)})")


def log_download_error(title: str, error: str):
    """Log download error"""
    log_error(f"Download failed: {title} - {error}")
