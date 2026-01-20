"""
Celery 작업 정의
"""
from celery import Celery
from services.youtube_processor import YouTubeProcessor
from services.pose_detector import PoseDetector
from services.posture_analyzer import PostureAnalyzer
import os

# Celery 앱 초기화
celery_app = Celery(
    'posture_analysis',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

@celery_app.task(name='analyze_posture')
def analyze_posture_task(analysis_id: str, youtube_url: str):
    """
    자세 분석 작업을 수행합니다.
    """
    try:
        # 1. YouTube 영상 다운로드
        processor = YouTubeProcessor()
        video_path = processor.download_video(youtube_url)
        
        # 2. 프레임 추출
        frames = processor.extract_frames(video_path, fps=1.0)
        
        # 3. 자세 인식 및 분석
        pose_detector = PoseDetector()
        posture_analyzer = PostureAnalyzer()
        
        results = []
        for idx, frame in enumerate(frames):
            # 자세 감지
            pose_result = pose_detector.detect_pose(frame)
            
            if pose_result:
                # 점수 계산
                score = posture_analyzer.calculate_score(pose_result['landmarks'])
                
                results.append({
                    'frame_number': idx,
                    'score': score,
                    'landmarks': pose_result['landmarks']
                })
        
        # 4. 임시 파일 정리
        processor.cleanup(video_path)
        
        # 5. 결과 반환 (실제로는 DB에 저장)
        return {
            'analysis_id': analysis_id,
            'status': 'completed',
            'results': results,
            'total_frames': len(results)
        }
    
    except Exception as e:
        return {
            'analysis_id': analysis_id,
            'status': 'error',
            'error': str(e)
        }
