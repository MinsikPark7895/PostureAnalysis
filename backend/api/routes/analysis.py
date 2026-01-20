from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import uuid
import re
from models.memory_store import memory_store
from services.analysis_processor import AnalysisProcessor

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
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    YouTube URL을 받아서 자세 분석 작업을 시작합니다.
    """
    # URL 검증
    if not validate_youtube_url(request.youtube_url):
        raise HTTPException(
            status_code=400,
            detail="유효한 YouTube URL이 아닙니다"
        )
    
    # 분석 ID 생성
    analysis_id = str(uuid.uuid4())
    
    # 메모리 저장소에 분석 작업 생성
    memory_store.create_analysis(analysis_id, request.youtube_url)
    
    # 백그라운드 작업으로 분석 시작
    processor = AnalysisProcessor()
    background_tasks.add_task(
        processor.process_analysis,
        analysis_id,
        request.youtube_url
    )
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="queued",
        message="분석 작업이 시작되었습니다"
    )

@router.get("/analysis/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """
    분석 진행 상황을 조회합니다.
    """
    analysis = memory_store.get_analysis(analysis_id)
    
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
        response["error"] = analysis.get("error", "알 수 없는 오류")
    
    return response

@router.get("/analysis/{analysis_id}/result")
async def get_analysis_result(analysis_id: str):
    """
    분석 결과를 조회합니다.
    """
    analysis = memory_store.get_analysis(analysis_id)
    
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
        "frames": analysis["frame_data"],
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
    analysis = memory_store.get_analysis(analysis_id)
    
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
    
    frame_data = analysis.get("frame_data", [])
    
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
    analyses = memory_store.get_all_analyses()
    
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
    if memory_store.delete_analysis(analysis_id):
        return {"message": "분석 작업이 삭제되었습니다"}
    else:
        raise HTTPException(
            status_code=404,
            detail="분석 작업을 찾을 수 없습니다"
        )
