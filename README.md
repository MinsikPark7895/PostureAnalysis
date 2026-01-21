# Posture Analysis System

YouTube 영상에서 사람의 자세를 분석하여 스켈리톤과 자세 점수를 제공하는 시스템입니다.

## 📋 주요 기능

### ✅ 구현된 기능

1. **YouTube 영상 분석**
   - YouTube URL 입력으로 영상 분석 시작
   - 영상 다운로드 및 프레임 추출
   - MediaPipe를 사용한 실시간 자세 인식

2. **자세 점수 계산**
   - 어깨 정렬도, 척추 정렬도, 무릎 각도, 목 각도 종합 평가
   - 0-100점 척도로 점수 제공
   - 프레임별 점수 및 통계 제공

3. **시각화**
   - **시간에 따른 점수 그래프**: Recharts를 사용한 인터랙티브 그래프
   - **스켈리톤 프레임 표시**: 각 프레임에 스켈리톤이 그려진 이미지 표시
   - **자동 재생**: 영상처럼 프레임을 자동으로 재생
   - **프레임 탐색**: 슬라이더, 그래프 클릭, 버튼으로 프레임 이동

4. **비동기 처리**
   - Celery + Redis를 사용한 작업 큐 (프로덕션)
   - BackgroundTasks를 사용한 간단한 처리 (개발)
   - 실시간 진행률 표시

5. **데이터 저장**
   - PostgreSQL을 사용한 영구 저장 (프로덕션)
   - 메모리 저장소를 사용한 임시 저장 (개발)

## 🛠 기술 스택

### Frontend
- **React 18** + **Vite** - 빠른 개발 환경
- **TypeScript** - 타입 안정성
- **Recharts** - 점수 그래프 시각화
- **Axios** - API 통신
- **YouTube IFrame API** - 영상 표시

### Backend
- **Python 3.11+** - 백엔드 언어
- **FastAPI** - 고성능 웹 프레임워크
- **MediaPipe Pose** - 자세 인식 AI 모델
- **Celery** - 비동기 작업 큐
- **PostgreSQL** - 데이터베이스 (프로덕션)
- **Redis** - 작업 큐 브로커
- **yt-dlp** - YouTube 영상 다운로드
- **OpenCV** - 영상 처리

## 📁 프로젝트 구조

```
PostureAnalysis/
├── frontend/                    # React 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   │   ├── VideoPlayer.tsx      # YouTube 영상 플레이어
│   │   │   └── PostureAnalysis.tsx  # 분석 결과 표시 (그래프, 재생 컨트롤)
│   │   ├── services/
│   │   │   └── api.ts               # API 클라이언트
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                      # FastAPI 백엔드
│   ├── api/
│   │   ├── main.py                 # FastAPI 앱 진입점
│   │   └── routes/
│   │       ├── analysis.py         # 분석 API 라우트
│   │       └── health.py           # 헬스 체크
│   ├── services/
│   │   ├── youtube_processor.py   # YouTube 영상 처리
│   │   ├── pose_detector.py        # MediaPipe 자세 인식
│   │   ├── posture_analyzer.py     # 자세 점수 계산
│   │   └── analysis_processor.py  # 분석 파이프라인
│   ├── models/
│   │   ├── database.py             # PostgreSQL 모델
│   │   ├── memory_store.py         # 메모리 저장소
│   │   ├── db_store.py              # PostgreSQL 저장소
│   │   └── store_factory.py        # 저장소 팩토리
│   ├── tasks/
│   │   └── analysis_task.py        # Celery 작업 정의
│   ├── requirements.txt
│   └── Dockerfile
│
├── QUICK_START.md                 # 빠른 시작 가이드
├── DEPLOYMENT_GUIDE.md            # 배포 가이드
├── SECURITY.md                    # 보안 가이드
└── README.md                      # 이 파일
```

## 🚀 빠른 시작

### 방법 1: 메모리 저장소 사용 (가장 간단)

PostgreSQL과 Redis 없이 실행 가능합니다.

#### 1. Backend 실행

```bash
cd backend

# 가상 환경 생성 (처음 한 번만)
python -m venv venv

# 가상 환경 활성화
# Windows CMD:
venv\Scripts\activate.bat
# Windows PowerShell (오류 시):
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn api.main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

#### 2. Frontend 실행 (새 터미널)

```bash
cd frontend

# 의존성 설치 (처음 한 번만)
npm install

# 개발 서버 실행
npm run dev
```

프론트엔드는 `http://localhost:5173`에서 실행됩니다.

### 방법 2: PostgreSQL + Celery 사용 (프로덕션과 유사)

자세한 내용은 [QUICK_START.md](QUICK_START.md)를 참고하세요.

## 💻 사용 방법

### 1. 분석 시작

1. 프론트엔드에서 YouTube URL 입력
2. "분석 시작" 버튼 클릭
3. 분석 진행 상황 확인 (진행률 표시)

### 2. 결과 확인

분석이 완료되면:

1. **점수 요약**: 평균 점수, 최고/최저 점수 확인
2. **점수 그래프**: 시간에 따른 점수 변화 그래프
   - 그래프 클릭으로 특정 시점으로 이동
   - 현재 프레임 위치에 빨간 세로선 표시
3. **프레임 재생**:
   - ▶ 재생 버튼으로 자동 재생
   - 재생 속도 조절 (0.5x, 1x, 2x, 4x)
   - 슬라이더로 원하는 프레임으로 이동
   - 처음/끝 버튼으로 빠른 이동
4. **스켈리톤 프레임**: 현재 프레임의 스켈리톤 이미지 자동 표시

## 📡 API 엔드포인트

### 분석 시작
```
POST /api/analyze
Body: { "youtube_url": "https://www.youtube.com/watch?v=..." }
Response: { "analysis_id": "...", "status": "queued", "message": "..." }
```

### 분석 상태 조회
```
GET /api/analysis/{analysis_id}
Response: { "status": "processing", "progress": 50, ... }
```

### 분석 결과 조회
```
GET /api/analysis/{analysis_id}/result
Response: {
  "frames": [
    {
      "frame_number": 0,
      "timestamp": 0,
      "score": 85.2,
      "landmarks": {...},
      "image": "data:image/jpeg;base64,..."
    },
    ...
  ],
  "summary": {
    "average_score": 82.5,
    "min_score": 65.0,
    "max_score": 95.0,
    "total_frames": 60
  }
}
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

## 🌐 배포

### 배포 아키텍처

- **Frontend**: Vercel (무료 티어)
- **Backend API**: Render/Railway (무료 티어)
- **Background Worker**: Render/Railway (Celery)
- **PostgreSQL**: Render/Railway (무료 티어)
- **Redis**: Render/Railway (무료 티어)

### 배포 단계

자세한 배포 가이드는 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)를 참고하세요.

#### 간단 요약

1. **GitHub에 코드 푸시**
2. **Render에서 배포**:
   - PostgreSQL 생성
   - Redis 생성
   - Web Service 생성 (Backend API)
   - Background Worker 생성 (Celery)
3. **Vercel에서 배포**:
   - Frontend 배포
   - 환경 변수 설정 (`VITE_API_URL`)

## 🔧 주요 기능 상세

### 자세 점수 계산 알고리즘

점수는 다음 4가지 요소를 종합하여 계산됩니다:

1. **어깨 정렬도** (25점)
   - 좌우 어깨 높이 차이 측정

2. **척추 정렬도** (25점)
   - 어깨 중심점과 골반 중심점의 정렬도

3. **무릎 각도** (25점)
   - 이상적인 각도: 160-180도

4. **목 각도** (25점)
   - 고개 숙임 정도 측정

### 프레임 처리

- **프레임 추출**: 초당 1프레임 (1fps)
- **스켈리톤 그리기**: MediaPipe로 감지된 관절을 프레임 위에 그림
- **이미지 인코딩**: Base64로 인코딩하여 JSON에 포함

### 자동 재생

- `setInterval`을 사용한 프레임 자동 전환
- 재생 속도 조절 가능 (0.5x ~ 4x)
- 마지막 프레임 도달 시 자동 정지

## ⚙️ 환경 변수

### Backend

```bash
# 데이터베이스 (프로덕션)
DATABASE_URL=postgresql://user:password@host:5432/posture_analysis

# Redis (프로덕션)
REDIS_URL=redis://host:6379/0

# 설정
USE_CELERY=true              # Celery 사용 여부
USE_MEMORY_STORE=false       # 메모리 저장소 사용 여부
CREATE_TABLES=true           # 테이블 자동 생성 (첫 배포 시)
CORS_ORIGINS=http://localhost:5173,https://your-frontend.vercel.app
```

### Frontend

```bash
VITE_API_URL=http://localhost:8000  # 개발
# 또는
VITE_API_URL=https://your-api.onrender.com  # 프로덕션
```

## 🔒 보안

- ✅ 하드코딩된 비밀번호 없음
- ✅ 환경 변수로 민감 정보 관리
- ✅ `.env` 파일은 `.gitignore`에 포함
- ✅ 입력 검증 (YouTube URL)
- ✅ CORS 설정

자세한 내용은 [SECURITY.md](SECURITY.md)를 참고하세요.

## 🐛 문제 해결

### PowerShell 실행 정책 오류

```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

또는 CMD를 사용하세요.

### YouTube 403 Forbidden 에러

- yt-dlp 최신 버전으로 업데이트: `pip install -U yt-dlp`
- 다른 YouTube URL로 테스트
- 네트워크 환경 확인

### npm이 인식되지 않음

- Node.js 설치 확인: https://nodejs.org/
- 터미널 재시작

### 데이터베이스 연결 오류

- `DATABASE_URL` 환경 변수 확인
- PostgreSQL 서버 실행 확인
- `CREATE_TABLES=true` 설정 (첫 배포 시)

### Celery Worker가 작업을 받지 못함

- Redis 연결 확인
- `REDIS_URL` 환경 변수 확인
- Worker 로그 확인

## 📚 참고 문서

- [QUICK_START.md](QUICK_START.md) - 빠른 시작 가이드
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 상세 배포 가이드
- [SECURITY.md](SECURITY.md) - 보안 가이드
- [backend/PRODUCTION_SETUP.md](backend/PRODUCTION_SETUP.md) - 프로덕션 설정
- [backend/WINDOWS_SETUP.md](backend/WINDOWS_SETUP.md) - Windows 설정

## 🎯 향후 개선 사항

- [ ] Rate Limiting 추가
- [ ] 사용자 인증/인가
- [ ] 분석 결과 내보내기 (CSV, JSON)
- [ ] 더 정교한 자세 평가 알고리즘
- [ ] 실시간 웹캠 분석
- [ ] 다중 사용자 지원 강화

## 📝 라이선스

MIT

## 👥 기여

이슈 및 풀 리퀘스트를 환영합니다!
