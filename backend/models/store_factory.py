"""
저장소 팩토리 - 메모리 또는 데이터베이스 선택
"""
import os
from models.memory_store import memory_store, MemoryStore
from models.db_store import DatabaseStore

_store_instance = None

def get_store():
    """
    환경 변수에 따라 적절한 저장소를 반환합니다.
    - USE_MEMORY_STORE=true: 메모리 저장소
    - DATABASE_URL 설정됨: PostgreSQL 저장소
    
    싱글톤 패턴으로 인스턴스를 재사용합니다.
    """
    global _store_instance
    
    if _store_instance is not None:
        return _store_instance
    
    use_memory = os.getenv("USE_MEMORY_STORE", "false").lower() == "true"
    database_url = os.getenv("DATABASE_URL")
    
    if use_memory or not database_url:
        # 메모리 저장소 사용
        _store_instance = memory_store
    else:
        # PostgreSQL 저장소 사용
        _store_instance = DatabaseStore()
    
    return _store_instance
