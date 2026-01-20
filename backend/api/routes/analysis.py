from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
import re
import os
from models.store_factory import get_store
from tasks.analysis_task import analyze_posture_task

router = APIRouter()

class AnalysisRequest(BaseModel):
    youtube_url: str

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str

def validate_youtube_url(url: str) -> bool:
    """YouTube URL 검증"""
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    return False

@router.post("/analyze", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest):
    """
    YouTube URL을 받아서 자세 분석 작업을 시작합니다.
    Celery 작업 큐에 추가합니다.
    """
    # URL 검증
    if not validate_youtube_url(request.youtube_url):
        raise HTTPException(
            status_code=400,
            detail="유효한 YouTube URL이 아닙니다"
        )
    
    # 분석 ID 생성
    analysis_id = str(uuid.uuid4())
    
    # 저장소에 분석 작업 생성
    store = get_store()
    store.create_analysis(analysis_id, request.youtube_url)
    
    # Celery 작업 큐에 추가
    redis_url = os.getenv('REDIS_URL')
    use_celery = os.getenv('USE_CELERY', 'true').lower() == 'true'
    use_memory_store = os.getenv('USE_MEMORY_STORE', 'false').lower() == 'true'
    
    # 개발 모드: 메모리 저장소 사용 시 BackgroundTasks 허용
    is_dev_mode = use_memory_store or not redis_url
    
    if use_celery and redis_url:
        try:
            # Celery 작업 시작
            task = analyze_posture_task.delay(analysis_id, request.youtube_url)
            message = f"분석 작업이 큐에 추가되었습니다 (Task ID: {task.id})"
        except Exception as e:
            # Celery 연결 실패 시
            if is_dev_mode:
                # 개발 모드: BackgroundTasks로 폴백
                from services.analysis_processor import AnalysisProcessor
                import asyncio
                processor = AnalysisProcessor()
                asyncio.create_task(processor.process_analysis(analysis_id, request.youtube_url))
                message = "분석 작업이 시작되었습니다 (개발 모드: BackgroundTasks 사용)"
            else:
                # 프로덕션: 에러 발생
                raise HTTPException(
                    status_code=503,
                    detail=f"작업 큐에 연결할 수 없습니다. Redis URL을 확인하세요: {str(e)}"
                )
    elif is_dev_mode:
        # 개발 모드: BackgroundTasks 사용
        from services.analysis_processor import AnalysisProcessor
        import asyncio
        processor = AnalysisProcessor()
        asyncio.create_task(processor.process_analysis(analysis_id, request.youtube_url))
        message = "분석 작업이 시작되었습니다 (개발 모드: BackgroundTasks 사용)"
    else:
        # 프로덕션 환경에서 Celery를 사용할 수 없는 경우
        raise HTTPException(
            status_code=503,
            detail="프로덕션 환경에서는 Celery와 Redis가 필요합니다. REDIS_URL을 설정하고 USE_CELERY=true로 설정하세요."
        )
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="queued",
        message=message
    )

@router.get("/analysis/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """
    분석 진행 상황을 조회합니다.
    """
    store = get_store()
    analysis = store.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="분석 작업을 찾을 수 없습니다"
        )
    
    response = {
        "analysis_id": analysis_id,
        "status": analysis["status"],
        "progress": analysis["progress"],
        "youtube_url": analysis["youtube_url"],
        "created_at": analysis["created_at"],
    }
    
    # 완료된 경우 점수 정보 추가
    if analysis["status"] == "completed":
        response["average_score"] = analysis["average_score"]
        response["min_score"] = analysis["min_score"]
        response["max_score"] = analysis["max_score"]
    
    # 에러 발생한 경우 에러 메시지 추가
    if analysis["status"] == "error":
        response["error"] = analysis.get("error") or analysis.get("error_message", "알 수 없는 오류")
    
    return response

@router.get("/analysis/{analysis_id}/result")
async def get_analysis_result(analysis_id: str):
    """
    분석 결과를 조회합니다.
    """
    store = get_store()
    analysis = store.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="분석 작업을 찾을 수 없습니다"
        )
    
    if analysis["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"분석이 아직 완료되지 않았습니다. 현재 상태: {analysis['status']}"
        )
    
    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "youtube_url": analysis["youtube_url"],
        "created_at": analysis["created_at"],
        "completed_at": analysis["completed_at"],
        "frames": analysis["frame_data"] or [],
        "summary": {
            "average_score": analysis["average_score"],
            "min_score": analysis["min_score"],
            "max_score": analysis["max_score"],
            "total_frames": len(analysis["frame_data"]) if analysis["frame_data"] else 0
        }
    }

@router.get("/analysis/{analysis_id}/frames/{frame_number}")
async def get_frame_result(analysis_id: str, frame_number: int):
    """
    특정 프레임의 분석 결과를 조회합니다.
    """
    store = get_store()
    analysis = store.get_analysis(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="분석 작업을 찾을 수 없습니다"
        )
    
    if analysis["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"분석이 아직 완료되지 않았습니다"
        )
    
    frame_data = analysis.get("frame_data") or []
    
    if frame_number < 0 or frame_number >= len(frame_data):
        raise HTTPException(
            status_code=404,
            detail=f"프레임 {frame_number}을 찾을 수 없습니다"
        )
    
    return frame_data[frame_number]

@router.get("/analyses")
async def list_analyses():
    """
    모든 분석 작업 목록을 조회합니다.
    """
    store = get_store()
    analyses = store.get_all_analyses()
    
    # 간단한 정보만 반환
    return [
        {
            "analysis_id": a["id"],
            "youtube_url": a["youtube_url"],
            "status": a["status"],
            "progress": a["progress"],
            "created_at": a["created_at"],
            "average_score": a.get("average_score"),
        }
        for a in analyses
    ]

@router.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """
    분석 작업을 삭제합니다.
    """
    store = get_store()
    if store.delete_analysis(analysis_id):
        return {"message": "분석 작업이 삭제되었습니다"}
    else:
        raise HTTPException(
            status_code=404,
            detail="분석 작업을 찾을 수 없습니다"
        )
