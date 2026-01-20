#!/bin/bash
# 프로젝트 초기화 스크립트

echo "🚀 Posture Analysis 프로젝트 초기화 시작..."

# Frontend 초기화
echo "📦 Frontend 의존성 설치 중..."
cd frontend
if [ -f "package.json" ]; then
    npm install
    echo "✅ Frontend 의존성 설치 완료"
else
    echo "❌ Frontend package.json을 찾을 수 없습니다"
fi
cd ..

# Backend 초기화
echo "🐍 Backend 가상 환경 생성 중..."
cd backend
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "✅ 가상 환경 생성 완료"
fi

echo "📦 Backend 의존성 설치 중..."
source venv/bin/activate
pip install -r requirements.txt
echo "✅ Backend 의존성 설치 완료"
deactivate
cd ..

echo "✨ 초기화 완료!"
echo ""
echo "다음 단계:"
echo "1. Frontend: cd frontend && npm run dev"
echo "2. Backend: cd backend && source venv/bin/activate && uvicorn api.main:app --reload"
echo "3. Celery Worker: cd backend && source venv/bin/activate && celery -A tasks.analysis_task worker --loglevel=info"
echo ""
echo "자세한 내용은 SETUP.md를 참고하세요."
