# 프로덕션 배포 설정 가이드

## 완전한 개선 사항

✅ **PostgreSQL 데이터베이스 통합**
✅ **Celery + Redis 작업 큐**
✅ **여러 인스턴스 지원**
✅ **데이터 영구 저장**

## 환경 변수 설정

### 필수 환경 변수

```bash
# 데이터베이스 (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/posture_analysis

# Redis (Celery 작업 큐)
REDIS_URL=redis://host:6379/0

# Celery 사용 여부 (기본값: true)
USE_CELERY=true
```

### 선택적 환경 변수

```bash
# 메모리 저장소 사용 (개발 환경, 기본값: false)
USE_MEMORY_STORE=false

# 테이블 자동 생성 (개발 환경, 기본값: false)
CREATE_TABLES=false

# CORS 설정
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-domain.com

# 보안
SECRET_KEY=your-secret-key-here
```

## 배포 단계

### 1. 데이터베이스 설정

#### PostgreSQL 생성 (Render 예시)
1. Render 대시보드에서 새 PostgreSQL 생성
2. 데이터베이스 URL 복사
3. 환경 변수에 `DATABASE_URL` 설정

#### 로컬 개발
```bash
# Docker 사용
docker run -d \
  -e POSTGRES_USER=posture_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=posture_analysis \
  -p 5432:5432 \
  postgres:15

# DATABASE_URL 설정
export DATABASE_URL=postgresql://posture_user:your_password@localhost:5432/posture_analysis
```

### 2. Redis 설정

#### Redis 생성 (Render 예시)
1. Render 대시보드에서 새 Redis 생성
2. Redis URL 복사
3. 환경 변수에 `REDIS_URL` 설정

#### 로컬 개발
```bash
# Docker 사용
docker run -d -p 6379:6379 redis:alpine

# REDIS_URL 설정
export REDIS_URL=redis://localhost:6379/0
```

### 3. 데이터베이스 테이블 생성

#### 방법 1: 환경 변수로 자동 생성
```bash
export CREATE_TABLES=true
# 서버 시작 시 자동으로 테이블 생성
```

#### 방법 2: Alembic 사용 (권장)
```bash
# Alembic 초기화 (처음 한 번만)
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Initial migration"

# 마이그레이션 적용
alembic upgrade head
```

### 4. Celery Worker 실행

#### 로컬 개발
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
celery -A tasks.analysis_task worker --loglevel=info
```

#### 프로덕션 (Render Worker)
1. Render 대시보드에서 새 Background Worker 생성
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `celery -A tasks.analysis_task worker --loglevel=info`
5. 환경 변수 설정:
   - `REDIS_URL`
   - `DATABASE_URL`
   - `USE_CELERY=true`

### 5. API 서버 실행

#### 로컬 개발
```bash
cd backend
source venv/bin/activate
uvicorn api.main:app --reload
```

#### 프로덕션 (Render Web Service)
1. Render 대시보드에서 새 Web Service 생성
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. 환경 변수 설정:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `USE_CELERY=true`
   - `CORS_ORIGINS`

## 저장소 선택

시스템은 환경 변수에 따라 자동으로 저장소를 선택합니다:

### PostgreSQL 사용 (프로덕션)
```bash
DATABASE_URL=postgresql://...
USE_MEMORY_STORE=false  # 또는 설정 안 함
```

### 메모리 저장소 사용 (개발)
```bash
USE_MEMORY_STORE=true
# 또는 DATABASE_URL을 설정하지 않음
```

## 작업 큐 선택

### Celery 사용 (프로덕션)
```bash
REDIS_URL=redis://...
USE_CELERY=true  # 또는 설정 안 함
```

### BackgroundTasks 사용 (개발)
```bash
USE_CELERY=false
# 또는 REDIS_URL을 설정하지 않음
```

## 문제 해결

### 데이터베이스 연결 오류
```bash
# 연결 테스트
psql $DATABASE_URL

# 테이블 확인
psql $DATABASE_URL -c "\dt"
```

### Redis 연결 오류
```bash
# 연결 테스트
redis-cli -u $REDIS_URL ping
```

### Celery Worker가 작업을 받지 못함
1. Redis 연결 확인
2. Worker 로그 확인
3. `USE_CELERY=true` 확인

## 배포 체크리스트

- [ ] PostgreSQL 데이터베이스 생성 및 연결
- [ ] Redis 생성 및 연결
- [ ] 환경 변수 설정
- [ ] 데이터베이스 테이블 생성
- [ ] Celery Worker 실행
- [ ] API 서버 실행
- [ ] CORS 설정 확인
- [ ] 프론트엔드 API URL 설정

## 성능 최적화

1. **데이터베이스 연결 풀링**: 프로덕션에서는 연결 풀 설정
2. **Celery Worker 수**: `celery -A tasks.analysis_task worker --concurrency=4`
3. **Redis 메모리**: 충분한 메모리 할당
4. **데이터베이스 인덱스**: 자주 조회하는 필드에 인덱스 추가
