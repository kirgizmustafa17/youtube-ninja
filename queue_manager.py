"""
Download Queue Manager
Handles multiple download requests in sequence
"""

from collections import deque
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass


@dataclass
class QueueItem:
    """Represents a single download in the queue"""
    url: str
    video_info: Dict[str, Any]
    download_video: bool = True
    download_audio: bool = True
    video_quality: str = '1080'
    audio_quality: str = '0'
    playlist_name: str = None  # For subdirectory
    playlist_position: str = None  # e.g. "3/10"


class DownloadQueue:
    """Manages a queue of downloads to process sequentially"""
    
    def __init__(self):
        self._queue = deque()
        self._current: Optional[QueueItem] = None
        self._is_downloading = False
        self._on_next_callback: Optional[Callable[[QueueItem], None]] = None
        self._on_queue_empty_callback: Optional[Callable[[], None]] = None
    
    @property
    def is_downloading(self) -> bool:
        """Check if a download is in progress"""
        return self._is_downloading
    
    @property
    def current(self) -> Optional[QueueItem]:
        """Get current download item"""
        return self._current
    
    @property
    def pending_count(self) -> int:
        """Get number of pending downloads"""
        return len(self._queue)
    
    @property
    def total_count(self) -> int:
        """Get total count including current"""
        return len(self._queue) + (1 if self._current else 0)
    
    def set_callbacks(
        self,
        on_next: Callable[[QueueItem], None] = None,
        on_queue_empty: Callable[[], None] = None
    ):
        """Set callback functions"""
        self._on_next_callback = on_next
        self._on_queue_empty_callback = on_queue_empty
    
    def add(self, item: QueueItem) -> int:
        """
        Add item to queue
        
        Returns:
            Position in queue (0 = will be downloaded immediately)
        """
        self._queue.append(item)
        position = len(self._queue) - 1
        print(f"[DEBUG] Queue.add(): position={position}, is_downloading={self._is_downloading}, queue_len={len(self._queue)}")
        
        # Start processing if not already downloading
        if not self._is_downloading:
            print("[DEBUG] Queue.add(): calling _process_next")
            self._process_next()
        
        return position
    
    def add_url(
        self,
        url: str,
        video_info: Dict[str, Any],
        download_video: bool = True,
        download_audio: bool = True,
        video_quality: str = '1080',
        audio_quality: str = '0',
        playlist_name: str = None,
        playlist_position: str = None
    ) -> int:
        """Convenience method to add URL to queue"""
        item = QueueItem(
            url=url,
            video_info=video_info,
            download_video=download_video,
            download_audio=download_audio,
            video_quality=video_quality,
            audio_quality=audio_quality,
            playlist_name=playlist_name,
            playlist_position=playlist_position
        )
        return self.add(item)
    
    def _process_next(self):
        """Process next item in queue"""
        print(f"[DEBUG] Queue._process_next(): queue_len={len(self._queue)}, has_callback={self._on_next_callback is not None}")
        if self._queue:
            self._current = self._queue.popleft()
            self._is_downloading = True
            print(f"[DEBUG] Queue._process_next(): starting {self._current.video_info.get('title', 'Unknown')[:30]}")
            
            if self._on_next_callback:
                print("[DEBUG] Queue._process_next(): calling on_next_callback")
                self._on_next_callback(self._current)
            else:
                print("[DEBUG] Queue._process_next(): NO CALLBACK SET!")
        else:
            self._current = None
            self._is_downloading = False
            print("[DEBUG] Queue._process_next(): queue empty")
            
            if self._on_queue_empty_callback:
                self._on_queue_empty_callback()
    
    def complete_current(self):
        """Mark current download as complete and process next"""
        self._is_downloading = False
        self._current = None
        self._process_next()
    
    def cancel_current(self):
        """Cancel current download and process next"""
        self._is_downloading = False
        self._current = None
        self._process_next()
    
    def clear(self):
        """Clear all pending downloads"""
        self._queue.clear()
    
    def remove(self, url: str) -> bool:
        """Remove item from queue by URL"""
        original_len = len(self._queue)
        self._queue = deque(item for item in self._queue if item.url != url)
        return len(self._queue) < original_len
    
    def get_pending(self) -> list:
        """Get list of pending downloads"""
        return list(self._queue)
    
    def is_in_queue(self, url: str) -> bool:
        """Check if URL is in queue"""
        if self._current and self._current.url == url:
            return True
        return any(item.url == url for item in self._queue)
