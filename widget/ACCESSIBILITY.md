# 접근성 (Accessibility) 개선 사항

## 현재 구현된 접근성 기능

### 1. Semantic HTML & ARIA
- ✅ `role="tab"` 및 `aria-selected` 속성 사용 (Widget.jsx 탭)
- ✅ `role="log"`, `aria-live="polite"` 사용 (ChatInterface 메시지)
- ✅ `aria-label` 제공 (입력 필드, 버튼)
- ✅ `aria-describedby` 사용 (ChatInterface 입력 안내)

### 2. 키보드 네비게이션
- ✅ 모든 인터랙티브 요소는 `<button>` 태그 사용
- ✅ Enter 키로 메시지 전송 (ChatInterface)
- ✅ Shift+Enter로 줄바꿈 지원

### 3. 시각적 피드백
- ✅ 포커스 상태 시각적 표시 (`:focus` 스타일)
- ✅ 비활성화 상태 명확히 표시 (`:disabled` 스타일)
- ✅ 로딩 상태 애니메이션 및 텍스트 제공

### 4. 스크린 리더 지원
- ✅ `.sr-only` 클래스 구현
- ✅ 의미 있는 alt 텍스트 (SVG 아이콘에는 `aria-label` 필요)

## 추가 개선 필요 사항

### 우선순위 1 (필수)

1. **SVG 아이콘 접근성**
   ```jsx
   // 현재
   <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
     <path d="..." />
   </svg>

   // 개선
   <svg viewBox="0 0 24 24" aria-label="분석 리포트" role="img">
     <path d="..." />
   </svg>
   ```

2. **폼 레이블 연결**
   ```jsx
   // ChatInterface.jsx
   <label htmlFor="chat-input" className="sr-only">
     메시지 입력
   </label>
   <textarea
     id="chat-input"
     className="chat-input"
     aria-label="메시지 입력"
   />
   ```

3. **Skip Navigation 링크**
   ```jsx
   <a href="#main-content" className="sr-only">
     메인 콘텐츠로 건너뛰기
   </a>
   <main id="main-content">
     {/* 콘텐츠 */}
   </main>
   ```

### 우선순위 2 (권장)

4. **색상 대비 비율**
   - WCAG AA 기준: 최소 4.5:1 (일반 텍스트)
   - WCAG AAA 기준: 최소 7:1 (일반 텍스트)
   - 현재 보라색 배경의 흰색 텍스트는 충분한 대비 보유
   - 회색 텍스트 (`var(--primary-500)`)는 확인 필요

5. **포커스 인디케이터 개선**
   ```css
   .tab-btn:focus-visible {
     outline: 3px solid var(--accent-500);
     outline-offset: 2px;
   }

   .chat-input:focus-visible {
     outline: 3px solid var(--accent-500);
     outline-offset: 2px;
   }
   ```

6. **에러 메시지 ARIA 알림**
   ```jsx
   <div role="alert" aria-live="assertive">
     {error && <p>{error}</p>}
   </div>
   ```

### 우선순위 3 (선택)

7. **Reduced Motion 지원**
   ```css
   @media (prefers-reduced-motion: reduce) {
     * {
       animation-duration: 0.01ms !important;
       animation-iteration-count: 1 !important;
       transition-duration: 0.01ms !important;
     }
   }
   ```

8. **다크 모드 지원**
   ```css
   @media (prefers-color-scheme: dark) {
     :root {
       --primary-50: #1e293b;
       --primary-900: #f8fafc;
       /* ... */
     }
   }
   ```

9. **언어 속성**
   ```html
   <html lang="ko">
   ```

## 테스트 도구

### 자동화 도구
- [ ] [axe DevTools](https://www.deque.com/axe/devtools/)
- [ ] [Lighthouse Accessibility](https://developers.google.com/web/tools/lighthouse)
- [ ] [WAVE](https://wave.webaim.org/)

### 수동 테스트
- [ ] 키보드만으로 전체 기능 사용 가능한지 확인
- [ ] 스크린 리더 (NVDA, JAWS, VoiceOver) 테스트
- [ ] 색상 대비 비율 검사 (WebAIM Contrast Checker)
- [ ] 150%, 200% 확대 시 레이아웃 확인

## 구현 계획

### Phase 1: 즉시 적용 가능 (1-2시간)
- [ ] SVG에 `aria-label` 추가
- [ ] Skip navigation 링크
- [ ] Focus-visible 스타일 개선
- [ ] Reduced motion CSS

### Phase 2: 리팩토링 필요 (1-2일)
- [ ] 폼 레이블 시스템 개선
- [ ] 에러 메시지 ARIA 알림
- [ ] 색상 대비 개선
- [ ] 자동화 테스트 통합

### Phase 3: 고급 기능 (1주)
- [ ] 다크 모드 지원
- [ ] 접근성 설정 패널
- [ ] 다국어 지원 (i18n)

## 참고 자료

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)
- [React Accessibility](https://react.dev/learn/accessibility)
