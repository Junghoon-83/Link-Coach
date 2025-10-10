import { useState } from 'react'

function ReportViewer({ report }) {
  const [isExpanded, setIsExpanded] = useState(false)

  // 더미 데이터
  const dummyReport = {
    leadershipType: '개별비전형',
    leadershipCode: 'LLH', // 개별비전형: 공유(L), 상호작용(L), 성장(H)
    scores: {
      sharing: 4.2, // 4.5 미만
      interaction: 4.0, // 4.5 미만
      growth: 5.5 // 4.5 이상
    },
    summary: '미래 지향적 비전과 개인 성장을 중심으로 팀을 이끄는 리더십 스타일입니다. 혁신적 관점으로 과제를 재정의하며, 실행 과정에서 팀원과의 명확한 목표 정렬이 성공의 핵심입니다.',
    strengths: [
      {
        title: '전략적 사고와 혁신',
        description: '신사업 기획, 문제 재정의, 혁신 아이디어 도출에 탁월한 역량을 발휘합니다.'
      },
      {
        title: '변화 주도 능력',
        description: '방향 전환이 필요한 초기 단계에서 팀을 이끌며 새로운 가능성을 제시합니다.'
      },
      {
        title: '장기 비전 수립',
        description: '개인과 조직의 성장 로드맵을 설계하고 미래 지향적 목표를 명확히 합니다.'
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

  // 레이더 차트 계산
  const calculateRadarPoint = (score, angle) => {
    const center = 200
    const maxRadius = 160
    const radius = ((score - 1) / 5) * maxRadius
    const x = center + radius * Math.cos(angle)
    const y = center + radius * Math.sin(angle)
    return { x, y }
  }

  const angles = {
    sharing: -Math.PI / 2,
    interaction: Math.PI / 6,
    growth: 5 * Math.PI / 6
  }

  const sharingPoint = calculateRadarPoint(dummyReport.scores.sharing, angles.sharing)
  const interactionPoint = calculateRadarPoint(dummyReport.scores.interaction, angles.interaction)
  const growthPoint = calculateRadarPoint(dummyReport.scores.growth, angles.growth)

  const polygonPoints = `${sharingPoint.x},${sharingPoint.y} ${interactionPoint.x},${interactionPoint.y} ${growthPoint.x},${growthPoint.y}`

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
        <h3 className="summary-title">{dummyReport.leadershipType}</h3>
        <p className="summary-text">{dummyReport.summary}</p>
      </div>

      {/* 레이더 차트 */}
      <div className="radar-chart-section">
        <h3 className="section-title">리더십 역량 분석</h3>
        <div className="radar-chart-container">
          <svg viewBox="0 0 400 400" className="radar-chart">
            {/* 배경 격자 */}
            <g className="radar-grid">
              {[1, 2, 3, 4, 5, 6].map((level) => (
                <circle
                  key={level}
                  cx="200"
                  cy="200"
                  r={((level - 1) / 5) * 160}
                  fill="none"
                  stroke="rgba(139, 92, 246, 0.1)"
                  strokeWidth="1"
                />
              ))}
              {/* 축선 */}
              <line x1="200" y1="200" x2="200" y2="40" stroke="rgba(139, 92, 246, 0.2)" strokeWidth="1" />
              <line x1="200" y1="200" x2="338.6" y2="280" stroke="rgba(139, 92, 246, 0.2)" strokeWidth="1" />
              <line x1="200" y1="200" x2="61.4" y2="280" stroke="rgba(139, 92, 246, 0.2)" strokeWidth="1" />
            </g>

            {/* 점수 영역 */}
            <polygon
              points={polygonPoints}
              fill="rgba(139, 92, 246, 0.15)"
              stroke="rgba(139, 92, 246, 0.6)"
              strokeWidth="2"
              className="score-polygon"
            />

            {/* 점수 포인트 */}
            <circle
              cx={sharingPoint.x}
              cy={sharingPoint.y}
              r="6"
              fill="#10b981"
              stroke="white"
              strokeWidth="2"
              className="score-point sharing"
            />
            <circle
              cx={interactionPoint.x}
              cy={interactionPoint.y}
              r="6"
              fill="#3b82f6"
              stroke="white"
              strokeWidth="2"
              className="score-point interaction"
            />
            <circle
              cx={growthPoint.x}
              cy={growthPoint.y}
              r="6"
              fill="#f59e0b"
              stroke="white"
              strokeWidth="2"
              className="score-point growth"
            />

            {/* 축 레이블 */}
            <text x="200" y="25" textAnchor="middle" className="axis-label">공유</text>
            <text x="360" y="290" textAnchor="middle" className="axis-label">상호작용</text>
            <text x="40" y="290" textAnchor="middle" className="axis-label">성장</text>
          </svg>

          <div className="score-details">
            <div className="score-detail-card">
              <div className="score-detail-title">공유 (Sharing)</div>
              <div className="score-detail-value sharing-color">{dummyReport.scores.sharing.toFixed(1)}</div>
              <div className="score-detail-desc">목표 공유 및 참여 촉진</div>
            </div>
            <div className="score-detail-card">
              <div className="score-detail-title">상호작용 (Interaction)</div>
              <div className="score-detail-value interaction-color">{dummyReport.scores.interaction.toFixed(1)}</div>
              <div className="score-detail-desc">관계 구축 및 소통 역량</div>
            </div>
            <div className="score-detail-card">
              <div className="score-detail-title">성장 (Growth)</div>
              <div className="score-detail-value growth-color">{dummyReport.scores.growth.toFixed(1)}</div>
              <div className="score-detail-desc">개별 성장 지원 역량</div>
            </div>
          </div>
        </div>
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
