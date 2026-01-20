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

## 시작하기

### 1. Frontend 설정

```bash
cd frontend
npm install
npm run dev
```

### 2. Backend 설정

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### 3. 환경 변수 설정

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

#### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

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
