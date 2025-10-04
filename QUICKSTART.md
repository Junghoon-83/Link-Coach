# Link-Coach MVP 빠른 시작 가이드

## 🎯 현재 상황

Link-Coach MVP 프로젝트가 완전히 구축되었습니다!

## 📋 실행 전 확인사항

### ✅ 이미 완료된 항목
- [x] 전체 프로젝트 구조 생성 (60+ 파일)
- [x] Docker 설정 파일 (docker-compose.yml)
- [x] 환경 변수 파일 (server/.env, widget/.env)
- [x] 초기화 스크립트 작성
- [x] 샘플 데이터 및 모델

### ⚠️ 실행 전 필수 설정

#### 1. Google Gemini API 키 설정 (필수)

`server/.env` 파일을 열어 다음을 설정:

```bash
# server/.env 파일 수정
GEMINI_API_KEY=your-actual-api-key-here
```

**API 키 발급 방법:**
1. https://aistudio.google.com/app/apikey 접속
2. "Create API Key" 클릭
3. 발급받은 키를 복사하여 .env 파일에 붙여넣기

## 🚀 실행 방법

### 방법 1: Docker 사용 (권장)

Docker Desktop이 설치되어 있는 경우:

```bash
cd /Users/jhuny_mac/Develop/Link-Coach

# 전체 시스템 자동 설치 및 실행
./setup.sh
```

**setup.sh가 자동으로 수행:**
- ✅ Docker 컨테이너 시작
- ✅ ML 모델 생성
- ✅ 데이터베이스 초기화
- ✅ ChromaDB 데이터 임베딩
- ✅ 헬스체크

### 방법 2: 로컬 개발 환경

Docker 없이 로컬에서 실행:

```bash
# 1. 로컬 환경 설정
./setup-local.sh

# 2. 백엔드 실행 (터미널 1)
cd server
source venv/bin/activate
uvicorn app.main:app --reload

# 3. 프론트엔드 실행 (터미널 2)
cd widget
npm run dev
```

**주의:** 로컬 실행 시 PostgreSQL과 ChromaDB를 별도로 설치해야 합니다.

## 📍 접속 URL

설치 완료 후 다음 URL로 접속:

| 서비스 | URL | 설명 |
|--------|-----|------|
| **프론트엔드 위젯** | http://localhost:5173 | React 위젯 UI |
| **API 문서** | http://localhost:8000/docs | Swagger UI |
| **백엔드 API** | http://localhost:8000 | FastAPI 서버 |
| **헬스체크** | http://localhost:8000/health | 서버 상태 |

## 🧪 테스트 방법

### 1. 헬스체크

```bash
curl http://localhost:8000/health
```

### 2. API 테스트

```bash
# AI 리포트 생성 테스트
curl -X POST http://localhost:8000/api/v1/coaching/interpretation \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{
    "user_id": "test_user_123",
    "leadership_type": "ENTJ",
    "assessment_data": null
  }'
```

### 3. 프론트엔드 테스트

1. 브라우저에서 http://localhost:5173 접속
2. 위젯이 자동으로 초기화됨 (개발 모드)
3. "해석 리포트" 탭에서 AI 생성 리포트 확인
4. "AI 코칭 Q&A" 탭에서 질문 테스트

## 🔧 개발 팁

### 로그 확인

```bash
# Docker 로그
docker-compose logs -f server

# 특정 서비스 로그만
docker-compose logs -f chromadb
```

### 데이터베이스 접속

```bash
# PostgreSQL 접속
docker-compose exec postgres psql -U linkcoach_user -d linkcoach

# 테이블 확인
\dt
```

### 서비스 재시작

```bash
# 전체 재시작
docker-compose restart

# 특정 서비스만
docker-compose restart server
```

### 서비스 중지

```bash
# 모든 컨테이너 중지
docker-compose down

# 볼륨까지 삭제 (초기화)
docker-compose down -v
```

## 🐛 문제 해결

### 1. Docker 컨테이너가 시작되지 않는 경우

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs

# 완전 재시작
docker-compose down
docker-compose up -d
```

### 2. "GEMINI_API_KEY" 오류

- `server/.env` 파일에서 실제 API 키를 설정했는지 확인
- API 키가 유효한지 확인: https://aistudio.google.com

### 3. ChromaDB 연결 오류

```bash
# ChromaDB 재시작
docker-compose restart chromadb

# ChromaDB 로그 확인
docker-compose logs chromadb
```

### 4. 포트 충돌

다른 서비스가 이미 포트를 사용 중인 경우:

```bash
# 사용 중인 포트 확인 (macOS)
lsof -i :8000
lsof -i :5173

# docker-compose.yml에서 포트 변경
```

## 📚 추가 리소스

- [전체 README](./README.md) - 상세한 프로젝트 문서
- [API 문서](http://localhost:8000/docs) - Swagger UI
- [아키텍처 다이어그램](./README.md#시스템-아키텍처)

## 🎉 다음 단계

1. ✅ Google Gemini API 키 설정
2. ✅ `./setup.sh` 또는 `./setup-local.sh` 실행
3. ✅ http://localhost:5173 접속하여 테스트
4. 실제 ML 모델로 교체
5. 실제 임상 데이터로 ChromaDB 업데이트
6. 'Link' 웹사이트와 통합

---

**문제가 발생하면 이 문서를 참고하거나, GitHub Issues에 질문을 올려주세요!**
