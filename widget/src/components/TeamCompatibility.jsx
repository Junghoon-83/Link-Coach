import { useState } from 'react'

function TeamCompatibility({ userData }) {
  const [selectedFollowers, setSelectedFollowers] = useState([])
  const [memberNames, setMemberNames] = useState({})
  const [showCompatibility, setShowCompatibility] = useState(false)

  // 리더십 데이터
  const leadershipData = {
    leadershipType: '개별비전형',
    leadershipCode: 'LLH', // 개별비전형: 공유(L), 상호작용(L), 성장(H)
    scores: {
      sharing: 4.2, // 4.5 미만
      interaction: 4.0, // 4.5 미만
      growth: 5.5 // 4.5 이상
    }
  }

  // 팔로워십 유형 데이터 (Link-Lite와 동일)
  const followershipTypes = [
    { id: 'driver', name: 'Driver', description: '팀원은 리더가 제안한 내용 뿐 아니라 내용을 발전시켜오는 적극적인 업무 참여 태도를 보인다. 문제가 발생할때에는 원인에 대한 분석 뿐만 아니라 해결책을 모색한다.' },
    { id: 'thinker', name: 'Thinker', description: '한가지 일에 대한 몰입이 높은편이고 여러가지 일에 대해 정신 에너지를 전환하는 것을 어려워한다. 새로운 아이디어를 많이 내는 편이지만, 실행을 위한 행동은 느린편이다.' },
    { id: 'supporter', name: 'Supporter', description: '리더의 업무 지시에 빠르게 순응하고 업무를 처리한다. 리더를 포함한 팀 구성원의 업무를 지원하는 역할을 편안해한다. 주도적으로 나서서 업무를 진행하는 것에 부담이 있는 편이라, 리더로서 팀원의 리더십 개발이 고민이 된다.' },
    { id: 'doer', name: 'Doer', description: 'R&R이 분명할 경우 업무에 대한 이해가 빠르고 정확도 높게 업무를 처리한다. 다만 새로운 아이디어가 필요하거나 개념 수준에서 논의가 필요한 상황일 때 혼란스러워한다.' },
    { id: 'follower', name: 'Follower', description: '업무 동기가 떨어져 보이고, 업무 실수 및 업무 몰입도가 많이 떨어져 있다. 최근들어 이 팀원의 업무 몰입을 높이기 위해 어떻게 접근해야 할지에 대한 고민이 깊어졌다.' }
  ]

  // 궁합 데이터 (LLH: 성과지향 리더 = 개별비전형)
  const compatibilityMatrix = {
    driver: { score: 88, message: '좋은 조합! 적극성과 성과 지향이 높은 성과를 만듭니다.' },
    thinker: { score: 80, message: '좋은 조합! 사고력과 성과 지향이 질적 성과를 이룹니다.' },
    supporter: { score: 70, message: '보통 조합. 지지는 좋지만 관계적 소통이 부족할 수 있습니다.' },
    doer: { score: 95, message: '완벽한 조합! 실행력과 성과 지향이 최고의 효율성을 만듭니다.' },
    follower: { score: 60, message: '주의 필요. 성과 지향만으로는 동기부여 회복에 한계가 있습니다.' }
  }

  // 팔로워십 선택/해제
  const toggleFollower = (followerId) => {
    setSelectedFollowers(prev => {
      if (prev.includes(followerId)) {
        // 선택 해제
        const newNames = { ...memberNames }
        delete newNames[followerId]
        setMemberNames(newNames)
        return prev.filter(id => id !== followerId)
      } else {
        // 선택
        return [...prev, followerId]
      }
    })
    setShowCompatibility(false)
  }

  // 팀원 이름 업데이트
  const updateMemberName = (followerId, name) => {
    setMemberNames(prev => ({ ...prev, [followerId]: name }))
  }

  // 궁합 분석
  const analyzeCompatibility = () => {
    if (selectedFollowers.length === 0) return
    setShowCompatibility(true)
  }

  // 점수에 따른 레벨 (Link-Lite와 동일)
  const getScoreLevel = (score) => {
    if (score >= 90) return '최고'
    if (score >= 80) return '좋음'
    if (score >= 70) return '보통'
    if (score >= 60) return '주의'
    return '개선 필요'
  }

  // 점수에 따른 클래스
  const getScoreClass = (score) => {
    if (score >= 90) return 'score-excellent'
    if (score >= 80) return 'score-good'
    if (score >= 70) return 'score-average'
    if (score >= 60) return 'score-caution'
    return 'score-poor'
  }

  return (
    <div className="team-compatibility-container">
      {/* 리더십 유형 설명 */}
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
        <h3 className="summary-title">{leadershipData.leadershipType}</h3>
        <p className="summary-text">지영 리더님은 개별 구성원의 성장과 비전 실현을 최우선으로 하는 리더십 스타일을 가지고 계십니다.</p>
      </div>

      {/* 팀 궁합 분석 섹션 */}
      <div className="followership-section">
        <h3 className="section-title">팀원의 팔로워십 유형을 선택하세요</h3>
        <p className="section-description">팀원들의 팔로워십 유형을 선택하면 맞춤형 코칭 전략을 제안해드립니다.</p>

        <div className="followership-grid">
          {followershipTypes.map(follower => {
            const isSelected = selectedFollowers.includes(follower.id)
            return (
              <div
                key={follower.id}
                className={`followership-card ${isSelected ? 'selected' : ''}`}
                onClick={(e) => {
                  if (e.target.tagName !== 'INPUT') {
                    toggleFollower(follower.id)
                  }
                }}
              >
                <div className="followership-name">{follower.name}</div>
                <div className="followership-desc">{follower.description}</div>
                {isSelected && (
                  <input
                    type="text"
                    className="member-name-input"
                    placeholder="팀원 이름 입력 (선택사항)"
                    value={memberNames[follower.id] || ''}
                    onChange={(e) => updateMemberName(follower.id, e.target.value)}
                    onClick={(e) => e.stopPropagation()}
                  />
                )}
              </div>
            )
          })}
        </div>

        <button
          className="premium-btn"
          onClick={analyzeCompatibility}
          disabled={selectedFollowers.length === 0}
        >
          <span>팀 궁합 분석하기</span>
          <span>→</span>
        </button>
      </div>

      {/* 궁합 결과 */}
      {showCompatibility && selectedFollowers.length > 0 && (
        <div className="compatibility-results">
          <h3 className="section-title">팀 궁합 분석 결과</h3>
          <div className="compatibility-list">
            {selectedFollowers.map(followerId => {
              const follower = followershipTypes.find(f => f.id === followerId)
              const compatibility = compatibilityMatrix[followerId]
              const memberName = memberNames[followerId]
              const displayName = memberName
                ? `${memberName} (${follower.name})`
                : follower.name

              return (
                <div key={followerId} className="compatibility-item">
                  <div className="compatibility-score">
                    <div className={`score-circle ${getScoreClass(compatibility.score)}`}>
                      {compatibility.score}
                    </div>
                    <div className="score-level">{getScoreLevel(compatibility.score)}</div>
                  </div>
                  <div className="compatibility-info">
                    <h4>{displayName}</h4>
                    <div className="compatibility-message">{compatibility.message}</div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default TeamCompatibility
