"""
메모리 기반 임시 저장소 (PostgreSQL 대체)
"""
from datetime import datetime
from typing import Dict, Optional, List
import threading

class MemoryStore:
    """
    메모리 기반 데이터 저장소
    프로덕션에서는 PostgreSQL로 교체 필요
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MemoryStore, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._analyses: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._initialized = True
    
    def create_analysis(self, analysis_id: str, youtube_url: str) -> Dict:
        """새 분석 작업 생성"""
        with self._lock:
            self._analyses[analysis_id] = {
                'id': analysis_id,
                'youtube_url': youtube_url,
                'status': 'pending',
                'progress': 0,
                'created_at': datetime.utcnow().isoformat(),
                'completed_at': None,
                'average_score': None,
                'min_score': None,
                'max_score': None,
                'frame_data': None,
                'error': None
            }
        return self._analyses[analysis_id]
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """분석 작업 조회"""
        with self._lock:
            return self._analyses.get(analysis_id)
    
    def update_analysis(self, analysis_id: str, **kwargs) -> Optional[Dict]:
        """분석 작업 업데이트"""
        with self._lock:
            if analysis_id not in self._analyses:
                return None
            
            for key, value in kwargs.items():
                self._analyses[analysis_id][key] = value
            
            return self._analyses[analysis_id]
    
    def update_progress(self, analysis_id: str, progress: int, status: str = 'processing'):
        """진행률 업데이트"""
        self.update_analysis(
            analysis_id,
            progress=progress,
            status=status
        )
    
    def complete_analysis(
        self,
        analysis_id: str,
        frame_data: List[Dict],
        average_score: float,
        min_score: float,
        max_score: float
    ):
        """분석 완료 처리"""
        self.update_analysis(
            analysis_id,
            status='completed',
            progress=100,
            completed_at=datetime.utcnow().isoformat(),
            frame_data=frame_data,
            average_score=average_score,
            min_score=min_score,
            max_score=max_score
        )
    
    def fail_analysis(self, analysis_id: str, error: str):
        """분석 실패 처리"""
        self.update_analysis(
            analysis_id,
            status='error',
            error=error,
            completed_at=datetime.utcnow().isoformat()
        )
    
    def get_all_analyses(self) -> List[Dict]:
        """모든 분석 작업 조회"""
        with self._lock:
            return list(self._analyses.values())
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """분석 작업 삭제"""
        with self._lock:
            if analysis_id in self._analyses:
                del self._analyses[analysis_id]
                return True
            return False

# 전역 인스턴스
memory_store = MemoryStore()
