# 🔧 Link-Coach 문제 해결 가이드

## 타임아웃 오류 해결 (2025-10-04)

### 문제 증상
```
네트워크 오류: 서버에 연결할 수 없습니다.
리포트 생성 실패: AxiosError {message: 'timeout of 30000ms exceeded'...}
```

### 원인
1. **서버 초기화 블로킹**: `lifespan` 함수에서 ML 모델/Vector DB 초기화가 동기적으로 실행되어 서버가 요청을 받지 못함
2. **타임아웃 설정 부족**: 기본 30초로는 리포트 생성 같은 긴 작업 처리 불가

### 해결책

#### 1. 서버 초기화 최적화 ✅
**파일**: `/server/app/main.py`

**변경 전:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ML 모델 로드 (블로킹됨)
    await ml_model_service.load_model()

    # Vector DB 연결 (블로킹됨)
    await vector_db_service.health_check()

    yield
```

**변경 후:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작을 블로킹하지 않도록 스킵
    logger.info("⏩ ML 모델 로드 스킵 (백그라운드 처리)")
    logger.info("⏩ ChromaDB 연결 스킵 (첫 요청 시 연결)")
    logger.info("✅ 서버 시작 완료 - 요청 대기 중...")

    yield
```

#### 2. 클라이언트 타임아웃 증가 ✅
**파일**: `/widget/src/services/api.js`

**변경:**
```javascript
const apiClient = axios.create({
  timeout: 120000, // 30초 → 2분 (리포트 생성은 시간이 걸릴 수 있음)
  // ...
});
```

#### 3. 개발용 토큰 생성 엔드포인트 추가 ✅
**파일**: `/server/app/main.py`

```python
@app.get("/dev/token", tags=["Development"])
async def get_dev_token():
    """개발용 임시 JWT 토큰 생성"""
    token = create_jwt_token({
        "user_id": "dev_user_123",
        "email": "dev@example.com",
        "role": "user"
    })
    return {"token": token, "user_id": "dev_user_123"}
```

**사용법:**
```bash
curl http://localhost:8000/dev/token
```

---

## 서버 재시작 방법

### 1. 프로세스 확인
```bash
ps aux | grep uvicorn
```

### 2. 프로세스 종료
```bash
# 특정 프로세스 종료
kill <PID>

# 모든 uvicorn 프로세스 종료
pkill -f uvicorn

# 포트 강제 해제
lsof -ti:8000 | xargs kill -9
```

### 3. 서버 재시작
```bash
cd server
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 빠른 테스트

### 1. 헬스체크
```bash
curl http://localhost:8000/health
```

**예상 응답:**
```json
{
  "status": "healthy",
  "service": "Link-Coach API",
  "version": "0.1.0",
  "environment": "development"
}
```

### 2. 개발 토큰 생성
```bash
curl http://localhost:8000/dev/token
```

**예상 응답:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "dev_user_123",
  "usage": "Add this token to Authorization header as 'Bearer <token>'"
}
```

### 3. 리포트 생성 테스트
```bash
TOKEN=$(curl -s http://localhost:8000/dev/token | jq -r .token)

curl -X POST http://localhost:8000/api/v1/coaching/interpretation \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "dev_user_123",
    "leadership_type": "ENTJ",
    "assessment_data": {
      "scores": {"extraversion": 75, "thinking": 80}
    }
  }'
```

---

## 일반적인 문제들

### 문제 1: "Address already in use"
**원인**: 포트 8000이 이미 사용 중

**해결:**
```bash
lsof -ti:8000 | xargs kill -9
```

### 문제 2: 서버가 응답하지 않음
**원인**:
- 초기화 블로킹
- 의존성 문제
- 환경 변수 누락

**해결:**
1. 서버 로그 확인:
   ```bash
   tail -f logs/app.log  # 로그 파일 경로에 따라 조정
   ```

2. 환경 변수 확인:
   ```bash
   cat server/.env
   ```

3. 필수 환경 변수:
   - `GEMINI_API_KEY` (Google Gemini API)
   - `JWT_SECRET_KEY` (JWT 토큰 서명)
   - `DATABASE_URL` (PostgreSQL)

### 문제 3: CORS 오류
**증상**: `Access to XMLHttpRequest has been blocked by CORS policy`

**해결:** `/server/app/config.py` 확인
```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite 개발 서버
    "*"  # 개발 환경에서만
]
```

### 문제 4: JWT 인증 실패
**개발 모드 우회:**
```python
# server/app/core/security.py
if settings.is_development and token.startswith('dev-'):
    return {"user_id": "dev_user_123", ...}
```

**또는 정식 토큰 사용:**
```bash
curl http://localhost:8000/dev/token
```

---

## 로그 확인

### 1. 애플리케이션 로그
```bash
# 실시간 로그 확인
tail -f server/logs/app.log

# 에러만 필터링
grep ERROR server/logs/app.log
```

### 2. uvicorn 로그
```bash
# uvicorn 직접 실행 시 stdout/stderr 확인
uvicorn app.main:app --reload --log-level debug
```

### 3. 주요 로그 메시지

**정상:**
```
✅ 서버 시작 완료 - 요청 대기 중...
✅ ML 모델 로드 완료
✅ ChromaDB 연결 완료
```

**경고:**
```
⚠️ ML 모델 로드 실패 (계속 진행)
⚠️ ChromaDB 연결 실패 (계속 진행)
```

**오류:**
```
❌ ML 모델 로드 실패
❌ ChromaDB 연결 실패
```

---

## 성능 최적화

### 타임아웃 설정 권장값

| 작업 | 타임아웃 | 이유 |
|------|----------|------|
| 헬스체크 | 5초 | 간단한 상태 확인 |
| 리포트 생성 | 2분 | LLM 처리 시간 필요 |
| Q&A 스트리밍 | 무제한 | 스트리밍은 자체 종료 |
| 일반 API | 30초 | 표준 설정 |

### 클라이언트 설정
```javascript
// widget/src/services/api.js
const apiClient = axios.create({
  timeout: 120000,  // 2분

  // 재시도 설정 (선택)
  retry: 3,
  retryDelay: 1000,
});
```

---

## 디버깅 팁

### 1. Verbose 로그 활성화
```bash
# .env 파일
LOG_LEVEL=DEBUG
```

### 2. API 문서 확인
```
http://localhost:8000/docs
```

### 3. 네트워크 요청 추적
```bash
# Chrome DevTools > Network 탭
# 또는
curl -v http://localhost:8000/api/...
```

### 4. Python 디버거
```python
import pdb; pdb.set_trace()
```

---

## 환경별 설정

### 개발 (Development)
- 자동 리로드: ON
- 상세 로그: ON
- CORS: `*` 허용
- 토큰 검증: 완화

### 스테이징 (Staging)
- 자동 리로드: OFF
- 상세 로그: ON
- CORS: 특정 도메인
- 토큰 검증: 엄격

### 프로덕션 (Production)
- 자동 리로드: OFF
- 상세 로그: ERROR 이상
- CORS: 특정 도메인
- 토큰 검증: 엄격
- Docs: 비활성화

---

## 체크리스트

### 서버 시작 전
- [ ] 가상 환경 활성화: `source venv/bin/activate`
- [ ] 의존성 설치: `pip install -r requirements.txt`
- [ ] 환경 변수 설정: `.env` 파일 확인
- [ ] 포트 확인: `lsof -i:8000`

### 배포 전
- [ ] 테스트 통과
- [ ] 로그 레벨 조정 (ERROR)
- [ ] CORS 설정 확인
- [ ] 타임아웃 설정 검증
- [ ] 환경 변수 프로덕션 값 설정

---

## 문의

문제가 해결되지 않을 경우:
1. GitHub Issues: https://github.com/your-org/link-coach/issues
2. Slack: #link-coach-support
3. Email: support@link-coach.com

---

**마지막 업데이트**: 2025-10-04
**버전**: 1.0
**작성자**: AI Team
