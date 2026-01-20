"""
PostgreSQL 기반 데이터 저장소
"""
from sqlalchemy.orm import Session
from models.database import Analysis, get_db
from datetime import datetime
from typing import Optional, List, Dict
from contextlib import contextmanager

class DatabaseStore:
    """PostgreSQL 기반 저장소"""
    
    def _get_session(self) -> Session:
        """데이터베이스 세션 생성"""
        db_gen = get_db()
        return next(db_gen)
    
    def create_analysis(self, analysis_id: str, youtube_url: str) -> Dict:
        """새 분석 작업 생성"""
        db = self._get_session()
        try:
            analysis = Analysis(
                id=analysis_id,
                youtube_url=youtube_url,
                status='pending',
                progress=0,
                created_at=datetime.utcnow()
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            
            return self._analysis_to_dict(analysis)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
    def _analysis_to_dict(self, analysis: Analysis) -> Dict:
        """Analysis 객체를 딕셔너리로 변환"""
        return {
            'id': analysis.id,
            'youtube_url': analysis.youtube_url,
            'status': analysis.status,
            'progress': analysis.progress,
            'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
            'completed_at': analysis.completed_at.isoformat() if analysis.completed_at else None,
            'average_score': analysis.average_score,
            'min_score': analysis.min_score,
            'max_score': analysis.max_score,
            'frame_data': analysis.frame_data,
            'error': analysis.error_message
        }
    
    def get_analysis(self, analysis_id: str) -> Optional[Dict]:
        """분석 작업 조회"""
        db = self._get_session()
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                return None
            return self._analysis_to_dict(analysis)
        finally:
            db.close()
    
    def update_analysis(self, analysis_id: str, **kwargs) -> Optional[Dict]:
        """분석 작업 업데이트"""
        db = self._get_session()
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if not analysis:
                return None
            
            for key, value in kwargs.items():
                if hasattr(analysis, key):
                    setattr(analysis, key, value)
            
            db.commit()
            db.refresh(analysis)
            return self._analysis_to_dict(analysis)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    
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
            completed_at=datetime.utcnow(),
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
            error_message=error,
            completed_at=datetime.utcnow()
        )
    
    def get_all_analyses(self) -> List[Dict]:
        """모든 분석 작업 조회"""
        db = self._get_session()
        try:
            analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).all()
            return [self._analysis_to_dict(a) for a in analyses]
        finally:
            db.close()
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """분석 작업 삭제"""
        db = self._get_session()
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                db.delete(analysis)
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
