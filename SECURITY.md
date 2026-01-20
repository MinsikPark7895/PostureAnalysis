# 보안 가이드

## Git에 올리기 전 확인사항

### ✅ 안전한 항목
- 모든 코드 파일
- `.env.example` 파일 (실제 비밀번호 없음)
- 설정 파일들 (render.yaml, railway.json 등)
- README 및 문서 파일

### ⚠️ 주의사항

1. **절대 Git에 올리면 안 되는 것들:**
   - `.env` 파일 (실제 비밀번호 포함)
   - `temp_videos/` 디렉토리 (다운로드된 영상)
   - `venv/` 또는 `node_modules/` (이미 .gitignore에 포함됨)
   - 실제 데이터베이스 파일

2. **현재 코드 상태:**
   - ✅ `.env` 파일은 `.gitignore`에 포함되어 있음
   - ✅ 모든 민감한 정보는 환경 변수로 관리
   - ✅ 하드코딩된 비밀번호 없음
   - ✅ 기본값들은 모두 예시일 뿐

3. **배포 전 확인:**
   - 환경 변수 설정 확인
   - CORS 설정 확인 (프로덕션 도메인만 허용)
   - Rate Limiting 추가 고려
   - HTTPS 사용

## 현재 보안 상태

### 안전함 ✅
- 코드에 실제 비밀번호나 API 키가 하드코딩되어 있지 않음
- `.gitignore`에 민감한 파일들이 포함되어 있음
- 환경 변수를 통한 설정 관리

### 개선 권장사항 (프로덕션 배포 시)
1. Rate Limiting 추가
2. 인증/인가 시스템 추가
3. 입력 검증 강화
4. 에러 메시지 일반화
5. 로깅 시스템 구축

## Git 초기화 및 푸시

```bash
# Git 초기화
git init

# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: Posture Analysis System"

# 원격 저장소 추가 (GitHub 등)
git remote add origin <your-repo-url>

# 푸시
git push -u origin main
```

## 환경 변수 설정 (로컬 개발)

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/posture_analysis
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

**주의**: 위의 값들은 예시입니다. 실제 비밀번호를 사용하세요.
