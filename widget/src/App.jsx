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

  // 개발 모드: 임시 데이터로 초기화
  useEffect(() => {
    console.log('[App] useEffect 실행, DEV:', import.meta.env.DEV, 'isInitialized:', isInitialized)

    if (import.meta.env.DEV && !isInitialized) {
      console.log('[App] 개발 모드 초기화 시작...')

      // 개발 환경에서 자동 초기화
      const initDev = async () => {
        try {
          console.log('[App] 토큰 요청 중...')
          // 서버에서 개발용 JWT 토큰 가져오기
          const response = await fetch('/dev/token')
          console.log('[App] 토큰 응답:', response.status)

          const data = await response.json()
          console.log('[App] 토큰 데이터:', data)

          // 실제 JWT 토큰 설정
          setAuthToken(data.token)

          setUserData({
            userId: data.user_id,
            leadershipType: '개별비전형',
            assessmentData: {
              scores: {
                extraversion: 75,
                thinking: 80,
                judging: 70
              }
            }
          })
          console.log('[App] 초기화 완료!')
          setIsInitialized(true)
        } catch (error) {
          console.error('[App] 개발 토큰 가져오기 실패:', error)
          // 폴백: 간단한 토큰 사용
          setAuthToken('dev-test-token-12345')
          setUserData({
            userId: 'dev_user_123',
            leadershipType: '개별비전형',
            assessmentData: null
          })
          console.log('[App] 폴백으로 초기화 완료')
          setIsInitialized(true)
        }
      }

      setTimeout(initDev, 1500)
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
