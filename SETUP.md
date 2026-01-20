# 프로젝트 초기 설정 가이드

## 📋 사전 요구사항

### 필수 설치
- **Node.js** 18+ 및 npm
- **Python** 3.11+
- **PostgreSQL** (로컬 또는 클라우드)
- **Redis** (로컬 또는 클라우드)

### 선택 설치
- **Docker** (컨테이너 배포 시)

## 🚀 초기 설정

### 1. Frontend 설정

```bash
# frontend 디렉토리로 이동
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어서 API URL 설정

# 개발 서버 실행
npm run dev
```

Frontend는 `http://localhost:3000`에서 실행됩니다.

### 2. Backend 설정

```bash
# backend 디렉토리로 이동
cd backend

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
# .env 파일을 생성하고 다음 내용 추가:
# DATABASE_URL=postgresql://user:password@localhost:5432/posture_analysis
# REDIS_URL=redis://localhost:6379/0
# SECRET_KEY=your-secret-key-here
# CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 데이터베이스 마이그레이션 (선택사항)
# alembic init alembic
# alembic revision --autogenerate -m "Initial migration"
# alembic upgrade head

# 개발 서버 실행
uvicorn api.main:app --reload
```

Backend API는 `http://localhost:8000`에서 실행됩니다.

### 3. Redis 설정 (Celery용)

#### 로컬 설치
```bash
# Windows (Chocolatey)
choco install redis-64

# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis
```

#### Docker 사용
```bash
docker run -d -p 6379:6379 redis:alpine
```

### 4. PostgreSQL 설정

#### 로컬 설치
- [PostgreSQL 공식 사이트](https://www.postgresql.org/download/)에서 다운로드

#### Docker 사용
```bash
docker run -d \
  -e POSTGRES_USER=posture_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=posture_analysis \
  -p 5432:5432 \
  postgres:15
```

#### 클라우드 옵션
- **Render**: 무료 PostgreSQL 제공
- **Supabase**: 무료 PostgreSQL 제공
- **Railway**: PostgreSQL 추가 가능

## 📦 프로젝트 구조

```
PostureAnalysis/
├── frontend/              # React 프론트엔드
│   ├── src/
│   │   ├── components/    # React 컴포넌트
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/               # FastAPI 백엔드
│   ├── api/              # API 라우트
│   ├── services/         # 비즈니스 로직
│   ├── tasks/            # Celery 작업
│   ├── models/           # 데이터베이스 모델
│   ├── requirements.txt
│   └── Dockerfile
│
└── README.md
```

## 🔧 개발 워크플로우

### Frontend 개발
```bash
cd frontend
npm run dev
```

### Backend 개발
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn api.main:app --reload
```

### Celery Worker 실행 (별도 터미널)
```bash
cd backend
source venv/bin/activate
celery -A tasks.analysis_task worker --loglevel=info
```

## 🌐 배포

### Frontend (Vercel)

1. **Vercel 계정 생성**: https://vercel.com
2. **프로젝트 연결**:
   ```bash
   cd frontend
   npm install -g vercel
   vercel login
   vercel
   ```
3. **환경 변수 설정**: Vercel 대시보드에서 `VITE_API_URL` 설정

### Backend (Render)

1. **Render 계정 생성**: https://render.com
2. **GitHub 레포지토리 연결**
3. **Web Service 생성**:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. **환경 변수 설정**: Render 대시보드에서 설정
5. **PostgreSQL 추가**: Render 대시보드에서 새 PostgreSQL 생성
6. **Redis 추가**: Render 대시보드에서 새 Redis 생성
7. **Worker 추가**: `render.yaml` 파일 사용 또는 수동 생성

### Backend (Railway)

1. **Railway 계정 생성**: https://railway.app
2. **GitHub 레포지토리 연결**
3. **New Project → Deploy from GitHub**
4. **Root Directory**: `backend` 설정
5. **환경 변수 설정**: Railway 대시보드에서 설정
6. **PostgreSQL 추가**: Railway 대시보드에서 추가
7. **Redis 추가**: Railway 대시보드에서 추가

## 🧪 테스트

### API 테스트
```bash
# Health check
curl http://localhost:8000/api/health

# 분석 시작
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

## ⚠️ 문제 해결

### MediaPipe 설치 오류
```bash
# Windows에서 Visual C++ 재배포 가능 패키지 필요
# https://aka.ms/vs/17/release/vc_redist.x64.exe

# 또는 conda 사용
conda install -c conda-forge mediapipe
```

### Redis 연결 오류
- Redis가 실행 중인지 확인: `redis-cli ping`
- 환경 변수 `REDIS_URL` 확인

### PostgreSQL 연결 오류
- 데이터베이스가 실행 중인지 확인
- `DATABASE_URL` 형식 확인: `postgresql://user:password@host:port/dbname`

## 📚 추가 리소스

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [MediaPipe Pose](https://google.github.io/mediapipe/solutions/pose)
- [Vercel 문서](https://vercel.com/docs)
- [Render 문서](https://render.com/docs)
