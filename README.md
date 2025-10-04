# Link-Coach MVP

AI 기반 개인화 리더십 코칭 서비스 - 임베디드 웹 위젯

## 📋 프로젝트 개요

Link-Coach는 기존 'Link' 진단 웹사이트에 통합할 수 있는 AI 기반 코칭 위젯입니다. 사용자의 리더십 유형을 분석하고 RAG(Retrieval-Augmented Generation) 기술을 활용하여 개인화된 해석과 실시간 Q&A를 제공합니다.

### 핵심 기능

- **AI 심층 해석 리포트**: 사용자의 리더십 유형에 대한 상세한 분석 리포트 생성
- **맥락 기반 Q&A**: 생성된 리포트 내용을 기반으로 한 스트리밍 방식의 AI 대화

### 기술 스택

**백엔드**
- Python 3.11
- FastAPI (비동기 웹 프레임워크)
- PostgreSQL (결과 캐시 및 로그)
- ChromaDB (Vector Database for RAG)
- Google Gemini (LLM)
- Scikit-learn (ML 모델)

**프론트엔드**
- React 18
- Vite (빌드 도구)
- Axios (HTTP 클라이언트)

**인프라**
- Docker & Docker Compose
- Google Cloud Run (예정)

## 🏗️ 시스템 아키텍처

```
Link Website
    ↓ (JWT Token + User Data)
Widget (React)
    ↓ (HTTPS API)
API Gateway (FastAPI)
    ↓
AI Service Layer
    ├── ML Model (leadership_classifier.pkl)
    ├── Vector DB (ChromaDB) → RAG Engine
    └── LLM Service (Google Gemini)
    ↓
PostgreSQL (Cache & Logs)
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd Link-Coach

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값을 입력:
# - GEMINI_API_KEY: Google Gemini API 키
# - JWT_SECRET_KEY: 강력한 랜덤 문자열
```

### 2. Docker로 실행

```bash
# 모든 서비스 시작 (PostgreSQL, ChromaDB, FastAPI, React)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 서비스 중지
docker-compose down
```

### 3. 접속 확인

- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **프론트엔드 위젯**: http://localhost:5173
- **PostgreSQL**: localhost:5432
- **ChromaDB**: http://localhost:8001

### 4. 헬스체크

```bash
# 백엔드 서버 상태 확인
curl http://localhost:8000/health

# 응답 예시:
# {
#   "status": "healthy",
#   "service": "Link-Coach API",
#   "version": "0.1.0",
#   "environment": "development"
# }
```

## 📁 프로젝트 구조

```
Link-Coach/
├── server/                      # 백엔드
│   ├── app/
│   │   ├── main.py             # FastAPI 앱 엔트리포인트
│   │   ├── config.py           # 설정 관리
│   │   ├── api/v1/endpoints/   # API 엔드포인트
│   │   ├── core/               # 보안, 로깅
│   │   ├── services/           # AI 서비스 레이어
│   │   ├── models/             # 데이터 모델
│   │   └── db/                 # DB 세션 관리
│   ├── models/                 # ML 모델 파일 (.pkl)
│   ├── requirements.txt
│   └── Dockerfile
│
├── widget/                      # 프론트엔드
│   ├── src/
│   │   ├── App.jsx             # 메인 앱
│   │   ├── components/         # React 컴포넌트
│   │   ├── services/api.js     # API 클라이언트
│   │   └── styles/widget.css   # 스타일시트
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml          # Docker 오케스트레이션
├── .env.example                # 환경 변수 템플릿
└── README.md
```

## 🔧 개발 가이드

### 로컬 개발 (Docker 없이)

**백엔드**

```bash
cd server

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

**프론트엔드**

```bash
cd widget

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### API 엔드포인트

#### 1. AI 심층 해석 리포트 생성

```http
POST /api/v1/coaching/interpretation
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "user_id": "user_123",
  "leadership_type": "ENTJ",
  "assessment_data": {}
}
```

**응답:**
```json
{
  "report_id": "rpt_abc123",
  "user_id": "user_123",
  "leadership_type": "ENTJ",
  "interpretation": "당신의 ENTJ 리더십 유형은...",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### 2. 맥락 기반 Q&A (스트리밍)

```http
POST /api/v1/coaching/query
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "user_id": "user_123",
  "report_id": "rpt_abc123",
  "question": "이 유형의 강점은 무엇인가요?",
  "conversation_history": []
}
```

**응답:** Server-Sent Events (SSE) 스트리밍
```
data: 당신의
data: ENTJ
data: 유형의
data: 강점은...
data: [DONE]
```

#### 3. 리포트 조회

```http
GET /api/v1/coaching/reports/{report_id}
Authorization: Bearer <JWT_TOKEN>
```

## 🔐 보안

### JWT 인증

모든 API 요청은 JWT 토큰을 통해 인증됩니다:

```javascript
// 위젯 초기화 시
setAuthToken(token)

// 자동으로 모든 요청 헤더에 추가됨
// Authorization: Bearer <token>
```

### CORS 설정

`.env` 파일에서 허용된 origin 설정:

```env
CORS_ORIGINS=http://localhost:5173,https://your-link-website.com
```

## 📊 데이터베이스

### 테이블 구조

- **reports**: AI 생성 리포트 저장
- **conversations**: Q&A 대화 로그
- **vector_documents**: ChromaDB 문서 메타데이터
- **api_logs**: API 요청 로그

### 마이그레이션

```bash
# 테이블 자동 생성 (개발 환경)
# app/main.py의 lifespan에서 자동 실행

# TODO: 프로덕션 환경에서는 Alembic 사용
```

## 🧪 테스트

```bash
cd server

# 유닛 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app tests/
```

## 📦 배포

### Google Cloud Run 배포 (예정)

```bash
# Docker 이미지 빌드
docker build -t linkcoach-server ./server
docker build -t linkcoach-widget ./widget

# Cloud Run에 배포
gcloud run deploy linkcoach-api \
  --image gcr.io/your-project/linkcoach-server \
  --platform managed \
  --region asia-northeast1
```

## 🛠️ 추가 개발 필요 항목

### 백엔드
- [ ] Alembic 마이그레이션 설정
- [ ] PostgreSQL 리포트 캐싱 구현 (현재 메모리 캐시)
- [ ] API 로그 미들웨어 구현
- [ ] ML 모델 실제 인터페이스 연동
- [ ] ChromaDB 초기 데이터 임베딩 스크립트

### 프론트엔드
- [ ] 에러 바운더리 추가
- [ ] 로딩 상태 개선
- [ ] 반응형 디자인 최적화
- [ ] 임베딩 스크립트 (embed.js) 작성
- [ ] E2E 테스트

### 인프라
- [ ] CI/CD 파이프라인 구축
- [ ] 모니터링 및 로깅 (Sentry, DataDog 등)
- [ ] 부하 테스트

## 🤝 기여 가이드

1. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
2. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
3. 브랜치 푸시 (`git push origin feature/AmazingFeature`)
4. Pull Request 생성

## 📝 라이선스

This project is licensed under the MIT License.

## 📞 문의

프로젝트 관련 문의사항은 이슈를 생성해주세요.

---

**Built with ❤️ by Link-Coach Team**
