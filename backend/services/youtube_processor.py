"""
YouTube 영상 다운로드 및 프레임 추출 모듈
"""
import yt_dlp
import cv2
import numpy as np
import os
from pathlib import Path
from typing import List, Optional

class YouTubeProcessor:
    def __init__(self, temp_dir: str = "./temp_videos"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def download_video(self, youtube_url: str, max_duration: int = 600) -> str:
        """
        YouTube 영상을 다운로드합니다.
        
        Args:
            youtube_url: YouTube URL
            max_duration: 최대 영상 길이 (초)
        
        Returns:
            다운로드된 영상 파일 경로
        """
        video_id = self._extract_video_id(youtube_url)
        output_path = self.temp_dir / f"{video_id}.mp4"
        
        ydl_opts = {
            'format': 'best[height<=720]',  # 해상도 제한
            'outtmpl': str(output_path),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            duration = info.get('duration', 0)
            
            if duration > max_duration:
                raise ValueError(f"영상 길이가 {max_duration}초를 초과합니다")
        
        return str(output_path)
    
    def extract_frames(
        self,
        video_path: str,
        fps: float = 1.0,
        max_frames: Optional[int] = None
    ) -> List[np.ndarray]:
        """
        영상에서 프레임을 추출합니다.
        
        Args:
            video_path: 영상 파일 경로
            fps: 초당 추출할 프레임 수
            max_frames: 최대 프레임 수
        
        Returns:
            프레임 이미지 리스트
        """
        cap = cv2.VideoCapture(video_path)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(video_fps / fps)
        
        frames = []
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frames.append(frame)
                
                if max_frames and len(frames) >= max_frames:
                    break
            
            frame_count += 1
        
        cap.release()
        return frames
    
    def cleanup(self, video_path: str):
        """임시 영상 파일을 삭제합니다."""
        if os.path.exists(video_path):
            os.remove(video_path)
    
    def _extract_video_id(self, url: str) -> str:
        """YouTube URL에서 video ID를 추출합니다."""
        import re
        pattern = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})'
        match = re.search(pattern, url)
        return match.group(1) if match else "unknown"
