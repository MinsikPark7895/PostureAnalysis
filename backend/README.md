# Backend - Posture Analysis API

FastAPI 기반 자세 분석 백엔드 서버입니다.

## 현재 상태

✅ **메모리 기반 저장소 사용** (PostgreSQL 불필요)
- `models/memory_store.py`에서 메모리에 데이터 저장
- 서버 재시작 시 데이터는 초기화됨
- 프로덕션에서는 PostgreSQL로 교체 필요

✅ **Celery 없이 BackgroundTasks 사용**
- Redis 불필요
- FastAPI의 BackgroundTasks로 비동기 처리
- 프로덕션에서는 Celery + Redis 사용 권장

## 시작하기

### 1. 가상 환경 설정

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정 (선택사항)

`.env` 파일 생성:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
TEMP_DIR=./temp_videos
```

### 4. 서버 실행

```bash
uvicorn api.main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

## API 엔드포인트

### 분석 시작
```
POST /api/analyze
Body: { "youtube_url": "https://www.youtube.com/watch?v=..." }
```

### 분석 상태 조회
```
GET /api/analysis/{analysis_id}
```

### 분석 결과 조회
```
GET /api/analysis/{analysis_id}/result
```

### 특정 프레임 결과 조회
```
GET /api/analysis/{analysis_id}/frames/{frame_number}
```

### 모든 분석 목록
```
GET /api/analyses
```

### 분석 삭제
```
DELETE /api/analysis/{analysis_id}
```

## 주의사항

1. **임시 파일**: `temp_videos/` 디렉토리에 다운로드된 영상이 저장됩니다. 분석 완료 후 자동 삭제됩니다.

2. **메모리 저장소**: 서버 재시작 시 모든 분석 데이터가 사라집니다.

3. **MediaPipe**: GPU가 없으면 CPU로 실행되며 느릴 수 있습니다.

4. **영상 길이 제한**: 기본적으로 최대 10분(600초)까지만 분석 가능합니다.

## 프로덕션 배포 시

1. PostgreSQL로 데이터베이스 교체
2. Celery + Redis로 작업 큐 교체
3. 환경 변수 설정
4. HTTPS 설정
5. Rate Limiting 추가
