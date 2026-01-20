"""
데이터베이스 모델 정의
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

Base = declarative_base()

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True)
    youtube_url = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, processing, completed, error
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # 결과 데이터
    average_score = Column(Float, nullable=True)
    min_score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    frame_data = Column(JSON, nullable=True)  # 프레임별 스켈리톤 및 점수

# 데이터베이스 연결
# 주의: 기본값은 예시일 뿐입니다. 실제 배포 시 환경 변수로 설정하세요.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/posture_analysis")
# 현재는 메모리 저장소를 사용하므로 이 엔진은 사용되지 않습니다.
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
