# 배포 가이드 (Deployment Guide)

## 최근 배포 정보

### 프로덕션 배포 (2025-10-10)

**배포 URL:** https://link-coach.netlify.app

**빌드 결과:**
- ✅ 빌드 시간: 401ms
- ✅ 총 89개 모듈 변환
- ✅ Functions: chat.cjs, generate.cjs

**번들 크기 (gzip):**
```
index.html                    0.34 kB
index.css                     6.80 kB
react-vendor.js              45.26 kB
index.js                     17.47 kB
ChatInterface.js              1.90 kB
TeamCompatibility.js          2.69 kB
Widget.js                     2.19 kB
ReportViewer.js               2.56 kB
────────────────────────────────────
총 gzip 크기                ~79 kB
```

## 배포된 기능

### 1. 프론트엔드
- ✅ React 18 + Vite 애플리케이션
- ✅ 코드 스플리팅 (4개 컴포넌트 lazy loading)
- ✅ ErrorBoundary (에러 처리)
- ✅ SkeletonLoader (로딩 UX)
- ✅ 접근성 개선 (ARIA, 키보드 네비게이션)
- ✅ 반응형 디자인

### 2. Netlify Functions
- ✅ `/.netlify/functions/chat` - AI 채팅 (Gemini 2.5 Flash)
- ✅ `/.netlify/functions/generate` - 리포트 생성 (Gemini 2.0 Flash Exp)

### 3. 임베딩 SDK
- ✅ `/embed.js` - 외부 사이트 통합 스크립트
- ✅ `/example.html` - 데모 페이지

## 배포 전 체크리스트

### 로컬 테스트
- [x] `npm run dev` 실행 확인
- [x] `npm run lint` 에러 없음
- [x] `npm run build` 성공
- [x] 모든 컴포넌트 정상 작동
- [x] API 함수 통신 정상

### 코드 품질
- [x] ESLint 0 에러, 0 경고
- [x] 사용하지 않는 코드 제거
- [x] 콘솔 에러 없음
- [x] PropTypes 검증 (또는 TypeScript)

### 성능
- [x] 번들 크기 < 200KB
- [x] 코드 스플리팅 적용
- [x] Lazy loading 적용
- [x] CSS 최적화

### 접근성
- [x] ARIA 속성 추가
- [x] 키보드 네비게이션 지원
- [x] Skip navigation 링크
- [x] 스크린 리더 호환성

### 보안
- [x] 환경 변수 설정 (GEMINI_API_KEY)
- [x] Origin 검증 (postMessage)
- [x] HTTPS 강제
- [x] 민감 정보 제외

## 배포 단계

### 1. 프리뷰 배포 (테스트용)

```bash
# 로컬 빌드 확인
npm run build

# Netlify 프리뷰 배포
netlify deploy

# 프리뷰 URL에서 테스트
# https://[unique-id]--link-coach.netlify.app
```

### 2. 프로덕션 배포

```bash
# 프로덕션 배포
netlify deploy --prod

# 배포 완료 후 확인
# https://link-coach.netlify.app
```

### 3. 배포 후 확인

- [ ] 메인 URL 접속 확인
- [ ] 리포트 탭 정상 표시
- [ ] 팀 궁합 탭 정상 작동
- [ ] AI 채팅 응답 확인
- [ ] 모바일 반응형 확인
- [ ] 에러 바운더리 테스트 (의도적 에러 발생)

## 환경 변수 설정

### Netlify Dashboard에서 설정 필요

```
GEMINI_API_KEY=your-google-gemini-api-key
```

**설정 방법:**
1. Netlify Dashboard → Site settings → Environment variables
2. "Add a variable" 클릭
3. Key: `GEMINI_API_KEY`, Value: `[your-api-key]`
4. 저장 후 재배포

**또는 CLI 사용:**
```bash
netlify env:set GEMINI_API_KEY "your-api-key"
netlify deploy --prod
```

## 배포 문제 해결

### 빌드 실패

**증상:** Netlify 빌드가 실패함

**해결:**
1. 로컬에서 `npm run build` 실행 확인
2. package.json의 build 스크립트 확인
3. Node.js 버전 호환성 확인 (18.x 권장)

```toml
# netlify.toml
[build.environment]
  NODE_VERSION = "18"
```

### Functions 에러

**증상:** API 호출 시 500 에러

**해결:**
1. Netlify Dashboard → Functions → Logs 확인
2. 환경 변수 설정 확인
3. Functions 로그 확인:
```bash
netlify functions:list
netlify logs:function chat
```

### CORS 에러

**증상:** 프론트엔드에서 API 호출 실패

**해결:**
1. Functions에서 CORS 헤더 설정 확인
2. `Access-Control-Allow-Origin` 올바르게 설정
3. Netlify Functions는 기본적으로 CORS 지원

### 느린 로딩 속도

**해결:**
1. Netlify Analytics로 성능 모니터링
2. 번들 크기 확인: `npm run build`
3. 이미지 최적화 (SVG 압축)
4. CDN 캐싱 확인

## 성능 모니터링

### Netlify Analytics

Netlify Dashboard에서 확인:
- 페이지 로드 시간
- 대역폭 사용량
- 방문자 통계
- Functions 호출 횟수

### Google Lighthouse

```bash
# Chrome DevTools에서
# Lighthouse → Performance 탭 → Generate report
```

**목표 점수:**
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 90
- SEO: > 80

### Bundle Analyzer

```bash
# 번들 분석 설치
npm install -D rollup-plugin-visualizer

# vite.config.js에 추가 후 빌드
npm run build

# dist/stats.html 확인
```

## 롤백 (Rollback)

### 이전 버전으로 복구

**Netlify Dashboard 사용:**
1. Deploys 탭 이동
2. 이전 배포 선택
3. "Publish deploy" 클릭

**CLI 사용:**
```bash
# 배포 목록 확인
netlify deploy:list

# 특정 배포로 롤백
netlify deploy:publish [deploy-id]
```

## CI/CD 설정 (선택)

### GitHub Actions 예제

```yaml
# .github/workflows/deploy.yml
name: Deploy to Netlify

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lint
      - run: npm run build
      - uses: netlify/actions/cli@master
        with:
          args: deploy --prod
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

## 도메인 설정

### 커스텀 도메인 연결

```bash
# 도메인 추가
netlify domains:add yourdomain.com

# DNS 설정 확인
netlify dns:setup
```

**수동 DNS 설정:**
- A 레코드: `75.2.60.5`
- CNAME: `link-coach.netlify.app`

## 모니터링 및 알림

### Netlify Notifications

Netlify Dashboard → Site settings → Build & deploy → Deploy notifications:
- Deploy started
- Deploy succeeded
- Deploy failed
- Form submission (해당 시)

### Slack/Discord 통합

```bash
# Webhook URL 설정
netlify notifications:create \
  --type deploy-succeeded \
  --event deploy-building \
  --slack https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## 참고 자료

- [Netlify Docs](https://docs.netlify.com/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)
- [React Production Build](https://react.dev/learn/start-a-new-react-project#deploying-to-production)
- [Web Vitals](https://web.dev/vitals/)

## 배포 히스토리

### 2025-10-10 (최신)
- ✅ 에러 바운더리 추가
- ✅ 스켈레톤 로더 구현
- ✅ 접근성 개선 (ARIA, 키보드)
- ✅ 성능 최적화 (lazy loading, code splitting)
- ✅ 임베딩 SDK 추가
- ✅ ESLint 설정 및 코드 정리
- 번들 크기: 79KB (gzip)
- 빌드 시간: 401ms

### 이전 배포
- 초기 구현 (리더십 분석, AI 채팅, 팀 궁합)
- Gemini API 통합
- Netlify Functions 구현
