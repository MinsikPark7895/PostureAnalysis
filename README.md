# Posture Analysis System

YouTube 영상에서 사람의 자세를 분석하여 스켈리톤과 자세 점수를 제공하는 시스템입니다.

## 프로젝트 개요

이 프로젝트는 YouTube 영상 URL을 입력받아 영상에서 사람의 자세를 분석하고, MediaPipe를 활용하여 스켈리톤을 추출한 후 자세 점수를 계산하여 시각화하는 웹 애플리케이션입니다.

주요 기능:
- YouTube 영상 다운로드 및 프레임 추출
- MediaPipe Pose를 사용한 실시간 자세 인식 및 스켈리톤 추출
- 어깨 정렬도, 척추 정렬도, 무릎 각도, 목 각도를 종합한 자세 점수 계산 (0-100점)
- 시간에 따른 점수 변화 그래프 시각화
- 스켈리톤이 그려진 프레임 이미지 표시 및 자동 재생

## 프로젝트 구조

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

## 사용한 기술

### Frontend
- **React 18** + **Vite** - 빠른 개발 환경 및 모던 프론트엔드 프레임워크
- **TypeScript** - 타입 안정성 보장
- **Recharts** - 점수 그래프 시각화
- **Axios** - API 통신
- **YouTube IFrame API** - 영상 표시

### Backend
- **Python 3.11+** - 백엔드 언어
- **FastAPI** - 고성능 웹 프레임워크
- **MediaPipe Pose** - 자세 인식 AI 모델 (스켈리톤 추출 및 관절 위치 감지)
- **Celery** - 비동기 작업 큐 (프로덕션 환경)
- **PostgreSQL** - 데이터베이스 (프로덕션 환경)
- **Redis** - 작업 큐 브로커 (Celery와 함께 사용)
- **yt-dlp** - YouTube 영상 다운로드
- **OpenCV** - 영상 처리 및 프레임 추출

### MediaPipe 활용
이 프로젝트는 **MediaPipe Pose**를 핵심 기술로 사용합니다:
- MediaPipe Pose 모델을 통해 영상의 각 프레임에서 사람의 관절 위치(landmarks)를 감지
- 감지된 관절 위치를 기반으로 스켈리톤을 그려 프레임 이미지에 시각화
- 어깨, 척추, 무릎, 목 등의 관절 위치를 분석하여 자세 점수 계산
