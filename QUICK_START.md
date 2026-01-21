# 빠른 시작 가이드

## 🚀 로컬 실행 (개발 모드)

### 방법 1: 메모리 저장소 사용 (가장 간단)

PostgreSQL과 Redis 없이 실행 가능합니다.

#### 1. Backend 실행

```bash
cd backend

# 가상 환경 생성 (처음 한 번만)
python -m venv venv

# 가상 환경 활성화
# Windows PowerShell (오류 발생 시 아래 참고):
venv\Scripts\activate
# Windows CMD:
venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# PowerShell 실행 정책 오류 발생 시:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# 또는 CMD를 사용하세요

# 의존성 설치
pip install -r requirements.txt

# 서버 실행 (메모리 저장소 모드)
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

#### 1. PostgreSQL 실행

**Docker 사용:**
```bash
docker run -d \
  -e POSTGRES_USER=posture_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=posture_analysis \
  -p 5432:5432 \
  postgres:15
```

**또는 로컬 PostgreSQL 설치 후:**
```bash
createdb posture_analysis
```

#### 2. Redis 실행

**Docker 사용:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**또는 로컬 Redis 설치 후:**
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

#### 3. 환경 변수 설정

`backend/.env` 파일 생성:
```bash
DATABASE_URL=postgresql://posture_user:your_password@localhost:5432/posture_analysis
REDIS_URL=redis://localhost:6379/0
USE_CELERY=true
USE_MEMORY_STORE=false
CREATE_TABLES=true
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### 4. Backend 실행

```bash
cd backend
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn api.main:app --reload
```

#### 5. Celery Worker 실행 (새 터미널)

```bash
cd backend
venv\Scripts\activate  # Windows
celery -A tasks.analysis_task worker --loglevel=info
```

#### 6. Frontend 실행 (새 터미널)

```bash
cd frontend
npm install
npm run dev
```

## 🌐 배포 방법

### 옵션 1: Render (추천 - 무료 티어 제공)

#### 1. GitHub에 코드 푸시

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/PostureAnalysis.git
git push -u origin main
```

#### 2. Render 대시보드 설정

**PostgreSQL 생성:**
1. [Render Dashboard](https://dashboard.render.com) 접속
2. New → PostgreSQL 클릭
3. 이름: `posture-analysis-db`
4. Plan: Free 선택
5. Create Database 클릭
6. **Internal Database URL** 복사 (예: `postgresql://user:password@host:5432/dbname`)

**Redis 생성:**
1. New → Redis 클릭
2. 이름: `posture-analysis-redis`
3. Plan: Free 선택
4. Create Redis 클릭
5. **Internal Redis URL** 복사 (예: `redis://host:6379`)

**Web Service 생성:**
1. New → Web Service 클릭
2. GitHub 레포지토리 연결
3. 설정:
   - **Name**: `posture-analysis-api`
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables 추가:
   ```
   DATABASE_URL = <PostgreSQL Internal URL>
   REDIS_URL = <Redis Internal URL>
   USE_CELERY = true
   USE_MEMORY_STORE = false
   CREATE_TABLES = true
   CORS_ORIGINS = https://your-frontend.vercel.app
   ```
5. Create Web Service 클릭

**Background Worker 생성:**
1. New → Background Worker 클릭
2. 같은 GitHub 레포지토리 선택
3. 설정:
   - **Name**: `posture-analysis-worker`
   - **Root Directory**: `backend`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A tasks.analysis_task worker --loglevel=info`
4. Environment Variables 추가 (Web Service와 동일):
   ```
   DATABASE_URL = <PostgreSQL Internal URL>
   REDIS_URL = <Redis Internal URL>
   USE_CELERY = true
   USE_MEMORY_STORE = false
   ```
5. Create Background Worker 클릭

**Frontend 배포 (Vercel):**
1. [Vercel](https://vercel.com) 접속
2. New Project 클릭
3. GitHub 레포지토리 연결
4. 설정:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
5. Environment Variables 추가:
   ```
   VITE_API_URL = https://posture-analysis-api.onrender.com
   ```
6. Deploy 클릭

### 옵션 2: Railway

#### 1. GitHub에 코드 푸시 (위와 동일)

#### 2. Railway 대시보드 설정

1. [Railway](https://railway.app) 접속
2. New Project → Deploy from GitHub
3. 레포지토리 선택

**PostgreSQL 추가:**
1. New → Database → Add PostgreSQL
2. 자동으로 환경 변수 `DATABASE_URL` 생성됨

**Redis 추가:**
1. New → Database → Add Redis
2. 자동으로 환경 변수 `REDIS_URL` 생성됨

**서비스 설정:**
1. 서비스 → Settings
2. Root Directory: `backend`
3. Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. Environment Variables 추가:
   ```
   USE_CELERY = true
   USE_MEMORY_STORE = false
   CREATE_TABLES = true
   CORS_ORIGINS = https://your-frontend.vercel.app
   ```

**Worker 추가:**
1. New → Service → Empty Service
2. GitHub 레포지토리 연결
3. Root Directory: `backend`
4. Start Command: `celery -A tasks.analysis_task worker --loglevel=info`
5. Environment Variables는 자동으로 공유됨

**Frontend 배포:**
- Vercel 사용 (위와 동일)
- 또는 Railway에서 새 서비스로 배포

## ✅ 배포 확인

### 1. API 서버 확인
```bash
curl https://your-api-url.onrender.com/api/health
```

### 2. Frontend 확인
브라우저에서 프론트엔드 URL 접속

### 3. 분석 테스트
1. 프론트엔드에서 YouTube URL 입력
2. 분석 시작
3. 결과 확인

## 🔧 문제 해결

### Backend가 시작되지 않음
- 환경 변수 확인
- 로그 확인: Render/Railway Dashboard → Logs

### Celery Worker가 작업을 받지 못함
- Redis 연결 확인
- Worker 로그 확인
- `USE_CELERY=true` 확인

### 데이터베이스 연결 오류
- `DATABASE_URL` 확인
- PostgreSQL 서버 실행 확인
- `CREATE_TABLES=true` 설정 (첫 배포 시)

### CORS 오류
- `CORS_ORIGINS`에 프론트엔드 URL 포함 확인
- 프론트엔드의 `VITE_API_URL` 확인

## 📝 체크리스트

### 로컬 실행
- [ ] Python 3.11+ 설치
- [ ] Node.js 18+ 설치
- [ ] Backend 의존성 설치
- [ ] Frontend 의존성 설치
- [ ] 서버 실행 확인

### 배포
- [ ] GitHub에 코드 푸시
- [ ] PostgreSQL 생성 및 URL 복사
- [ ] Redis 생성 및 URL 복사
- [ ] Web Service 생성 및 환경 변수 설정
- [ ] Background Worker 생성 및 환경 변수 설정
- [ ] Frontend 배포 및 API URL 설정
- [ ] 모든 서비스 실행 확인
