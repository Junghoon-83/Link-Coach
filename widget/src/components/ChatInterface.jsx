import { useState, useRef, useEffect } from 'react';
import { query } from '../services/api';

function ChatInterface({ reportId, userData }) {
  const [messages, setMessages] = useState([
    {
      id: 0,
      role: 'assistant',
      content: `안녕하세요, 지영 리더님. 저는 그라운더입니다. 당신의 리더십 분석 결과를 바탕으로 실질적인 인사이트를 제공하겠습니다. 궁금하신 점을 편하게 질문해 주세요.`
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

    // 스크롤 가능 여부 체크
    const messagesContainer = messagesEndRef.current?.parentElement;
    if (messagesContainer) {
      const hasScroll = messagesContainer.scrollHeight > messagesContainer.clientHeight;
      if (hasScroll) {
        messagesContainer.classList.add('has-scroll');
      } else {
        messagesContainer.classList.remove('has-scroll');
      }
    }
  }, [messages]);

  // 스크롤 위치 감지
  useEffect(() => {
    const messagesContainer = messagesEndRef.current?.parentElement;
    if (!messagesContainer) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = messagesContainer;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
      setShowScrollButton(!isNearBottom && scrollHeight > clientHeight);
    };

    messagesContainer.addEventListener('scroll', handleScroll);
    handleScroll(); // 초기 상태 체크

    return () => messagesContainer.removeEventListener('scroll', handleScroll);
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    const questionText = inputValue.trim();
    if (!questionText || isLoading) return;

    const userMessage = { id: Date.now(), role: 'user', content: questionText };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setInputValue('');

    try {
      // 대화 히스토리 구성 (role과 content만 포함)
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const response = await query(questionText, reportId, conversationHistory);
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.answer || response
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `일시적인 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.`
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      {showScrollButton && (
        <button
          className="scroll-to-bottom"
          onClick={scrollToBottom}
          aria-label="대화 끝으로 이동"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
      )}
      <div
        className="chat-messages"
        role="log"
        aria-live="polite"
        aria-label="대화 내용"
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message ${msg.role}`}
            role="article"
            aria-label={msg.role === 'user' ? '내 메시지' : '그라운더 메시지'}
          >
            <div className="message-avatar">
              {msg.role === 'user' ? (
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                </svg>
              )}
            </div>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {isLoading && (
            <div className="message assistant">
                <div className="message-avatar">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                  </svg>
                </div>
                <div className="message-content typing-message">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <span className="typing-text">분석 중</span>
                </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chat-input-container" role="form">
        <textarea
          className="chat-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSendMessage())}
          placeholder="그라운더에게 질문하세요..."
          disabled={isLoading}
          aria-label="메시지 입력"
          aria-describedby="send-button-description"
        />
        <span id="send-button-description" className="sr-only">
          Enter 키를 눌러 메시지를 전송하거나, Shift+Enter로 줄바꿈
        </span>
        <button
          className={`btn-send ${!inputValue.trim() && !isLoading ? 'btn-empty' : ''}`}
          onClick={handleSendMessage}
          disabled={!inputValue.trim() || isLoading}
          aria-label={isLoading ? '메시지 전송 중' : '메시지 전송'}
        >
          {isLoading ? (
            <svg className="btn-icon spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          ) : (
            <svg className="btn-icon" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;