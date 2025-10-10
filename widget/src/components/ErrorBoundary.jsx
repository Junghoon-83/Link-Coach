import { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // 프로덕션에서는 Sentry 등으로 전송
    if (import.meta.env.PROD) {
      // TODO: Send to error tracking service
      // Sentry.captureException(error, { extra: errorInfo });
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary-container">
          <div className="error-boundary-content">
            <svg
              className="error-icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>

            <h2 className="error-title">문제가 발생했습니다</h2>

            <p className="error-message">
              일시적인 오류로 서비스를 불러올 수 없습니다.
              <br />
              잠시 후 다시 시도해 주세요.
            </p>

            {import.meta.env.DEV && this.state.error && (
              <details className="error-details">
                <summary>개발자 정보</summary>
                <pre>{this.state.error.toString()}</pre>
              </details>
            )}

            <button
              className="error-retry-button"
              onClick={this.handleReset}
            >
              다시 시도
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
