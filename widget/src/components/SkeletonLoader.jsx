function SkeletonLoader({ type = 'report' }) {
  if (type === 'report') {
    return (
      <div className="skeleton-report">
        {/* 헤더 스켈레톤 */}
        <div className="skeleton-badge" />

        {/* 요약 카드 스켈레톤 */}
        <div className="skeleton-summary-card">
          <div className="skeleton-title" />
          <div className="skeleton-text" />
          <div className="skeleton-text short" />
        </div>

        {/* 레이더 차트 스켈레톤 */}
        <div className="skeleton-radar-section">
          <div className="skeleton-chart-circle" />
          <div className="skeleton-score-cards">
            <div className="skeleton-score-card" />
            <div className="skeleton-score-card" />
            <div className="skeleton-score-card" />
          </div>
        </div>

        {/* 강점 카드 스켈레톤 */}
        <div className="skeleton-strengths">
          <div className="skeleton-card" />
          <div className="skeleton-card" />
          <div className="skeleton-card" />
        </div>
      </div>
    );
  }

  if (type === 'chat') {
    return (
      <div className="skeleton-chat">
        <div className="skeleton-message assistant">
          <div className="skeleton-avatar" />
          <div className="skeleton-message-content">
            <div className="skeleton-text" />
            <div className="skeleton-text short" />
          </div>
        </div>
        <div className="skeleton-message user">
          <div className="skeleton-message-content user">
            <div className="skeleton-text short" />
          </div>
          <div className="skeleton-avatar" />
        </div>
        <div className="skeleton-message assistant">
          <div className="skeleton-avatar" />
          <div className="skeleton-message-content">
            <div className="skeleton-text" />
            <div className="skeleton-text" />
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default SkeletonLoader;
