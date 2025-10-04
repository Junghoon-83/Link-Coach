import { useState, useEffect } from 'react';
import { generateInterpretation } from '../services/api';
import ChatInterface from './ChatInterface';
import ReportViewer from './ReportViewer';

function Widget({ userData }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('report');

  useEffect(() => {
    const loadReport = async () => {
      try {
        const reportData = await generateInterpretation({
          user_id: userData.userId,
          leadership_type: userData.leadershipType,
          assessment_data: userData.assessmentData,
        });
        setReport(reportData);
      } catch (err) {
        setError('리포트 생성에 실패했습니다: ' + err.message);
      } finally {
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
          className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
          role="tab"
          aria-selected={activeTab === 'chat'}
          aria-controls="chat-panel"
        >
          <svg className="tab-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span className="tab-label">그라운더와 대화</span>
        </button>
      </div>
      <div className="widget-content">
        {activeTab === 'report' && (
          <ReportViewer report={report} />
        )}
        {activeTab === 'chat' && <ChatInterface reportId={report.report_id} userData={userData} />}
      </div>
    </div>
  );
}

export default Widget;