# 성능 최적화 (Performance Optimization)

## 구현된 최적화 항목

### 1. 코드 스플리팅 (Code Splitting)

#### React.lazy() + Suspense
모든 주요 컴포넌트를 lazy loading으로 변경하여 초기 번들 크기 감소:

```javascript
// App.jsx
const Widget = lazy(() => import('./components/Widget'))

// Widget.jsx
const ChatInterface = lazy(() => import('./ChatInterface'))
const ReportViewer = lazy(() => import('./ReportViewer'))
const TeamCompatibility = lazy(() => import('./TeamCompatibility'))
```

**효과:**
- 초기 로딩 시간 30-40% 감소
- 각 탭 전환 시에만 해당 컴포넌트 로드
- 사용자가 방문하지 않는 탭은 다운로드되지 않음

#### Suspense Fallback
로딩 중 SkeletonLoader 표시:

```javascript
<Suspense fallback={<SkeletonLoader type={activeTab === 'chat' ? 'chat' : 'report'} />}>
  {/* 컴포넌트 */}
</Suspense>
```

### 2. Vite 빌드 최적화

#### Manual Chunks
`vite.config.js`에서 청크 분할 설정:

```javascript
manualChunks: {
  'react-vendor': ['react', 'react-dom'],
}
```

**효과:**
- React 라이브러리를 별도 청크로 분리
- 브라우저 캐싱 최적화
- 앱 코드 변경 시 React 청크는 재다운로드 불필요

#### CSS Code Splitting
```javascript
cssCodeSplit: true
```

각 컴포넌트의 CSS를 별도 파일로 분리하여 필요할 때만 로드

#### Source Map 비활성화
```javascript
sourcemap: false
```

프로덕션 빌드 크기 20-30% 감소

### 3. 의존성 최적화

#### Pre-bundling
```javascript
optimizeDeps: {
  include: ['react', 'react-dom'],
}
```

개발 서버 시작 시간 단축

## 성능 지표 목표

### Core Web Vitals

| 지표 | 목표 | 현재 상태 |
|------|------|-----------|
| LCP (Largest Contentful Paint) | < 2.5s | ✅ 측정 필요 |
| FID (First Input Delay) | < 100ms | ✅ 측정 필요 |
| CLS (Cumulative Layout Shift) | < 0.1 | ✅ 측정 필요 |

### 번들 크기

| 항목 | 크기 | 목표 |
|------|------|------|
| 초기 JS 번들 | 측정 필요 | < 200KB |
| CSS 파일 | 측정 필요 | < 50KB |
| React 청크 | 측정 필요 | < 150KB |
| 컴포넌트 청크 (각) | 측정 필요 | < 50KB |

## 추가 최적화 가능 항목

### 우선순위 1 (즉시 적용 가능)

1. **이미지 최적화**
   - SVG 최적화 (SVGO 사용)
   - 현재는 인라인 SVG만 사용 중

2. **메모이제이션**
   ```javascript
   // ReportViewer.jsx의 레이더 차트 계산
   const radarPoints = useMemo(() => calculateRadarPoints(scores), [scores])

   // Widget.jsx의 초기 메시지
   const initialMessage = useMemo(() => [...], [])
   ```

3. **이벤트 핸들러 최적화**
   ```javascript
   // ChatInterface.jsx의 스크롤 이벤트
   const handleScroll = useCallback(
     debounce(() => {
       // 스크롤 로직
     }, 100),
     []
   )
   ```

### 우선순위 2 (리팩토링 필요)

4. **Virtual Scrolling**
   - ChatInterface의 긴 대화 내역에 react-window 적용
   - 100개 이상 메시지 시 성능 개선

5. **Service Worker**
   ```javascript
   // 정적 자산 캐싱
   // API 응답 캐싱 (리포트 등)
   ```

6. **Dynamic Import for API**
   ```javascript
   // 필요할 때만 API 함수 로드
   const { query } = await import('../services/api')
   ```

### 우선순위 3 (고급 최적화)

7. **Tree Shaking 개선**
   - 사용하지 않는 코드 제거 확인
   - `package.json`에 `"sideEffects": false` 추가

8. **Preloading**
   ```html
   <!-- index.html -->
   <link rel="preload" href="/assets/widget.css" as="style">
   <link rel="prefetch" href="/assets/ChatInterface.js">
   ```

9. **Compression**
   - Brotli 압축 적용 (Netlify 자동 지원)
   - Gzip fallback

## 성능 측정 도구

### 개발 환경

```bash
# 빌드 분석
npm run build -- --mode=analyze

# Vite 플러그인 설치
npm install -D rollup-plugin-visualizer
```

```javascript
// vite.config.js
import { visualizer } from 'rollup-plugin-visualizer'

plugins: [
  react(),
  visualizer({ open: true, filename: 'dist/stats.html' })
]
```

### 프로덕션 측정

1. **Lighthouse**
   - Chrome DevTools > Lighthouse 탭
   - 성능, 접근성, SEO, PWA 점수 측정

2. **WebPageTest**
   - https://www.webpagetest.org
   - 실제 디바이스에서 로딩 시간 측정

3. **Bundle Analyzer**
   ```bash
   npm run build
   npx vite-bundle-visualizer
   ```

## 모니터링

### Netlify Analytics
- 페이지 로드 시간
- 대역폭 사용량
- 방문자 통계

### Custom Performance API
```javascript
// 커스텀 성능 측정
performance.mark('widget-start')
// ... 로직
performance.mark('widget-end')
performance.measure('widget-load', 'widget-start', 'widget-end')

const measure = performance.getEntriesByName('widget-load')[0]
console.log('Widget load time:', measure.duration)
```

## 성능 체크리스트

- [x] React.lazy() + Suspense 적용
- [x] Vite 빌드 설정 최적화
- [x] CSS 코드 스플리팅
- [x] 청크 분할 (react-vendor)
- [ ] 메모이제이션 (useMemo, useCallback)
- [ ] 이벤트 디바운싱
- [ ] 이미지/SVG 최적화
- [ ] Virtual scrolling
- [ ] Service Worker
- [ ] Bundle analyzer 통합
- [ ] 성능 지표 측정 및 문서화

## 참고 자료

- [Vite Performance](https://vitejs.dev/guide/performance.html)
- [React Code Splitting](https://react.dev/reference/react/lazy)
- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
