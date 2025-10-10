import { useState, useEffect } from 'react';
import { generateInterpretation } from '../services/api';
import ChatInterface from './ChatInterface';
import ReportViewer from './ReportViewer';
import TeamCompatibility from './TeamCompatibility';

function Widget({ userData }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('report');

  useEffect(() => {
    const loadReport = async () => {
      try {
        // 더미 리포트 데이터 사용
        const dummyReport = {
          report_id: 'demo_report_001',
          interpretation: '지영 리더님의 리더십 분석 결과입니다.',
          leadership_type: userData.leadershipType,
          created_at: new Date().toISOString()
        };

        setTimeout(() => {
          setReport(dummyReport);
          setLoading(false);
        }, 100);
      } catch (err) {
        setError('리포트 생성에 실패했습니다: ' + err.message);
        setLoading(false);
      }
    };

    if (userData) {
      loadReport();
    }
  }, [userData]);

  if (loading) {
    return (
      <div className="widget-container loading-state">
        <div className="loading-content">
          <div className="loader">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <p className="loading-text">리더십 분석 리포트를 생성하고 있습니다</p>
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="widget-container error-state">
        <div className="error-content">
          <p className="error-title">리포트 생성 실패</p>
          <p className="error-message">{error}</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="widget-container empty-state">
        <p>리포트를 불러올 수 없습니다.</p>
      </div>
    );
  }

  return (
    <>
      <div className="widget-container">
        <div className="widget-header">
          <div className="header-content">
            <h2 className="widget-title">Link-Coach</h2>
            <p className="widget-subtitle">AI 링커십 코치</p>
          </div>
          <div className="user-info">
            <span className="user-name">지영 리더님</span>
            <span className="divider">|</span>
            <span className="leadership-type">{userData.leadershipType}</span>
          </div>
        </div>
        <div className="widget-tabs">
          <button
            className={`tab-btn ${activeTab === 'report' ? 'active' : ''}`}
            onClick={() => setActiveTab('report')}
            role="tab"
            aria-selected={activeTab === 'report'}
            aria-controls="report-panel"
          >
            <svg className="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span className="tab-label">분석 리포트</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'compatibility' ? 'active' : ''}`}
            onClick={() => setActiveTab('compatibility')}
            role="tab"
            aria-selected={activeTab === 'compatibility'}
            aria-controls="compatibility-panel"
          >
            <svg className="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span className="tab-label">팀 궁합</span>
          </button>
        </div>
        <div className="widget-content">
          {activeTab === 'report' && (
            <ReportViewer report={report} />
          )}
          {activeTab === 'compatibility' && (
            <TeamCompatibility userData={userData} />
          )}
          {activeTab === 'chat' && <ChatInterface reportId={report.report_id} userData={userData} />}
        </div>
      </div>

      {/* 플로팅 채팅 버튼 - report와 compatibility 탭일 때 표시 */}
      {(activeTab === 'report' || activeTab === 'compatibility') && (
        <button className="floating-chat-button" onClick={() => setActiveTab('chat')}>
          <svg className="chat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span className="chat-label">그라운더와 대화하기</span>
        </button>
      )}
    </>
  );
}

export default Widget;