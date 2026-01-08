"""
YouTube Downloader - yt-dlp wrapper module
Downloads videos with AV1/AVC support and best audio as MP3
Supports up to 8K resolution
"""

import os
import re
import yt_dlp
from pathlib import Path
from typing import Callable, Optional, Dict, Any


class YouTubeDownloader:
    """Wrapper class for yt-dlp to download YouTube videos"""
    
    YOUTUBE_URL_PATTERN = re.compile(
        r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/|music\.youtube\.com/watch\?v=)[\w-]+'
    )
    
    # Quality thresholds for codec selection
    # 1080p and below: AVC (H.264) + AAC for maximum compatibility
    # 1440p and above: AV1 + m4a (OPUS) for better quality at high resolutions
    HIGH_RES_THRESHOLD = 1440
    
    def __init__(self):
        self.home_dir = Path.home()
        self.videos_dir = self.home_dir / "Videos"
        self.music_dir = self.home_dir / "Music"
        
        # Ensure directories exist
        self.videos_dir.mkdir(exist_ok=True)
        self.music_dir.mkdir(exist_ok=True)
        
        self._cancel_requested = False
    
    @classmethod
    def is_youtube_url(cls, text: str) -> bool:
        """Check if the given text is a valid YouTube URL"""
        if not text:
            return False
        return bool(cls.YOUTUBE_URL_PATTERN.match(text.strip()))
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'youtube\.com/watch\?v=([\w-]+)',
            r'youtu\.be/([\w-]+)',
            r'youtube\.com/shorts/([\w-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch video metadata without downloading"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'thumbnail': info.get('thumbnail', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                }
        except Exception as e:
            print(f"Error fetching video info: {e}")
            return None
    
    def cancel_download(self):
        """Request cancellation of current download"""
        self._cancel_requested = True
    
    def download_video(
        self,
        url: str,
        progress_callback: Optional[Callable[[str, float, str], None]] = None,
        download_video: bool = True,
        download_audio: bool = True,
        video_quality: str = '1080',
        audio_quality: str = '0'
    ) -> Dict[str, bool]:
        """
        Download video and/or audio based on options
        
        Args:
            url: YouTube video URL
            progress_callback: Callback function(type, percent, status)
                             type: 'video' or 'audio'
                             percent: 0-100
                             status: status message
            download_video: Whether to download video
            download_audio: Whether to download audio/MP3
            video_quality: Video quality ('360', '480', '720', '1080', '1440', '2160', '4320')
            audio_quality: Audio quality ('0' = best, '1' = good)
        
        Returns:
            Dict with 'video' and 'audio' success status
        """
        self._cancel_requested = False
        results = {'video': False, 'audio': False}
        
        # Get video info for filename
        info = self.get_video_info(url)
        if not info:
            return results
        
        safe_title = self._sanitize_filename(info['title'])
        
        # Download video if enabled
        if download_video and not self._cancel_requested:
            results['video'] = self._download_video_file(
                url, safe_title, progress_callback, video_quality
            )
        
        # Download audio (MP3) if enabled
        if download_audio and not self._cancel_requested:
            results['audio'] = self._download_audio_file(
                url, safe_title, progress_callback, audio_quality
            )
        
        return results
    
    def _download_video_file(
        self,
        url: str,
        safe_title: str,
        progress_callback: Optional[Callable],
        video_quality: str = '1080'
    ) -> bool:
        """Download video in specified quality with appropriate codec"""
        
        output_path = str(self.videos_dir / f"{safe_title}.mp4")
        quality_int = int(video_quality)
        
        # Determine codec based on quality
        # High resolution (1440p+): prefer AV1 for better compression and quality
        # Lower resolution: prefer AVC (H.264) for compatibility
        if quality_int >= self.HIGH_RES_THRESHOLD:
            codec_preference = 'av01'  # AV1
            audio_codec = 'm4a'  # Better audio for high-res
            quality_label = f"{video_quality}p AV1"
        else:
            codec_preference = 'avc'  # H.264
            audio_codec = 'mp4a'  # AAC
            quality_label = f"{video_quality}p"
        
        def progress_hook(d):
            if self._cancel_requested:
                raise Exception("Download cancelled")
            
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    percent = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    speed_str = self._format_speed(speed) if speed else ''
                    if progress_callback:
                        progress_callback('video', percent, f"İndiriliyor ({quality_label})... {speed_str}")
            elif d['status'] == 'finished':
                if progress_callback:
                    progress_callback('video', 100, "Tamamlandı!")
        
        # Build format string based on quality and codec
        # For high-res: AV1 video + m4a audio, fallback to any codec
        # For low-res: AVC video + AAC audio, fallback to any codec
        if quality_int >= self.HIGH_RES_THRESHOLD:
            format_str = (
                f'bestvideo[height<={video_quality}][vcodec^=av01]+bestaudio[acodec^=opus]/'
                f'bestvideo[height<={video_quality}][vcodec^=av01]+bestaudio/'
                f'bestvideo[height<={video_quality}]+bestaudio/'
                f'best[height<={video_quality}]'
            )
        else:
            format_str = (
                f'bestvideo[height<={video_quality}][vcodec^=avc]+bestaudio[acodec^=mp4a]/'
                f'bestvideo[height<={video_quality}]+bestaudio/'
                f'best[height<={video_quality}]'
            )
        
        ydl_opts = {
            'format': format_str,
            'outtmpl': output_path,
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
            'overwrites': True,
            'writethumbnail': True,
            'postprocessors': [
                {'key': 'FFmpegMetadata'},
                {'key': 'EmbedThumbnail'},
            ],
        }
        
        try:
            if progress_callback:
                progress_callback('video', 0, "Başlatılıyor...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            if "cancelled" in str(e).lower():
                if progress_callback:
                    progress_callback('video', 0, "İptal edildi")
            else:
                print(f"Video download error: {e}")
                if progress_callback:
                    progress_callback('video', 0, f"Hata: {str(e)[:50]}")
            return False
    
    def _download_audio_file(
        self,
        url: str,
        safe_title: str,
        progress_callback: Optional[Callable],
        audio_quality: str = '0'
    ) -> bool:
        """Download best audio and convert to MP3"""
        
        output_template = str(self.music_dir / f"{safe_title}.%(ext)s")
        quality_label = "En İyi" if audio_quality == '0' else "Normal"
        
        def progress_hook(d):
            if self._cancel_requested:
                raise Exception("Download cancelled")
            
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    percent = (downloaded / total) * 100
                    speed = d.get('speed', 0)
                    speed_str = self._format_speed(speed) if speed else ''
                    if progress_callback:
                        progress_callback('audio', percent, f"İndiriliyor ({quality_label})... {speed_str}")
            elif d['status'] == 'finished':
                if progress_callback:
                    progress_callback('audio', 95, "MP3'e dönüştürülüyor...")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
            'overwrites': True,
            'writethumbnail': True,
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': audio_quality,  # '0' = best, '1' = good
                },
                {'key': 'FFmpegMetadata'},
                {
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'png',
                },
                {'key': 'EmbedThumbnail'},
            ],
            'postprocessor_args': {
                'thumbnailsconvertor': ['-vf', 'crop=in_h:in_h'],
            },
        }
        
        try:
            if progress_callback:
                progress_callback('audio', 0, "Başlatılıyor...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            if progress_callback:
                progress_callback('audio', 100, "Tamamlandı!")
            return True
        except Exception as e:
            if "cancelled" in str(e).lower():
                if progress_callback:
                    progress_callback('audio', 0, "İptal edildi")
            else:
                print(f"Audio download error: {e}")
                if progress_callback:
                    progress_callback('audio', 0, f"Hata: {str(e)[:50]}")
            return False
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Remove invalid characters from filename"""
        # Remove characters that are invalid in filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        # Limit length
        return filename[:200].strip()
    
    @staticmethod
    def _format_speed(speed: float) -> str:
        """Format download speed for display"""
        if speed is None:
            return ""
        if speed < 1024:
            return f"{speed:.0f} B/s"
        elif speed < 1024 * 1024:
            return f"{speed/1024:.1f} KB/s"
        else:
            return f"{speed/(1024*1024):.1f} MB/s"
