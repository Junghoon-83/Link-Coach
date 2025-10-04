#!/bin/bash

# Link-Coach MVP 전체 설치 및 초기화 스크립트
# 사용법: ./setup.sh

set -e  # 에러 발생 시 중단

echo "======================================"
echo "Link-Coach MVP 설치 시작"
echo "======================================"
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 환경 변수 파일 확인
echo "📋 1. 환경 변수 확인 중..."
if [ ! -f "server/.env" ]; then
    echo -e "${YELLOW}⚠️  server/.env 파일이 없습니다.${NC}"
    echo "기본 .env 파일이 이미 생성되어 있어야 합니다."
    exit 1
fi

if [ ! -f "widget/.env" ]; then
    echo -e "${YELLOW}⚠️  widget/.env 파일이 없습니다.${NC}"
    echo "기본 .env 파일이 이미 생성되어 있어야 합니다."
    exit 1
fi

echo -e "${GREEN}✅ 환경 변수 파일 확인 완료${NC}"
echo ""

# 2. Docker Compose로 서비스 시작
echo "🐳 2. Docker 컨테이너 시작 중..."
docker-compose up -d

echo "⏳ 서비스가 준비될 때까지 대기 중... (30초)"
sleep 30

echo -e "${GREEN}✅ Docker 컨테이너 시작 완료${NC}"
echo ""

# 3. ML 모델 생성 (개발용)
echo "🤖 3. 샘플 ML 모델 생성 중..."
docker-compose exec -T server python scripts/create_sample_model.py

echo -e "${GREEN}✅ ML 모델 생성 완료${NC}"
echo ""

# 4. 데이터베이스 초기화
echo "💾 4. PostgreSQL 데이터베이스 초기화 중..."
docker-compose exec -T server python scripts/init_database.py

echo -e "${GREEN}✅ 데이터베이스 초기화 완료${NC}"
echo ""

# 5. ChromaDB 데이터 임베딩
echo "🔍 5. ChromaDB 데이터 임베딩 중..."
docker-compose exec -T server python scripts/init_chroma_data.py

echo -e "${GREEN}✅ ChromaDB 데이터 임베딩 완료${NC}"
echo ""

# 6. 헬스체크
echo "🏥 6. 서비스 헬스체크 중..."

# 백엔드 헬스체크
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 백엔드 API: http://localhost:8000${NC}"
else
    echo -e "${RED}❌ 백엔드 API 응답 없음${NC}"
fi

# ChromaDB 헬스체크
if curl -f http://localhost:8001/api/v1/heartbeat > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ChromaDB: http://localhost:8001${NC}"
else
    echo -e "${YELLOW}⚠️  ChromaDB 응답 없음 (정상일 수 있음)${NC}"
fi

echo ""
echo "======================================"
echo -e "${GREEN}✅ Link-Coach MVP 설치 완료!${NC}"
echo "======================================"
echo ""
echo "📍 접속 정보:"
echo "  - 백엔드 API: http://localhost:8000"
echo "  - API 문서: http://localhost:8000/docs"
echo "  - 프론트엔드 위젯: http://localhost:5173"
echo "  - PostgreSQL: localhost:5432"
echo "  - ChromaDB: http://localhost:8001"
echo ""
echo "📝 다음 단계:"
echo "  1. server/.env 파일에서 GEMINI_API_KEY 설정"
echo "  2. 브라우저에서 http://localhost:5173 접속"
echo "  3. API 문서 확인: http://localhost:8000/docs"
echo ""
echo "🛑 서비스 중지: docker-compose down"
echo "📊 로그 확인: docker-compose logs -f"
echo ""
