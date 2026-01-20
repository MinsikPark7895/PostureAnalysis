# 배포 가이드

## 📋 배포 전 준비

### 1. 코드 준비
```bash
# Git 초기화 (아직 안 했다면)
git init
git add .
git commit -m "Ready for deployment"

# GitHub에 푸시
git remote add origin https://github.com/your-username/PostureAnalysis.git
git push -u origin main
```

### 2. 필요한 계정
- [GitHub](https://github.com) 계정
- [Render](https://render.com) 또는 [Railway](https://railway.app) 계정
- [Vercel](https://vercel.com) 계정 (프론트엔드용)

## 🚀 Render 배포 (단계별)

### Step 1: PostgreSQL 생성

1. [Render Dashboard](https://dashboard.render.com) 접속
2. **New** → **PostgreSQL** 클릭
3. 설정:
   - **Name**: `posture-analysis-db`
   - **Database**: `posture_analysis`
   - **User**: `posture_user`
   - **Region**: 가장 가까운 지역 선택
   - **Plan**: Free (또는 Starter)
4. **Create Database** 클릭
5. 생성 완료 후 **Internal Database URL** 복사
   - 예: `postgresql://posture_user:password@dpg-xxxxx-a/posture_analysis`

### Step 2: Redis 생성

1. **New** → **Redis** 클릭
2. 설정:
   - **Name**: `posture-analysis-redis`
   - **Region**: PostgreSQL과 동일한 지역
   - **Plan**: Free
3. **Create Redis** 클릭
4. 생성 완료 후 **Internal Redis URL** 복사
   - 예: `redis://red-xxxxx:6379`

### Step 3: Web Service 생성 (Backend API)

1. **New** → **Web Service** 클릭
2. **Connect GitHub** 클릭하여 레포지토리 연결
3. 레포지토리 선택 후 **Connect** 클릭
4. 설정:
   - **Name**: `posture-analysis-api`
   - **Region**: PostgreSQL과 동일한 지역
   - **Branch**: `main`
   - **Root Directory**: `backend` ⚠️ 중요!
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. **Advanced** → **Environment Variables** 추가:
   ```
   DATABASE_URL = <PostgreSQL Internal URL>
   REDIS_URL = <Redis Internal URL>
   USE_CELERY = true
   USE_MEMORY_STORE = false
   CREATE_TABLES = true
   CORS_ORIGINS = https://your-frontend.vercel.app
   ```
6. **Create Web Service** 클릭
7. 배포 완료까지 대기 (약 5-10분)
8. 배포 완료 후 **URL** 복사 (예: `https://posture-analysis-api.onrender.com`)

### Step 4: Background Worker 생성 (Celery)

1. **New** → **Background Worker** 클릭
2. 같은 GitHub 레포지토리 선택
3. 설정:
   - **Name**: `posture-analysis-worker`
   - **Region**: Web Service와 동일
   - **Branch**: `main`
   - **Root Directory**: `backend` ⚠️ 중요!
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A tasks.analysis_task worker --loglevel=info`
4. **Environment Variables** 추가 (Web Service와 동일):
   ```
   DATABASE_URL = <PostgreSQL Internal URL>
   REDIS_URL = <Redis Internal URL>
   USE_CELERY = true
   USE_MEMORY_STORE = false
   ```
5. **Create Background Worker** 클릭

### Step 5: Frontend 배포 (Vercel)

1. [Vercel](https://vercel.com) 접속
2. **Add New** → **Project** 클릭
3. GitHub 레포지토리 선택
4. 설정:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend` ⚠️ 중요!
   - **Build Command**: `npm run build` (자동 감지)
   - **Output Directory**: `dist` (자동 감지)
5. **Environment Variables** 추가:
   ```
   VITE_API_URL = https://posture-analysis-api.onrender.com
   ```
6. **Deploy** 클릭
7. 배포 완료 후 **URL** 확인

### Step 6: CORS 설정 업데이트

1. Render Dashboard → Web Service → Environment
2. `CORS_ORIGINS` 값을 Vercel 프론트엔드 URL로 업데이트:
   ```
   CORS_ORIGINS = https://your-frontend.vercel.app
   ```
3. **Save Changes** 클릭
4. 서비스 재시작 (자동)

## ✅ 배포 확인

### 1. API Health Check
```bash
curl https://your-api-url.onrender.com/api/health
```
응답: `{"status":"healthy"}`

### 2. Frontend 접속
브라우저에서 Vercel URL 접속

### 3. 분석 테스트
1. YouTube URL 입력
2. 분석 시작
3. 결과 확인

## 🔧 문제 해결

### 배포 실패

**문제**: Build 실패
- **해결**: Render Dashboard → Logs 확인
- **원인**: 의존성 설치 실패, Python 버전 문제 등

**문제**: 서버 시작 실패
- **해결**: Start Command 확인
- **원인**: 포트 설정 오류, 환경 변수 누락

### 연결 오류

**문제**: 데이터베이스 연결 실패
- **해결**: `DATABASE_URL` 확인
- **원인**: Internal URL 사용 안 함, 비밀번호 오류

**문제**: Redis 연결 실패
- **해결**: `REDIS_URL` 확인
- **원인**: Internal URL 사용 안 함

### Celery Worker 문제

**문제**: Worker가 작업을 받지 못함
- **해결**: 
  1. Worker 로그 확인
  2. `REDIS_URL` 확인
  3. `USE_CELERY=true` 확인

**문제**: 작업이 완료되지 않음
- **해결**: 
  1. Worker 로그 확인
  2. MediaPipe 설치 확인
  3. 메모리 부족 확인

### CORS 오류

**문제**: 프론트엔드에서 API 호출 실패
- **해결**: 
  1. `CORS_ORIGINS`에 프론트엔드 URL 포함 확인
  2. 프론트엔드의 `VITE_API_URL` 확인

## 📊 모니터링

### Render Dashboard
- **Metrics**: CPU, Memory 사용량
- **Logs**: 실시간 로그 확인
- **Events**: 배포 이벤트 확인

### Vercel Dashboard
- **Analytics**: 트래픽 분석
- **Logs**: 프론트엔드 로그

## 💰 비용

### Render 무료 티어
- PostgreSQL: 90일 무료 (이후 $7/월)
- Redis: 30일 무료 (이후 $10/월)
- Web Service: 무료 (제한적)
- Background Worker: 무료 (제한적)

### Vercel
- 프론트엔드: 무료 (제한적)

### 추천
- **개인 프로젝트**: 무료 티어로 시작
- **프로덕션**: Starter 플랜 ($7-25/월)

## 🔄 업데이트 배포

코드 변경 후:
```bash
git add .
git commit -m "Update"
git push
```

Render와 Vercel은 자동으로 재배포합니다.

## 📝 체크리스트

배포 전:
- [ ] GitHub에 코드 푸시
- [ ] 모든 테스트 통과
- [ ] 환경 변수 준비

배포 중:
- [ ] PostgreSQL 생성 및 URL 복사
- [ ] Redis 생성 및 URL 복사
- [ ] Web Service 생성 및 환경 변수 설정
- [ ] Background Worker 생성 및 환경 변수 설정
- [ ] Frontend 배포 및 API URL 설정

배포 후:
- [ ] API Health Check 통과
- [ ] Frontend 접속 확인
- [ ] 분석 기능 테스트
- [ ] CORS 설정 확인
