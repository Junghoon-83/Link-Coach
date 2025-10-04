#!/bin/bash

# Link-Coach MVP 로컬 개발 환경 설정 스크립트
# Docker 없이 로컬에서 실행

set -e

echo "======================================"
echo "Link-Coach MVP 로컬 개발 환경 설정"
echo "======================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Python 버전 확인
echo "🐍 1. Python 환경 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ $PYTHON_VERSION 확인됨${NC}"
echo ""

# 2. Node.js 버전 확인
echo "📦 2. Node.js 환경 확인 중..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js가 설치되어 있지 않습니다.${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION 확인됨${NC}"
echo ""

# 3. 백엔드 Python 가상환경 설정
echo "🔧 3. 백엔드 Python 가상환경 설정 중..."
cd server

if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
fi

echo "가상환경 활성화 및 의존성 설치 중..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✅ 백엔드 환경 설정 완료${NC}"
cd ..
echo ""

# 4. 프론트엔드 의존성 설치
echo "📦 4. 프론트엔드 의존성 설치 중..."
cd widget

if [ ! -d "node_modules" ]; then
    echo "npm install 실행 중..."
    npm install > /dev/null 2>&1
fi

echo -e "${GREEN}✅ 프론트엔드 환경 설정 완료${NC}"
cd ..
echo ""

# 5. 샘플 ML 모델 생성
echo "🤖 5. 샘플 ML 모델 생성 중..."
cd server
source venv/bin/activate
python scripts/create_sample_model.py
deactivate
cd ..
echo ""

echo "======================================"
echo -e "${GREEN}✅ 로컬 개발 환경 설정 완료!${NC}"
echo "======================================"
echo ""
echo "⚠️  주의: Docker 없이 로컬에서 실행하는 경우:"
echo "  - PostgreSQL과 ChromaDB는 별도로 설치 및 실행해야 합니다"
echo "  - 또는 Docker Desktop을 설치하여 docker-compose 사용을 권장합니다"
echo ""
echo "📍 로컬 실행 방법:"
echo ""
echo "  [터미널 1] 백엔드 실행:"
echo "  $ cd server"
echo "  $ source venv/bin/activate"
echo "  $ uvicorn app.main:app --reload"
echo ""
echo "  [터미널 2] 프론트엔드 실행:"
echo "  $ cd widget"
echo "  $ npm run dev"
echo ""
echo "💡 Docker 설치 권장:"
echo "  https://www.docker.com/products/docker-desktop"
echo ""
