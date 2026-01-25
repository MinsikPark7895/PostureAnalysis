# Windows PowerShell 실행 정책 오류 해결

## 문제

PowerShell에서 가상 환경을 활성화할 때 다음 오류가 발생:
```
이 시스템에서 스크립트를 실행할 수 없으므로 ... Activate.ps1 파일을 로드할 수 없습니다.
```

## 해결 방법

### 방법 1: 실행 정책 변경 (권장)

현재 사용자에 대해서만 실행 정책 변경:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

그 후 다시 활성화:
```powershell
venv\Scripts\activate
```

### 방법 2: 일시적으로 실행 정책 우회

```powershell
powershell -ExecutionPolicy Bypass -File venv\Scripts\Activate.ps1
```

### 방법 3: CMD 사용 (가장 간단)

PowerShell 대신 Command Prompt (CMD) 사용:

```cmd
cd backend
venv\Scripts\activate.bat
```

### 방법 4: 직접 Python 실행

가상 환경을 활성화하지 않고 직접 실행:

```powershell
# 가상 환경의 Python 직접 사용
.\venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

## 실행 정책 설명

- **Restricted**: 스크립트 실행 불가 (기본값)
- **RemoteSigned**: 로컬 스크립트는 실행 가능, 원격 스크립트는 서명 필요
- **Unrestricted**: 모든 스크립트 실행 가능 (비권장)

## 권장 방법

**방법 1 (실행 정책 변경)** 또는 **방법 3 (CMD 사용)**을 권장합니다.
