"""
Celery 작업 정의
"""
from celery import Celery
from celery.signals import task_prerun, task_postrun
from services.youtube_processor import YouTubeProcessor
from services.pose_detector import PoseDetector
from services.posture_analyzer import PostureAnalyzer
from models.store_factory import get_store
import os

# Celery 앱 초기화
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'posture_analysis',
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Celery 설정
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1시간 제한
    task_soft_time_limit=3300,  # 55분 소프트 제한
)

@celery_app.task(name='analyze_posture', bind=True)
def analyze_posture_task(self, analysis_id: str, youtube_url: str):
    """
    자세 분석 작업을 수행합니다.
    Celery 작업으로 실행되며, 진행 상황을 데이터베이스에 저장합니다.
    """
    store = get_store()
    
    try:
        # 상태를 processing으로 변경
        store.update_analysis(analysis_id, status='processing', progress=0)
        
        # 1. YouTube 영상 다운로드
        store.update_progress(analysis_id, 10, 'processing')
        processor = YouTubeProcessor()
        video_path = processor.download_video(youtube_url, max_duration=600)
        
        # 2. 프레임 추출
        store.update_progress(analysis_id, 20, 'processing')
        frames = processor.extract_frames(video_path, fps=1.0)
        
        total_frames = len(frames)
        if total_frames == 0:
            raise ValueError("프레임을 추출할 수 없습니다")
        
        # 3. 자세 인식 및 분석
        pose_detector = PoseDetector()
        posture_analyzer = PostureAnalyzer()
        
        results = []
        scores = []
        
        for idx, frame in enumerate(frames):
            # 진행률 업데이트 (20% ~ 90%)
            progress = 20 + int((idx / total_frames) * 70)
            store.update_progress(analysis_id, progress, 'processing')
            
            # 자세 감지
            pose_result = pose_detector.detect_pose(frame)
            
            if pose_result:
                # 점수 계산
                score = posture_analyzer.calculate_score(pose_result['landmarks'])
                scores.append(score)
                
                # 관절 좌표를 JSON 직렬화 가능한 형태로 변환
                landmarks_dict = {}
                for key, value in pose_result['landmarks'].items():
                    landmarks_dict[str(key)] = {
                        'x': float(value['x']),
                        'y': float(value['y']),
                        'z': float(value['z']),
                        'visibility': float(value['visibility'])
                    }
                
                results.append({
                    'frame_number': idx,
                    'timestamp': idx,  # 초 단위 (fps=1이므로)
                    'score': float(score),
                    'landmarks': landmarks_dict
                })
        
        # 4. 통계 계산
        if scores:
            average_score = sum(scores) / len(scores)
            min_score = min(scores)
            max_score = max(scores)
        else:
            average_score = 0.0
            min_score = 0.0
            max_score = 0.0
        
        # 5. 임시 파일 정리
        processor.cleanup(video_path)
        
        # 6. 결과 저장
        store.complete_analysis(
            analysis_id=analysis_id,
            frame_data=results,
            average_score=average_score,
            min_score=min_score,
            max_score=max_score
        )
        
        return {
            'analysis_id': analysis_id,
            'status': 'completed',
            'total_frames': len(results)
        }
    
    except Exception as e:
        # 에러 처리
        error_message = str(e)
        store.fail_analysis(analysis_id, error_message)
        
        # 임시 파일 정리 시도
        try:
            if 'video_path' in locals():
                processor.cleanup(video_path)
        except:
            pass
        
        # Celery에 에러 전파
        raise
