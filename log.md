# 이화여자대학교 캡스톤디자인프로젝트 2026년 1학기 스타트 03팀 올톨로지

# 배포 오류 원인 분석 로그 (Vercel FE+BE)

## 1) 증상

- **FE 접속**: `https://calc-alltology.vercel.app/`에서 `404 NOT_FOUND` 발생
- **BE 호출**: 한때 `500 INTERNAL_SERVER_ERROR (FUNCTION_INVOCATION_FAILED)` 발생
- Vercel 로그에 다음처럼 찍힘:
  - `GET / HTTP/1.1" 404 -`

## 2) 핵심 원인 (Root Cause)

### A. `/` 라우팅이 정적 파일로 가지 않고 “Functions(서버리스)”로 잡힘

- Vercel 프로젝트에서 **Framework Preset이 `FastAPI`로 설정**되어 있으면,
  - 배포 결과 요약(Deployment Summary)에 **Functions가 `/`** 로 생성되는 경우가 있음
  - 이때 루트 경로(`/`) 요청이 **정적 `index.html`이 아니라 Python 함수로 전달**
- Python 함수(백엔드)는 기본적으로 `/` 라우트를 제공하지 않으므로 **`/`에서 404**가 남
- 실제로 Vercel 화면에서도
  - **Static Assets**: `/index.html` 존재
  - **Functions**: `/` 존재
  - 이 조합이 “루트가 함수로 흘러감”을 의미했음

### B. 백엔드 런타임 크래시(500)로 FE에서 “에러” 표시

- FE는 `/api/add`를 호출하는데, BE가 크래시하면 FE에서 결과 대신 “에러”가 표시됨
- 초기에는 FastAPI 서버리스 실행 방식이 Vercel 설정/프리셋과 충돌하면서 `500`이 발생했음

## 3) 해결 방법 (Resolution)

### A. Vercel 설정에서 프레임워크 프리셋을 해제

- **Settings → General → Framework Preset**
  - `FastAPI` → **`Other`(= 프리셋 비활성화)** 로 변경 후 저장
- 이 조치로 Vercel이 `/`를 Functions로 잡는 문제가 완화/해결됨

### B. 라우팅을 명확히 분리 (정적 `/` vs API `/api/*`)

- `vercel.json`을 사용해 다음 의도를 명시:
  - **`/api/*`만** 서버리스 함수(`api/index.py`)로 라우팅
  - **`/` 및 나머지 경로는** 정적 `index.html`로 라우팅

## 4) 재발 방지 체크리스트

- Vercel의 **Framework Preset이 `FastAPI`로 자동 감지되어 있으면**, `/`가 Functions로 잡혀 FE가 404가 날 수 있음  
  → **Preset을 `Other`로 변경**하는 것을 우선 확인
- Deployment Summary에서 **Functions에 `/`가 생겼는지** 확인
  - 생겼다면 `/` 요청이 함수로 흘러갈 가능성이 큼
- 정적 FE는 `public/index.html`에 두는 것이 가장 안전함

## 5) “클릭하면 Web에서 BE 파일을 바로 보여주는 URL”이란?

보통 과제/보고서에서 말하는 “클릭하면 BE 파일을 볼 수 있는 URL”은 **GitHub의 파일 링크**를 의미합니다.

- **BE 파일(현재 프로젝트)**: `api/index.py`
- **웹에서 바로 보는 링크**: `https://github.com/ryeong03/0326/blob/main/api/index.py`

해당 링크를 제출 문서(보고서/README)에 넣으면, 클릭했을 때 브라우저에서 백엔드 코드가 바로 열립니다.

