import { useState, useEffect } from 'react'
import Widget from './components/Widget'
import { setAuthToken } from './services/api'

function App() {
  const [isInitialized, setIsInitialized] = useState(false)
  const [userData, setUserData] = useState(null)

  useEffect(() => {
    // 부모 페이지로부터 초기 데이터 수신
    const handleMessage = (event) => {
      // 실제 프로덕션에서는 origin 검증 필요
      // if (event.origin !== 'https://your-link-website.com') return

      const { type, data } = event.data

      if (type === 'INIT_WIDGET') {
        // JWT 토큰, 사용자 정보 저장
        const { token, userId, leadershipType, assessmentData } = data

        if (token) {
          setAuthToken(token)
        }

        setUserData({
          userId,
          leadershipType,
          assessmentData
        })

        setIsInitialized(true)
      }
    }

    window.addEventListener('message', handleMessage)

    // 부모 페이지에 준비 완료 신호 전송
    window.parent.postMessage({ type: 'WIDGET_READY' }, '*')

    return () => {
      window.removeEventListener('message', handleMessage)
    }
  }, [])

  // 데모/개발 모드: 임시 데이터로 초기화
  useEffect(() => {
    console.log('[App] useEffect 실행, isInitialized:', isInitialized)

    if (!isInitialized) {
      console.log('[App] 초기화 시작...')

      // 자동 초기화 (데모용)
      const initDemo = async () => {
        // 폴백: 데모 토큰 사용
        setAuthToken('demo-token-12345')
        setUserData({
          userId: 'demo_user_jiyoung',
          leadershipType: '개별비전형',
          assessmentData: {
            scores: {
              extraversion: 75,
              thinking: 80,
              judging: 70
            }
          }
        })
        console.log('[App] 데모 초기화 완료')
        setIsInitialized(true)
      }

      setTimeout(initDemo, 500)
    }
  }, [isInitialized])

  if (!isInitialized) {
    return (
      <div className="widget-loading">
        <div className="spinner"></div>
        <p>Loading Link-Coach...</p>
      </div>
    )
  }

  return (
    <div className="link-coach-app">
      <Widget userData={userData} />
    </div>
  )
}

export default App
