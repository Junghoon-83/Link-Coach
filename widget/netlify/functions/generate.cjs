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
    const { user_id, leadership_type } = JSON.parse(event.body);

    if (!user_id || !leadership_type) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'user_id and leadership_type are required' }),
      };
    }

    // Gemini API 초기화
    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });

    const prompt = `당신은 리더십 전문 코치입니다. 다음 리더십 유형에 대한 분석 리포트를 작성하세요.

리더십 유형: ${leadership_type}

리포트 형식:
1. 한 문장 요약 (이 리더의 핵심 특징)
2. 주요 강점 3가지 (각 강점별 제목과 설명)
3. 개선 영역 2가지 (각 영역별 제목, 설명, 실행 방안)
4. 실행 계획 (즉시/단기/장기로 구분)

간결하고 실질적으로 작성하세요.`;

    const result = await model.generateContent(prompt);
    const interpretation = result.response.text();

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        report_id: `report_${Date.now()}`,
        interpretation,
        leadership_type,
        created_at: new Date().toISOString(),
      }),
    };
  } catch (error) {
    console.error('Generate error:', error);
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Failed to generate report',
        message: error.message
      }),
    };
  }
};
