# Link-Coach Widget 임베딩 가이드

Link-Coach 위젯을 외부 웹사이트에 통합하는 방법을 설명합니다.

## 빠른 시작

### 방법 1: JavaScript API 사용 (권장)

가장 유연하고 강력한 방법입니다.

```html
<!DOCTYPE html>
<html>
<head>
  <title>My Website</title>
</head>
<body>
  <h1>Welcome to My Site</h1>

  <!-- Link-Coach 위젯 스크립트 -->
  <script src="https://link-coach.netlify.app/embed.js"></script>
  <script>
    // 사용자 로그인 후 위젯 초기화
    LinkCoach.init({
      token: 'YOUR_JWT_TOKEN',
      userId: 'user_12345',
      leadershipType: '개별비전형',
      assessmentData: {
        scores: {
          extraversion: 75,
          thinking: 80,
          judging: 70
        }
      }
    });
  </script>
</body>
</html>
```

### 방법 2: 자동 초기화 (간단한 통합)

HTML 속성만으로 위젯을 초기화합니다.

```html
<script
  src="https://link-coach.netlify.app/embed.js"
  data-auto-init="true"
  data-token="YOUR_JWT_TOKEN"
  data-user-id="user_12345"
  data-leadership-type="개별비전형"
  data-position="bottom-right"
></script>
```

### 방법 3: iframe 직접 삽입 (커스터마이징 필요시)

완전한 제어가 필요한 경우 iframe을 직접 사용합니다.

```html
<iframe
  id="link-coach-widget"
  src="https://link-coach.netlify.app"
  width="400"
  height="600"
  style="border: none;"
></iframe>

<script>
  const iframe = document.getElementById('link-coach-widget');

  // 위젯이 준비될 때까지 대기
  window.addEventListener('message', (event) => {
    if (event.data.type === 'WIDGET_READY') {
      // 초기화 데이터 전송
      iframe.contentWindow.postMessage({
        type: 'INIT_WIDGET',
        data: {
          token: 'YOUR_JWT_TOKEN',
          userId: 'user_12345',
          leadershipType: '개별비전형'
        }
      }, 'https://link-coach.netlify.app');
    }
  });
</script>
```

## API 레퍼런스

### `LinkCoach.init(options)`

위젯을 초기화합니다.

#### Parameters

| 이름 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `token` | string | ✅ | JWT 인증 토큰 |
| `userId` | string | ✅ | 사용자 고유 ID |
| `leadershipType` | string | ✅ | 리더십 유형 (예: '개별비전형') |
| `assessmentData` | object | ❌ | 평가 데이터 (점수 등) |
| `container` | string | ❌ | 위젯을 삽입할 DOM 셀렉터 (기본: body) |
| `widgetUrl` | string | ❌ | 위젯 URL (기본: 프로덕션 URL) |
| `width` | string | ❌ | 위젯 너비 (기본: '400px') |
| `height` | string | ❌ | 위젯 높이 (기본: '600px') |
| `position` | string | ❌ | 위치 ('bottom-right', 'bottom-left', 'custom') |
| `zIndex` | number | ❌ | z-index 값 (기본: 9999) |

#### Example

```javascript
LinkCoach.init({
  token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
  userId: 'user_jiyoung',
  leadershipType: '개별비전형',
  assessmentData: {
    scores: {
      extraversion: 75,
      thinking: 80,
      judging: 70
    }
  },
  position: 'bottom-right',
  width: '450px',
  height: '700px'
});
```

### `LinkCoach.show()`

숨겨진 위젯을 표시합니다.

```javascript
LinkCoach.show();
```

### `LinkCoach.hide()`

위젯을 숨깁니다 (DOM에서 제거하지 않음).

```javascript
LinkCoach.hide();
```

### `LinkCoach.toggle()`

위젯 표시/숨김을 토글합니다.

```javascript
LinkCoach.toggle();
```

### `LinkCoach.close()`

위젯을 완전히 닫고 DOM에서 제거합니다.

```javascript
LinkCoach.close();
```

### `LinkCoach.updateUser(userData)`

사용자 데이터를 업데이트합니다.

```javascript
LinkCoach.updateUser({
  userId: 'user_new',
  leadershipType: '팀화합형',
  assessmentData: { /* 새로운 데이터 */ }
});
```

## 고급 사용법

### 특정 컨테이너에 위젯 삽입

```html
<div id="coaching-section">
  <h2>AI 코칭</h2>
  <div id="widget-container"></div>
</div>

<script>
  LinkCoach.init({
    token: 'YOUR_TOKEN',
    userId: 'user_123',
    leadershipType: '개별비전형',
    container: '#widget-container',
    position: 'custom' // fixed 대신 relative 위치
  });
</script>
```

### 동적 위젯 로딩

사용자가 버튼을 클릭할 때만 위젯을 로드합니다.

```html
<button id="open-coach">AI 코치 열기</button>

<script src="https://link-coach.netlify.app/embed.js"></script>
<script>
  document.getElementById('open-coach').addEventListener('click', function() {
    if (!LinkCoach.isInitialized) {
      LinkCoach.init({
        token: getUserToken(), // 동적으로 토큰 가져오기
        userId: getCurrentUserId(),
        leadershipType: getUserLeadershipType()
      });
    } else {
      LinkCoach.show();
    }
  });
</script>
```

### React 애플리케이션 통합

```jsx
import { useEffect } from 'react';

function CoachingWidget({ user }) {
  useEffect(() => {
    // 스크립트 로드
    const script = document.createElement('script');
    script.src = 'https://link-coach.netlify.app/embed.js';
    script.async = true;

    script.onload = () => {
      window.LinkCoach.init({
        token: user.token,
        userId: user.id,
        leadershipType: user.leadershipType,
        container: '#link-coach-container'
      });
    };

    document.body.appendChild(script);

    // 클린업
    return () => {
      if (window.LinkCoach) {
        window.LinkCoach.close();
      }
      document.body.removeChild(script);
    };
  }, [user]);

  return <div id="link-coach-container"></div>;
}
```

### Vue.js 애플리케이션 통합

```vue
<template>
  <div id="link-coach-container"></div>
</template>

<script>
export default {
  name: 'CoachingWidget',
  props: ['user'],
  mounted() {
    this.loadWidget();
  },
  beforeUnmount() {
    if (window.LinkCoach) {
      window.LinkCoach.close();
    }
  },
  methods: {
    loadWidget() {
      const script = document.createElement('script');
      script.src = 'https://link-coach.netlify.app/embed.js';
      script.onload = () => {
        window.LinkCoach.init({
          token: this.user.token,
          userId: this.user.id,
          leadershipType: this.user.leadershipType,
          container: '#link-coach-container'
        });
      };
      document.body.appendChild(script);
    }
  }
}
</script>
```

## 보안 고려사항

### JWT 토큰 관리

1. **서버에서 토큰 생성**: 클라이언트에서 토큰을 생성하지 마세요
2. **짧은 만료 시간**: 토큰 만료 시간을 짧게 설정 (예: 1시간)
3. **HTTPS 사용**: 프로덕션에서는 반드시 HTTPS 사용
4. **토큰 갱신**: 만료된 토큰을 자동으로 갱신하는 로직 구현

```javascript
// 토큰 갱신 예제
async function refreshToken() {
  const response = await fetch('/api/refresh-token', {
    method: 'POST',
    credentials: 'include'
  });
  const { token } = await response.json();
  return token;
}

// 위젯 초기화 with 토큰 갱신
async function initWidget() {
  const token = await refreshToken();
  LinkCoach.init({
    token: token,
    // ... 기타 옵션
  });
}
```

### Origin 검증

프로덕션 환경에서는 반드시 허용된 origin만 메시지를 받도록 설정:

```javascript
// embed.js 내부에서 이미 구현됨
const allowedOrigins = [
  'https://link-coach.netlify.app',
  // 개발 환경 origin은 프로덕션에서 제거
];
```

## 스타일 커스터마이징

### CSS를 통한 위젯 스타일 조정

```css
/* iframe 컨테이너 스타일 */
#link-coach-widget-iframe {
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

/* 모바일 반응형 */
@media (max-width: 768px) {
  #link-coach-widget-iframe {
    width: 100% !important;
    height: 100vh !important;
    border-radius: 0;
  }
}
```

### 위젯 위치 커스터마이징

```javascript
LinkCoach.init({
  token: 'YOUR_TOKEN',
  userId: 'user_123',
  leadershipType: '개별비전형',
  position: 'custom' // custom 위치 사용
});

// CSS로 위치 지정
const iframe = document.getElementById('link-coach-widget-iframe');
iframe.style.top = '100px';
iframe.style.right = '50px';
```

## 문제 해결

### 위젯이 표시되지 않음

1. 브라우저 콘솔에서 에러 확인
2. JWT 토큰이 유효한지 확인
3. CORS 설정 확인
4. 필수 파라미터 (token, userId, leadershipType) 제공 확인

```javascript
// 디버깅 모드
LinkCoach.config.debug = true;
LinkCoach.init({ /* ... */ });
```

### 메시지 통신 실패

```javascript
// postMessage 이벤트 모니터링
window.addEventListener('message', (event) => {
  console.log('Received message:', event.data);
});
```

### iframe 로딩 문제

```javascript
const iframe = document.getElementById('link-coach-widget-iframe');
iframe.onload = function() {
  console.log('Widget loaded successfully');
};
iframe.onerror = function() {
  console.error('Failed to load widget');
};
```

## 브라우저 호환성

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- 모바일 브라우저 (iOS Safari, Chrome Mobile)

## 성능 최적화

### Lazy Loading

```javascript
// 사용자가 스크롤할 때만 위젯 로드
const observer = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) {
    loadLinkCoachWidget();
    observer.disconnect();
  }
});

observer.observe(document.getElementById('widget-trigger'));
```

### 프리로딩

```html
<!-- DNS prefetch -->
<link rel="dns-prefetch" href="https://link-coach.netlify.app">

<!-- Preconnect -->
<link rel="preconnect" href="https://link-coach.netlify.app">
```

## 예제 프로젝트

완전한 예제는 GitHub 저장소의 `/examples` 폴더를 참고하세요:

- `/examples/vanilla-js` - 순수 JavaScript 예제
- `/examples/react` - React 통합 예제
- `/examples/vue` - Vue.js 통합 예제
- `/examples/wordpress` - WordPress 플러그인 예제

## 지원

문제가 발생하거나 질문이 있으면:
- GitHub Issues: https://github.com/Junghoon-83/Link-Coach/issues
- 이메일: support@link-coach.com (예시)

## 라이선스

이 위젯은 Link-Coach 플랫폼의 일부이며, 사용 약관에 따라 제공됩니다.
