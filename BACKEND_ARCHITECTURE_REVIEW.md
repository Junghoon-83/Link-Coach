# Link-Coach 백엔드 아키텍처 검토 보고서

**검토일**: 2025-10-10
**현재 상태**: Netlify Serverless Functions 운영 중
**목표 상태**: FastAPI + PostgreSQL + ChromaDB 통합 백엔드

---

## 📊 1. 현재 상태 분석

### 현재 구현 (Production - 운영 중)
- **위치**: `widget/netlify/functions/`
- **구조**: Netlify Serverless Functions (CommonJS .cjs)
- **AI 모델**: Google Gemini API 직접 호출
  - chat.cjs: `gemini-2.5-flash` (실시간 대화)
  - generate.cjs: `gemini-2.0-flash-exp` (리포트 생성 - 미사용)
- **데이터**: 클라이언트 사이드 더미 데이터
- **인증**: sessionStorage 토큰만 (실제 검증 없음)
- **데이터베이스**: 없음 (상태 없음)
- **배포**: https://link-coach.netlify.app

### 계획된 구조 (README.md - 미구현)
- **위치**: `server/app/`
- **프레임워크**: FastAPI (Python 3.11)
- **데이터베이스**:
  - PostgreSQL (결과 캐시 및 로그)
  - ChromaDB (Vector Database for RAG)
- **ML 모델**: `leadership_classifier.pkl`
- **인증**: JWT 기반 완전한 인증
- **아키텍처**: Layered Architecture
  - API Gateway (FastAPI)
  - Service Layer (AI, ML, RAG)
  - Data Layer (PostgreSQL, ChromaDB)

---

## 🔍 2. 갭 분석

| 항목 | 계획 (README) | 현재 구현 | 상태 | 우선순위 |
|------|--------------|----------|------|---------|
| API 서버 | FastAPI | Netlify Functions | ❌ 미구현 | P0 |
| 데이터베이스 | PostgreSQL | 없음 | ❌ 미구현 | P0 |
| Vector DB | ChromaDB | 없음 | ❌ 미구현 | P1 |
| ML 모델 | .pkl 파일 | 없음 | ❌ 미구현 | P2 |
| JWT 인증 | 완전한 구현 | 더미 토큰만 | ⚠️ 부분 구현 | P0 |
| 리포트 생성 | RAG + ML + LLM | 클라이언트 더미 데이터 | ❌ 미구현 | P1 |
| 대화 기능 | RAG 기반 맥락 | Gemini 직접 호출 | ✅ 작동 중 | - |
| 대화 저장 | PostgreSQL | 없음 (클라이언트만) | ❌ 미구현 | P1 |
| API 로깅 | 미들웨어 + DB | 없음 | ❌ 미구현 | P2 |
| 모니터링 | Sentry 등 | 없음 | ❌ 미구현 | P2 |

---

## 🔴 3. 주요 문제점

### 심각한 문제
1. **아키텍처 불일치**
   - README.md와 실제 구현이 완전히 다름
   - 개발자 혼란 가능성
   - 유지보수 어려움

2. **확장성 부족**
   - Serverless Functions는 stateless
   - 대화 히스토리가 클라이언트에만 존재
   - 서버 재시작 시 모든 컨텍스트 손실

3. **데이터 지속성 없음**
   - 사용자 대화 기록 미저장
   - 분석 불가능
   - 개인화 서비스 제공 불가

4. **보안 취약점**
   - JWT 검증 미구현
   - CORS 설정만 존재
   - API 키 노출 위험 (Netlify 환경변수는 안전)

### 개선 필요 사항
1. **RAG 미구현**
   - 맥락 기반 응답 불가능
   - 일관성 없는 답변
   - 지식 베이스 활용 불가

2. **캐싱 없음**
   - 동일 질문에 매번 Gemini API 호출
   - 비용 증가
   - 응답 속도 느림

3. **모니터링/로깅 없음**
   - 에러 추적 불가
   - 사용자 행동 분석 불가
   - 성능 병목 파악 어려움

4. **스케일링 전략 부재**
   - Netlify Functions의 콜드 스타트
   - 동시 접속 제한
   - 비용 예측 어려움

---

## 🚀 4. 개선 제안 (우선순위별 로드맵)

### Phase 1: 기본 백엔드 구축 (1-2주)

**목표**: FastAPI 서버 가동 + PostgreSQL 연결

#### 1.1 FastAPI 기본 구조 배포
```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**구현 사항**:
- [x] `app/main.py` 이미 존재 (활성화 필요)
- [x] Health check 엔드포인트 (`/health`)
- [x] CORS 설정
- [x] 기본 로깅
- [ ] 프로덕션 배포 (Google Cloud Run 또는 Railway)

#### 1.2 PostgreSQL 연결 및 스키마 생성
```bash
docker-compose up -d postgres
python server/scripts/init_database.py
```

**데이터베이스 스키마**:
```sql
-- 1. 사용자 테이블
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. 대화 세션 테이블
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    report_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_report_id (report_id)
);

-- 3. 메시지 테이블
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_conversation (conversation_id, created_at)
);

-- 4. 리포트 캐시 테이블
CREATE TABLE reports (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id),
    leadership_type VARCHAR(50) NOT NULL,
    interpretation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    UNIQUE INDEX idx_user_leadership (user_id, leadership_type)
);

-- 5. API 로그 테이블
CREATE TABLE api_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INT,
    response_time_ms INT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_endpoint (user_id, endpoint),
    INDEX idx_created_at (created_at)
);
```

#### 1.3 JWT 인증 완성
```python
# app/core/security.py 수정
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

def create_jwt_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**구현 체크리스트**:
- [ ] JWT 토큰 생성 함수
- [ ] JWT 토큰 검증 미들웨어
- [ ] 토큰 발급 엔드포인트 (`POST /api/v1/auth/token`)
- [ ] 보호된 엔드포인트에 Depends 적용
- [ ] 토큰 갱신 로직

---

### Phase 2: RAG 파이프라인 구축 (1개월)

**목표**: ChromaDB 통합 + 맥락 기반 응답

#### 2.1 ChromaDB 설정 및 초기 데이터 임베딩
```bash
docker-compose up -d chromadb
python server/scripts/init_chroma_data.py
```

**지식 베이스 구조**:
```
knowledge_base/
├── leadership_types/
│   ├── 개별비전형.md
│   ├── 팀성과형.md
│   └── ...
├── coaching_guides/
│   ├── 강점_활용하기.md
│   ├── 약점_개선하기.md
│   └── ...
└── case_studies/
    ├── 사례1_의사결정.md
    └── ...
```

**임베딩 스크립트**:
```python
# server/scripts/init_chroma_data.py
from chromadb import Client
from app.services.vector_db import vector_db_service
import glob

def embed_knowledge_base():
    # 모든 마크다운 파일 읽기
    docs = []
    for file_path in glob.glob("knowledge_base/**/*.md", recursive=True):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            docs.append({
                "content": content,
                "metadata": {
                    "source": file_path,
                    "category": file_path.split('/')[1]
                }
            })

    # ChromaDB에 임베딩
    vector_db_service.add_documents(docs)
```

#### 2.2 RAG 파이프라인 구현
```python
# app/services/rag_service.py
class RAGService:
    async def get_contextual_answer(
        self,
        question: str,
        leadership_type: str,
        conversation_history: List[dict]
    ) -> str:
        # 1. 질문 임베딩
        # 2. ChromaDB에서 관련 문서 검색
        relevant_docs = await vector_db_service.search(
            query=question,
            filters={"leadership_type": leadership_type},
            top_k=3
        )

        # 3. 컨텍스트 구성
        context = "\n\n".join([doc["content"] for doc in relevant_docs])

        # 4. Gemini에 프롬프트 전달
        prompt = f"""
        컨텍스트:
        {context}

        대화 히스토리:
        {self._format_history(conversation_history)}

        질문: {question}

        위 컨텍스트를 바탕으로 질문에 답변하세요.
        """

        # 5. Gemini API 호출
        answer = await self.gemini_service.generate(prompt)
        return answer
```

#### 2.3 리포트 캐싱 구현
```python
# app/api/v1/endpoints/coaching.py
@router.post("/interpretation")
async def generate_interpretation(
    request: InterpretationRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. 캐시 확인
    cached = db.query(Report).filter(
        Report.user_id == request.user_id,
        Report.leadership_type == request.leadership_type,
        Report.expires_at > datetime.now()
    ).first()

    if cached:
        return cached

    # 2. 새로 생성
    interpretation = await ai_service.generate_interpretation(request)

    # 3. DB 저장
    report = Report(
        id=generate_id(),
        user_id=request.user_id,
        leadership_type=request.leadership_type,
        interpretation=interpretation,
        expires_at=datetime.now() + timedelta(days=30)
    )
    db.add(report)
    db.commit()

    return report
```

**구현 체크리스트**:
- [ ] ChromaDB 연결 서비스
- [ ] 지식 베이스 문서 작성
- [ ] 임베딩 스크립트
- [ ] RAG 검색 로직
- [ ] 프롬프트 템플릿
- [ ] 리포트 캐싱 로직

---

### Phase 3: 고급 기능 (2-3개월)

#### 3.1 ML 모델 통합
```python
# app/services/ml_model.py
class LeadershipClassifier:
    def __init__(self):
        self.model = joblib.load("models/leadership_classifier.pkl")

    def predict(self, assessment_data: dict) -> dict:
        # 특징 추출
        features = self._extract_features(assessment_data)

        # 예측
        prediction = self.model.predict([features])[0]
        probabilities = self.model.predict_proba([features])[0]

        return {
            "leadership_type": prediction,
            "confidence": max(probabilities),
            "all_scores": dict(zip(self.model.classes_, probabilities))
        }
```

#### 3.2 스트리밍 응답 (SSE)
```python
# app/api/v1/endpoints/coaching.py
from fastapi.responses import StreamingResponse

@router.post("/query/stream")
async def query_stream(
    request: QueryRequest,
    current_user = Depends(get_current_user)
):
    async def generate():
        async for chunk in ai_service.stream_answer(request.question):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

#### 3.3 모니터링 및 로깅
```python
# app/middleware/logging.py
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    # DB에 로그 저장
    log_entry = APILog(
        user_id=request.state.user_id if hasattr(request.state, 'user_id') else None,
        endpoint=request.url.path,
        method=request.method,
        status_code=response.status_code,
        response_time_ms=int(process_time)
    )
    db.add(log_entry)
    db.commit()

    return response
```

**구현 체크리스트**:
- [ ] ML 모델 훈련 및 저장
- [ ] 모델 로드 및 추론 서비스
- [ ] SSE 스트리밍 구현
- [ ] Sentry 통합
- [ ] API 로깅 미들웨어
- [ ] 대시보드 (선택)

---

## 🔄 5. 마이그레이션 전략

### 점진적 전환 단계

#### Step 1: 병렬 운영 (2주)
```
현재: widget → Netlify Functions → Gemini
추가: widget → FastAPI → Gemini (Functions 유지)
```

**방법**:
- FastAPI 서버를 별도 엔드포인트로 배포
- 위젯에서 환경변수로 선택 가능하게 구성
```javascript
const USE_FASTAPI = import.meta.env.VITE_USE_FASTAPI === 'true'
const API_BASE_URL = USE_FASTAPI
  ? 'https://api.link-coach.com'
  : '/.netlify/functions'
```

#### Step 2: FastAPI로 전환 (1개월)
```
목표: widget → FastAPI → RAG + Gemini
제거: Netlify Functions (단계적)
```

**방법**:
1. FastAPI 엔드포인트 안정화
2. 사용자 일부를 FastAPI로 라우팅 (A/B 테스트)
3. 모니터링 및 성능 비교
4. 전체 트래픽 FastAPI로 전환
5. Netlify Functions 제거

#### Step 3: 완전한 통합 (2개월)
```
최종: widget → FastAPI (PostgreSQL + ChromaDB + ML)
```

**방법**:
- RAG 파이프라인 활성화
- ML 모델 통합
- 고급 기능 배포
- Netlify Functions 완전 제거

---

## 🏗️ 6. 최종 목표 아키텍처

```
┌─────────────────────────────────────────────┐
│         Link Website (Parent Site)         │
│  - 리더십 진단 완료                          │
│  - JWT Token 생성                           │
│  - Widget 임베드                            │
└──────────────┬──────────────────────────────┘
               │ postMessage
               │ { token, userId, leadershipType }
               ↓
┌─────────────────────────────────────────────┐
│        Link-Coach Widget (React)            │
│  - 리포트 뷰어                               │
│  - 실시간 채팅                               │
└──────────────┬──────────────────────────────┘
               │ HTTPS + JWT
               ↓
┌─────────────────────────────────────────────┐
│         FastAPI Gateway (Server)            │
│  - JWT 인증 미들웨어                         │
│  - API 로깅                                  │
│  - Rate Limiting                            │
└────┬────────┬────────┬───────────┬──────────┘
     │        │        │           │
     │        │        │           ↓
     │        │        │    ┌──────────────┐
     │        │        │    │   Gemini API │
     │        │        │    │   (LLM)      │
     │        │        │    └──────────────┘
     │        │        │
     │        │        ↓
     │        │   ┌─────────────────┐
     │        │   │   ChromaDB      │
     │        │   │  (Vector Store) │
     │        │   │  - 리더십 지식   │
     │        │   │  - 코칭 가이드   │
     │        │   └─────────────────┘
     │        │           │
     │        │           ↓ RAG 검색
     │        │   ┌─────────────────┐
     │        │   │  RAG Service    │
     │        │   │  - Context 추출 │
     │        └───┤  - Prompt 구성  │
     │            └─────────────────┘
     │
     ↓
┌──────────────────────┐
│    PostgreSQL        │
│  - users             │
│  - conversations     │
│  - messages          │
│  - reports (cache)   │
│  - api_logs          │
└──────────────────────┘
```

### 데이터 플로우

#### 리포트 생성
```
1. Widget → POST /api/v1/coaching/interpretation
   { user_id, leadership_type, assessment_data }

2. FastAPI:
   - JWT 검증
   - PostgreSQL 캐시 확인
   - 캐시 없으면:
     a) ML 모델로 유형 분류 (선택)
     b) ChromaDB에서 관련 지식 검색
     c) Gemini로 리포트 생성
     d) PostgreSQL에 저장

3. Response:
   { report_id, interpretation, leadership_type }
```

#### 대화 (RAG 기반)
```
1. Widget → POST /api/v1/coaching/query
   { question, conversation_history, report_id }

2. FastAPI:
   - JWT 검증
   - 대화 히스토리 PostgreSQL 저장
   - ChromaDB RAG 검색:
     a) 질문 임베딩
     b) 유사 문서 검색 (top_k=3)
     c) Context 추출
   - Gemini 프롬프트:
     """
     Context: {rag_results}
     History: {conversation_history}
     Question: {question}
     """
   - 답변 생성

3. Response (Streaming):
   data: 답변
   data: 내용
   data: [DONE]
```

---

## ✅ 7. 즉시 실행 가능한 TODO

### 개발 환경 설정
```bash
# 1. 저장소 최신화
cd /Users/jhuny_mac/Develop/Link-Coach
git pull

# 2. Docker 서비스 시작
docker-compose up -d postgres chromadb

# 3. PostgreSQL 확인
docker exec -it linkcoach-postgres psql -U linkcoach_user -d linkcoach
# \dt  # 테이블 목록
# \q   # 종료

# 4. ChromaDB 확인
curl http://localhost:8001/api/v1/heartbeat

# 5. FastAPI 서버 실행
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/init_database.py  # 테이블 생성
uvicorn app.main:app --reload --port 8000

# 6. 별도 터미널에서 위젯 실행
cd widget
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
npm run dev

# 7. 테스트
# 브라우저: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

### 첫 번째 마일스톤 체크리스트

#### Week 1: 인프라 구축
- [ ] Docker Compose 실행 확인
- [ ] PostgreSQL 스키마 생성
- [ ] FastAPI 서버 로컬 실행
- [ ] Health check 엔드포인트 테스트
- [ ] JWT 인증 로직 구현
- [ ] 위젯 → FastAPI 연결 테스트

#### Week 2: 기본 기능 구현
- [ ] 대화 저장 API (`POST /api/v1/conversations`)
- [ ] 메시지 저장 API (`POST /api/v1/messages`)
- [ ] 대화 조회 API (`GET /api/v1/conversations/{id}`)
- [ ] 리포트 캐싱 로직
- [ ] API 로깅 미들웨어
- [ ] 에러 핸들링 개선

#### Week 3-4: RAG 파이프라인 (선택)
- [ ] 지식 베이스 문서 작성
- [ ] ChromaDB 임베딩 스크립트
- [ ] RAG 검색 서비스
- [ ] Gemini 프롬프트 개선
- [ ] 통합 테스트

---

## 📝 8. 참고 문서

### 프로젝트 문서
- `README.md`: 전체 프로젝트 개요 및 아키텍처
- `.claude/CLAUDE.md`: 개발 가이드 (프로젝트 루트)
- `widget/CLAUDE.md`: 위젯 개발 가이드
- `docker-compose.yml`: 인프라 구성

### 주요 파일 위치
```
Link-Coach/
├── server/
│   ├── app/
│   │   ├── main.py              # FastAPI 엔트리포인트 ✅
│   │   ├── config.py            # 설정 관리 ✅
│   │   ├── core/
│   │   │   └── security.py      # JWT 인증 (수정 필요)
│   │   ├── api/v1/endpoints/
│   │   │   └── coaching.py      # 코칭 API (수정 필요)
│   │   ├── services/
│   │   │   ├── vector_db.py     # ChromaDB ✅
│   │   │   └── ml_model.py      # ML 모델 ✅
│   │   └── models/
│   │       ├── database.py      # ORM 모델 (수정 필요)
│   │       └── schemas.py       # Pydantic 스키마 ✅
│   └── scripts/
│       ├── init_database.py     # DB 초기화 ✅
│       └── init_chroma_data.py  # ChromaDB 임베딩 ✅
├── widget/
│   ├── netlify/functions/
│   │   ├── chat.cjs             # 현재 운영 중 ✅
│   │   └── generate.cjs         # 미사용
│   └── src/
│       └── services/api.js      # API 클라이언트 (수정 필요)
└── docker-compose.yml           # 인프라 ✅
```

### 환경변수 (.env)
```env
# Database
POSTGRES_DB=linkcoach
POSTGRES_USER=linkcoach_user
POSTGRES_PASSWORD=linkcoach_pass
DATABASE_URL=postgresql://linkcoach_user:linkcoach_pass@localhost:5432/linkcoach

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8001

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key

# App
APP_ENV=development
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Widget (개발 시)
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🎯 9. 성공 지표

### Phase 1 완료 기준
- [ ] FastAPI 서버가 프로덕션에서 정상 작동
- [ ] PostgreSQL에 대화 저장 및 조회 가능
- [ ] JWT 인증으로 모든 API 보호
- [ ] 위젯이 FastAPI와 통신 (Netlify Functions 제거)

### Phase 2 완료 기준
- [ ] ChromaDB에 최소 100개 문서 임베딩
- [ ] RAG 검색 결과의 관련성 80% 이상
- [ ] 리포트 캐싱으로 응답 시간 50% 감소
- [ ] Gemini API 호출 비용 30% 감소

### Phase 3 완료 기준
- [ ] ML 모델 정확도 85% 이상
- [ ] SSE 스트리밍 응답 구현
- [ ] Sentry에서 에러율 1% 미만
- [ ] API 평균 응답 시간 500ms 이하

---

## 💡 10. 추가 고려사항

### 보안
- [ ] Rate Limiting (IP/사용자당)
- [ ] API 키 로테이션
- [ ] SQL Injection 방어 (ORM 사용)
- [ ] XSS 방어 (sanitization)
- [ ] HTTPS 강제 (프로덕션)

### 성능
- [ ] DB 쿼리 최적화 (인덱스)
- [ ] Redis 캐싱 (선택)
- [ ] CDN 사용 (정적 파일)
- [ ] Lazy loading (위젯)

### 비용 최적화
- [ ] Gemini API 호출 최소화 (캐싱)
- [ ] PostgreSQL 쿼리 최적화
- [ ] ChromaDB 임베딩 재사용
- [ ] 서버 리소스 모니터링

### 사용자 경험
- [ ] 응답 속도 향상 (스트리밍)
- [ ] 오프라인 모드 (선택)
- [ ] 다국어 지원 (i18n)
- [ ] 접근성 (a11y)

---

## 📞 11. 연락처 및 이슈 트래킹

- **GitHub**: https://github.com/Junghoon-83/Link-Coach
- **Production**: https://link-coach.netlify.app
- **이슈 보고**: GitHub Issues

---

**마지막 업데이트**: 2025-10-10
**검토자**: Claude Code
**다음 검토 예정**: Phase 1 완료 후
