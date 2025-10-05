const { GoogleGenerativeAI } = require('@google/generative-ai');

exports.handler = async (event) => {
  // CORS 헤더
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json',
  };

  // OPTIONS 요청 처리
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      headers,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  try {
    console.log('Chat function called');
    const { question, conversationHistory } = JSON.parse(event.body);
    console.log('Question:', question);

    if (!question) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Question is required' }),
      };
    }

    // API 키 확인
    if (!process.env.GEMINI_API_KEY) {
      console.error('GEMINI_API_KEY not found');
      return {
        statusCode: 500,
        headers,
        body: JSON.stringify({ error: 'API key not configured' }),
      };
    }

    // Gemini API 초기화
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: 'gemini-2.5-flash' });

    // 대화 히스토리 구성
    const history = (conversationHistory || []).map(msg => ({
      role: msg.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: msg.content }],
    }));

    // 시스템 프롬프트
    const systemPrompt = `당신은 "그라운더"라는 이름의 AI 리더십 코치입니다.
지영 리더님은 "개별비전형" 리더십 스타일을 가지고 있습니다.

개별비전형 리더의 특징:
- 각 팀원의 고유한 강점과 성장 목표를 파악하여 맞춤형 코칭 제공
- 개인의 커리어 비전과 조직의 방향성을 효과적으로 연결
- 깊은 신뢰 관계를 구축하여 솔직한 피드백 문화 조성

개선 영역:
- 개별 성장에 집중하다 보면 팀 전체의 단기 성과 목표를 놓칠 수 있음
- 모든 의견을 경청하려다 의사결정이 늦어질 수 있음

전문적이고 따뜻한 톤으로 실질적인 조언을 제공하세요. 답변은 2-3문장으로 간결하게 작성하세요.`;

    const chat = model.startChat({
      history: [
        {
          role: 'user',
          parts: [{ text: systemPrompt }],
        },
        {
          role: 'model',
          parts: [{ text: '네, 알겠습니다. 지영 리더님의 개별비전형 리더십을 고려하여 실질적인 조언을 제공하겠습니다.' }],
        },
        ...history,
      ],
    });

    console.log('Sending message to Gemini...');
    const result = await chat.sendMessage(question);
    const answer = result.response.text();
    console.log('Response received');

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({ answer }),
    };
  } catch (error) {
    console.error('Chat error:', error);
    console.error('Error details:', error.stack);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Failed to generate response',
        message: error.message,
        details: error.toString()
      }),
    };
  }
};
