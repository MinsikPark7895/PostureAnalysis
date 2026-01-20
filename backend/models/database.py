"""
데이터베이스 모델 정의
"""
from sqlalchemy import create_engine, Column, String, Integer, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from datetime import datetime
from typing import Generator

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
    error_message = Column(String, nullable=True)

# 데이터베이스 연결
DATABASE_URL = os.getenv("DATABASE_URL")

# 메모리 저장소 사용 여부 확인
USE_MEMORY_STORE = os.getenv("USE_MEMORY_STORE", "false").lower() == "true"

if DATABASE_URL and not USE_MEMORY_STORE:
    # PostgreSQL 사용
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,  # 서버리스 환경에 적합
        echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 테이블 생성 (개발 환경)
    if os.getenv("CREATE_TABLES", "false").lower() == "true":
        Base.metadata.create_all(bind=engine)
else:
    # 메모리 저장소 사용 (개발 환경)
    engine = None
    SessionLocal = None

def get_db() -> Generator[Session, None, None]:
    """데이터베이스 세션 생성"""
    if not SessionLocal:
        raise RuntimeError("데이터베이스가 설정되지 않았습니다. DATABASE_URL을 설정하거나 USE_MEMORY_STORE=true로 설정하세요.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
