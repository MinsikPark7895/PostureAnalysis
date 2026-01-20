# 프로젝트 초기화 스크립트 (Windows PowerShell)

Write-Host "🚀 Posture Analysis 프로젝트 초기화 시작..." -ForegroundColor Green

# Frontend 초기화
Write-Host "📦 Frontend 의존성 설치 중..." -ForegroundColor Yellow
Set-Location frontend
if (Test-Path "package.json") {
    npm install
    Write-Host "✅ Frontend 의존성 설치 완료" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend package.json을 찾을 수 없습니다" -ForegroundColor Red
}
Set-Location ..

# Backend 초기화
Write-Host "🐍 Backend 가상 환경 생성 중..." -ForegroundColor Yellow
Set-Location backend
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ 가상 환경 생성 완료" -ForegroundColor Green
}

Write-Host "📦 Backend 의존성 설치 중..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Write-Host "✅ Backend 의존성 설치 완료" -ForegroundColor Green
deactivate
Set-Location ..

Write-Host "✨ 초기화 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Cyan
Write-Host "1. Frontend: cd frontend; npm run dev"
Write-Host "2. Backend: cd backend; .\venv\Scripts\Activate.ps1; uvicorn api.main:app --reload"
Write-Host "3. Celery Worker: cd backend; .\venv\Scripts\Activate.ps1; celery -A tasks.analysis_task worker --loglevel=info"
Write-Host ""
Write-Host "자세한 내용은 SETUP.md를 참고하세요." -ForegroundColor Cyan
