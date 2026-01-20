# Posture Analysis System

YouTube 영상에서 사람의 자세를 분석하여 스켈리톤과 자세 점수를 제공하는 시스템입니다.

## 프로젝트 구조

```
PostureAnalysis/
├── frontend/          # React 프론트엔드 (Vercel 배포)
├── backend/           # FastAPI 백엔드 (Render/Railway 배포)
└── README.md
```

## 기술 스택

### Frontend
- React + Vite
- TypeScript
- Axios (API 통신)
- YouTube IFrame API

### Backend
- Python 3.11+
- FastAPI
- MediaPipe Pose
- Celery (비동기 작업)
- PostgreSQL

## 🚀 빠른 시작

### 로컬 실행 (개발 모드 - 메모리 저장소)

가장 간단한 방법입니다. PostgreSQL과 Redis 없이 실행 가능합니다.

#### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn api.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

서버는 `http://localhost:8000`, 프론트엔드는 `http://localhost:5173`에서 실행됩니다.

### 프로덕션 모드 (PostgreSQL + Celery)

자세한 내용은 [QUICK_START.md](QUICK_START.md)를 참고하세요.

## 🌐 배포

### Render (추천)

1. **PostgreSQL 생성**: Dashboard → New → PostgreSQL
2. **Redis 생성**: Dashboard → New → Redis
3. **Web Service 생성**: 
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. **Background Worker 생성**:
   - Start: `celery -A tasks.analysis_task worker --loglevel=info`
5. **Frontend 배포**: Vercel 사용

자세한 내용은 [QUICK_START.md](QUICK_START.md)를 참고하세요.

## 배포

### Frontend (Vercel)
```bash
cd frontend
vercel deploy
```

### Backend (Render)
1. Render 대시보드에서 새 Web Service 생성
2. GitHub 레포지토리 연결
3. Root Directory: `backend`
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

## 라이선스

MIT
