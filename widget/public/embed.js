/**
 * Link-Coach Widget Embed Script
 * 외부 사이트에서 Link-Coach 위젯을 쉽게 통합할 수 있는 스크립트
 *
 * 사용법:
 * <script src="https://link-coach.netlify.app/embed.js"></script>
 * <script>
 *   LinkCoach.init({
 *     token: 'YOUR_JWT_TOKEN',
 *     userId: 'user_123',
 *     leadershipType: '개별비전형',
 *     container: '#link-coach-widget' // 선택사항
 *   });
 * </script>
 */

(function(window, document) {
  'use strict';

  // 이미 로드되었는지 확인
  if (window.LinkCoach) {
    console.warn('Link-Coach widget is already loaded.');
    return;
  }

  // 설정 기본값
  const DEFAULT_CONFIG = {
    widgetUrl: 'https://link-coach.netlify.app',
    container: null, // null이면 body에 자동 추가
    width: '400px',
    height: '600px',
    position: 'bottom-right', // bottom-right, bottom-left, custom
    zIndex: 9999,
    theme: 'light' // light, dark (미래 기능)
  };

  // LinkCoach 객체
  const LinkCoach = {
    config: {},
    iframe: null,
    isInitialized: false,

    /**
     * 위젯 초기화
     * @param {Object} options - 초기화 옵션
     * @param {string} options.token - JWT 인증 토큰
     * @param {string} options.userId - 사용자 ID
     * @param {string} options.leadershipType - 리더십 유형
     * @param {Object} options.assessmentData - 평가 데이터 (선택)
     * @param {string} options.container - 컨테이너 셀렉터 (선택)
     * @param {string} options.widgetUrl - 위젯 URL (선택, 기본값: 프로덕션 URL)
     */
    init(options) {
      if (this.isInitialized) {
        console.warn('Link-Coach widget is already initialized.');
        return;
      }

      // 필수 파라미터 검증
      if (!options.token) {
        console.error('Link-Coach: token is required');
        return;
      }
      if (!options.userId) {
        console.error('Link-Coach: userId is required');
        return;
      }
      if (!options.leadershipType) {
        console.error('Link-Coach: leadershipType is required');
        return;
      }

      // 설정 병합
      this.config = Object.assign({}, DEFAULT_CONFIG, options);

      // iframe 생성
      this.createIframe();

      // 메시지 리스너 등록
      this.setupMessageListener();

      this.isInitialized = true;
      console.log('Link-Coach widget initialized successfully');
    },

    /**
     * iframe 생성 및 삽입
     */
    createIframe() {
      const iframe = document.createElement('iframe');
      iframe.id = 'link-coach-widget-iframe';
      iframe.src = this.config.widgetUrl;
      iframe.style.border = 'none';
      iframe.style.position = this.config.position === 'custom' ? 'relative' : 'fixed';
      iframe.style.width = this.config.width;
      iframe.style.height = this.config.height;
      iframe.style.zIndex = this.config.zIndex;
      iframe.allow = 'clipboard-read; clipboard-write';

      // 위치 설정
      if (this.config.position === 'bottom-right') {
        iframe.style.bottom = '20px';
        iframe.style.right = '20px';
      } else if (this.config.position === 'bottom-left') {
        iframe.style.bottom = '20px';
        iframe.style.left = '20px';
      }

      // 반응형 설정 (모바일)
      if (window.innerWidth < 768) {
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.bottom = '0';
        iframe.style.right = '0';
        iframe.style.left = '0';
        iframe.style.top = '0';
      }

      // 컨테이너에 추가
      let container;
      if (this.config.container) {
        container = document.querySelector(this.config.container);
        if (!container) {
          console.error(`Link-Coach: Container "${this.config.container}" not found`);
          return;
        }
      } else {
        container = document.body;
      }

      container.appendChild(iframe);
      this.iframe = iframe;
    },

    /**
     * postMessage 리스너 설정
     */
    setupMessageListener() {
      window.addEventListener('message', (event) => {
        // 보안: origin 검증
        const allowedOrigins = [
          this.config.widgetUrl,
          'https://link-coach.netlify.app',
          'http://localhost:5173',
          'http://localhost:8888'
        ];

        if (!allowedOrigins.includes(event.origin)) {
          return;
        }

        const { type, data } = event.data;

        switch (type) {
          case 'WIDGET_READY':
            // 위젯이 준비되면 초기화 데이터 전송
            this.sendInitData();
            break;

          case 'WIDGET_RESIZE':
            // 위젯 크기 조정 요청
            if (data.height) {
              this.iframe.style.height = data.height + 'px';
            }
            break;

          case 'WIDGET_CLOSE':
            // 위젯 닫기 요청
            this.close();
            break;

          case 'WIDGET_ERROR':
            // 위젯 에러 처리
            console.error('Link-Coach widget error:', data);
            break;

          default:
            break;
        }
      });
    },

    /**
     * 초기화 데이터 전송
     */
    sendInitData() {
      if (!this.iframe || !this.iframe.contentWindow) {
        console.error('Link-Coach: iframe not found');
        return;
      }

      const initData = {
        type: 'INIT_WIDGET',
        data: {
          token: this.config.token,
          userId: this.config.userId,
          leadershipType: this.config.leadershipType,
          assessmentData: this.config.assessmentData || null
        }
      };

      this.iframe.contentWindow.postMessage(initData, this.config.widgetUrl);
    },

    /**
     * 위젯 표시
     */
    show() {
      if (this.iframe) {
        this.iframe.style.display = 'block';
      }
    },

    /**
     * 위젯 숨김
     */
    hide() {
      if (this.iframe) {
        this.iframe.style.display = 'none';
      }
    },

    /**
     * 위젯 토글
     */
    toggle() {
      if (this.iframe) {
        const isVisible = this.iframe.style.display !== 'none';
        this.iframe.style.display = isVisible ? 'none' : 'block';
      }
    },

    /**
     * 위젯 닫기 및 제거
     */
    close() {
      if (this.iframe) {
        this.iframe.remove();
        this.iframe = null;
        this.isInitialized = false;
      }
    },

    /**
     * 사용자 데이터 업데이트
     */
    updateUser(userData) {
      if (!this.iframe || !this.iframe.contentWindow) {
        console.error('Link-Coach: iframe not found');
        return;
      }

      this.iframe.contentWindow.postMessage({
        type: 'UPDATE_USER',
        data: userData
      }, this.config.widgetUrl);
    }
  };

  // 전역 객체에 노출
  window.LinkCoach = LinkCoach;

  // 자동 초기화 (data 속성 사용)
  document.addEventListener('DOMContentLoaded', function() {
    const scriptTag = document.querySelector('script[src*="embed.js"]');
    if (scriptTag) {
      const autoInit = scriptTag.getAttribute('data-auto-init');
      if (autoInit === 'true') {
        const config = {
          token: scriptTag.getAttribute('data-token'),
          userId: scriptTag.getAttribute('data-user-id'),
          leadershipType: scriptTag.getAttribute('data-leadership-type'),
          container: scriptTag.getAttribute('data-container'),
          position: scriptTag.getAttribute('data-position') || 'bottom-right'
        };

        if (config.token && config.userId && config.leadershipType) {
          LinkCoach.init(config);
        }
      }
    }
  });

})(window, document);
