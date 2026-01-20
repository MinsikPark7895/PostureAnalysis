"""
분석 처리 서비스 (Celery 없이 동기/비동기 처리)
"""
from services.youtube_processor import YouTubeProcessor
from services.pose_detector import PoseDetector
from services.posture_analyzer import PostureAnalyzer
from models.memory_store import memory_store
import asyncio
from typing import Dict, List

class AnalysisProcessor:
    """분석 처리 클래스"""
    
    def __init__(self):
        self.processor = YouTubeProcessor()
        self.pose_detector = PoseDetector()
        self.posture_analyzer = PostureAnalyzer()
    
    async def process_analysis(self, analysis_id: str, youtube_url: str):
        """
        비동기로 분석 작업을 수행합니다.
        """
        try:
            # 상태를 processing으로 변경
            memory_store.update_analysis(analysis_id, status='processing', progress=0)
            
            # 1. YouTube 영상 다운로드
            memory_store.update_progress(analysis_id, 10, 'processing')
            video_path = await asyncio.to_thread(
                self.processor.download_video,
                youtube_url,
                600  # 최대 10분
            )
            
            # 2. 프레임 추출
            memory_store.update_progress(analysis_id, 20, 'processing')
            frames = await asyncio.to_thread(
                self.processor.extract_frames,
                video_path,
                1.0  # 초당 1프레임
            )
            
            total_frames = len(frames)
            if total_frames == 0:
                raise ValueError("프레임을 추출할 수 없습니다")
            
            # 3. 자세 인식 및 분석
            results = []
            scores = []
            
            for idx, frame in enumerate(frames):
                # 진행률 업데이트 (20% ~ 90%)
                progress = 20 + int((idx / total_frames) * 70)
                memory_store.update_progress(analysis_id, progress, 'processing')
                
                # 자세 감지
                pose_result = await asyncio.to_thread(
                    self.pose_detector.detect_pose,
                    frame
                )
                
                if pose_result:
                    # 점수 계산
                    score = self.posture_analyzer.calculate_score(
                        pose_result['landmarks']
                    )
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
            await asyncio.to_thread(self.processor.cleanup, video_path)
            
            # 6. 결과 저장
            memory_store.complete_analysis(
                analysis_id=analysis_id,
                frame_data=results,
                average_score=average_score,
                min_score=min_score,
                max_score=max_score
            )
            
        except Exception as e:
            # 에러 처리
            memory_store.fail_analysis(analysis_id, str(e))
            # 임시 파일 정리 시도
            try:
                if 'video_path' in locals():
                    await asyncio.to_thread(self.processor.cleanup, video_path)
            except:
                pass
    
    def process_analysis_sync(self, analysis_id: str, youtube_url: str):
        """
        동기 방식으로 분석 작업을 수행합니다 (테스트용)
        """
        try:
            memory_store.update_analysis(analysis_id, status='processing', progress=0)
            
            # 1. YouTube 영상 다운로드
            memory_store.update_progress(analysis_id, 10, 'processing')
            video_path = self.processor.download_video(youtube_url, 600)
            
            # 2. 프레임 추출
            memory_store.update_progress(analysis_id, 20, 'processing')
            frames = self.processor.extract_frames(video_path, fps=1.0)
            
            total_frames = len(frames)
            if total_frames == 0:
                raise ValueError("프레임을 추출할 수 없습니다")
            
            # 3. 자세 인식 및 분석
            results = []
            scores = []
            
            for idx, frame in enumerate(frames):
                progress = 20 + int((idx / total_frames) * 70)
                memory_store.update_progress(analysis_id, progress, 'processing')
                
                pose_result = self.pose_detector.detect_pose(frame)
                
                if pose_result:
                    score = self.posture_analyzer.calculate_score(
                        pose_result['landmarks']
                    )
                    scores.append(score)
                    
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
                        'timestamp': idx,
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
            self.processor.cleanup(video_path)
            
            # 6. 결과 저장
            memory_store.complete_analysis(
                analysis_id=analysis_id,
                frame_data=results,
                average_score=average_score,
                min_score=min_score,
                max_score=max_score
            )
            
        except Exception as e:
            memory_store.fail_analysis(analysis_id, str(e))
            try:
                if 'video_path' in locals():
                    self.processor.cleanup(video_path)
            except:
                pass
