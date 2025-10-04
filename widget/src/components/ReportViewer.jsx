import { useState } from 'react'

function ReportViewer({ report }) {
  const [isExpanded, setIsExpanded] = useState(false)

  // 더미 데이터
  const dummyReport = {
    leadershipType: '개별비전형',
    summary: '지영 리더님은 개별 구성원의 성장과 비전 실현을 최우선으로 하는 리더십 스타일을 가지고 계십니다.',
    strengths: [
      {
        title: '개인 맞춤형 코칭',
        description: '각 팀원의 강점과 성장 목표를 정확히 파악하여 맞춤형 지원을 제공합니다.'
      },
      {
        title: '장기적 비전 공유',
        description: '개인의 커리어 목표와 조직의 방향성을 연결하는 능력이 탁월합니다.'
      },
      {
        title: '신뢰 기반 관계',
        description: '팀원들과 깊은 신뢰 관계를 구축하여 솔직한 피드백 문화를 만듭니다.'
      }
    ],
    improvements: [
      {
        title: '팀 전체 성과 균형',
        description: '개별 성장에 집중하다 보면 팀 전체의 단기 성과 목표를 놓칠 수 있습니다.',
        action: '주간 팀 목표 점검 미팅을 통해 개인과 팀 목표의 균형을 유지하세요.'
      },
      {
        title: '의사결정 속도',
        description: '모든 의견을 경청하려다 보면 빠른 결정이 필요한 순간을 놓칠 수 있습니다.',
        action: '긴급 상황에서의 의사결정 프로세스를 사전에 정립해두세요.'
      }
    ],
    actionPlan: {
      immediate: '이번 주 1:1 미팅에서 각 팀원의 분기 목표를 재점검하세요.',
      shortTerm: '다음 달까지 팀 전체 OKR과 개인 목표의 연결고리를 문서화하세요.',
      longTerm: '분기마다 리더십 스타일 피드백 세션을 진행하여 균형점을 찾으세요.'
    }
  }

  if (!report) {
    return (
      <div className="report-viewer empty">
        <p className="empty-message">분석 리포트가 없습니다.</p>
      </div>
    )
  }

  return (
    <div className="report-viewer">
      <div className="report-header-badge">
        <div className="ai-badge">
          <svg className="ai-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
          </svg>
          <span className="ai-text">그라운더 AI 분석</span>
        </div>
      </div>

      <div className="report-summary-card">
        <h3 className="summary-title">리더십 분석 요약</h3>
        <p className="summary-text">{dummyReport.summary}</p>
      </div>

      <div className="report-section">
        <h3 className="section-title">
          <svg className="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          핵심 강점
        </h3>
        <div className="strengths-grid">
          {dummyReport.strengths.map((strength, index) => (
            <div key={index} className="strength-card">
              <div className="strength-number">{index + 1}</div>
              <h4 className="strength-title">{strength.title}</h4>
              <p className="strength-description">{strength.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="report-section">
        <h3 className="section-title">
          <svg className="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          성장 기회
        </h3>
        <div className="improvements-list">
          {dummyReport.improvements.map((item, index) => (
            <div key={index} className="improvement-card">
              <h4 className="improvement-title">{item.title}</h4>
              <p className="improvement-description">{item.description}</p>
              <div className="improvement-action">
                <svg className="action-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                <span>{item.action}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="report-section action-plan-section">
        <h3 className="section-title">
          <svg className="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
          실행 계획
        </h3>
        <div className="action-plan-timeline">
          <div className="timeline-item">
            <div className="timeline-marker immediate">즉시</div>
            <div className="timeline-content">
              <p>{dummyReport.actionPlan.immediate}</p>
            </div>
          </div>
          <div className="timeline-item">
            <div className="timeline-marker short-term">단기</div>
            <div className="timeline-content">
              <p>{dummyReport.actionPlan.shortTerm}</p>
            </div>
          </div>
          <div className="timeline-item">
            <div className="timeline-marker long-term">장기</div>
            <div className="timeline-content">
              <p>{dummyReport.actionPlan.longTerm}</p>
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}

export default ReportViewer
