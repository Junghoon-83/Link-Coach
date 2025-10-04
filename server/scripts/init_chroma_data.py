"""
ChromaDB 초기 데이터 임베딩 스크립트
리더십 임상 데이터를 ChromaDB에 저장
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import chromadb
from chromadb.config import Settings as ChromaSettings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 샘플 리더십 임상 데이터
SAMPLE_CLINICAL_DATA = [
    {
        "id": "entj_001",
        "leadership_type": "ENTJ",
        "content": """
ENTJ 유형의 리더는 천부적인 전략가입니다. 그들은 복잡한 문제를 체계적으로 분석하고
장기적인 비전을 수립하는 데 탁월합니다. 결단력이 강하고 목표 지향적이며,
팀을 효율적으로 이끌어 성과를 창출합니다. 그러나 때로는 타인의 감정을 간과할 수 있으며,
지나치게 직설적인 의사소통으로 인해 갈등이 발생할 수 있습니다.
        """,
        "metadata": {
            "category": "overview",
            "source": "clinical_research_2024"
        }
    },
    {
        "id": "entj_002",
        "leadership_type": "ENTJ",
        "content": """
ENTJ의 주요 강점: 1) 전략적 사고와 장기 계획 수립 능력, 2) 신속한 의사결정과 실행력,
3) 높은 목표 설정과 달성 의지, 4) 논리적이고 체계적인 문제 해결, 5) 팀 조직화 및
리소스 관리 능력. 이들은 위기 상황에서 냉정함을 유지하며 명확한 방향을 제시합니다.
        """,
        "metadata": {
            "category": "strengths",
            "source": "clinical_research_2024"
        }
    },
    {
        "id": "entj_003",
        "leadership_type": "ENTJ",
        "content": """
ENTJ가 직면하는 도전과제: 1) 팀원의 감정적 니즈를 간과하기 쉬움, 2) 지나치게
직설적인 피드백으로 인한 관계 손상, 3) 통제 욕구로 인한 위임의 어려움,
4) 완벽주의로 인한 스트레스와 번아웃, 5) 다른 관점에 대한 수용성 부족.
이러한 약점을 인식하고 보완하는 것이 리더십 발전의 핵심입니다.
        """,
        "metadata": {
            "category": "challenges",
            "source": "clinical_research_2024"
        }
    },
    {
        "id": "intj_001",
        "leadership_type": "INTJ",
        "content": """
INTJ 유형의 리더는 독립적인 사색가이자 혁신가입니다. 깊이 있는 분석과 독창적인
아이디어로 문제를 해결하며, 높은 기준과 완벽주의를 추구합니다. 체계적이고
계획적이며, 복잡한 시스템을 설계하고 개선하는 데 능숙합니다. 그러나 과도한
독립성으로 인해 협업이 어려울 수 있으며, 타인의 의견을 경시하는 경향이 있습니다.
        """,
        "metadata": {
            "category": "overview",
            "source": "clinical_research_2024"
        }
    },
    {
        "id": "intj_002",
        "leadership_type": "INTJ",
        "content": """
INTJ의 주요 강점: 1) 독창적이고 혁신적인 사고, 2) 깊이 있는 전략적 분석,
3) 높은 자기주도성과 독립성, 4) 장기적 비전과 계획 수립, 5) 복잡한 문제 해결 능력.
이들은 기존의 틀에 얽매이지 않고 새로운 접근법을 시도하며, 미래 지향적인
관점으로 조직을 이끕니다.
        """,
        "metadata": {
            "category": "strengths",
            "source": "clinical_research_2024"
        }
    },
    {
        "id": "enfj_001",
        "leadership_type": "ENFJ",
        "content": """
ENFJ 유형의 리더는 카리스마 넘치는 멘토입니다. 뛰어난 공감 능력으로 팀원들을
이해하고 동기부여하며, 조화로운 팀 문화를 구축합니다. 사람 중심적이고
열정적이며, 타인의 성장과 발전을 진심으로 지원합니다. 그러나 갈등 상황을
회피하거나, 타인의 평가에 지나치게 민감할 수 있습니다.
        """,
        "metadata": {
            "category": "overview",
            "source": "clinical_research_2024"
        }
    },
    {
        "id": "general_001",
        "leadership_type": None,
        "content": """
효과적인 리더십의 핵심은 자기 인식입니다. 자신의 강점과 약점을 정확히 파악하고,
상황에 맞게 리더십 스타일을 조정하는 능력이 중요합니다. 다양한 성격 유형의
팀원들을 이해하고 존중하며, 그들의 강점을 최대한 활용하는 것이 성공적인
리더의 조건입니다.
        """,
        "metadata": {
            "category": "general_advice",
            "source": "leadership_best_practices"
        }
    },
    {
        "id": "general_002",
        "leadership_type": None,
        "content": """
리더십 발전을 위한 실천 방법: 1) 정기적인 피드백 수집 및 반성, 2) 멘토링 및
코칭 프로그램 참여, 3) 다양한 리더십 경험 축적, 4) 감성 지능(EQ) 개발,
5) 지속적인 학습과 자기계발. 리더십은 타고나는 것이 아니라 개발되는 역량입니다.
        """,
        "metadata": {
            "category": "development",
            "source": "leadership_best_practices"
        }
    }
]


async def init_chromadb():
    """ChromaDB 초기화 및 데이터 임베딩"""
    try:
        logger.info("ChromaDB 연결 중...")

        # ChromaDB 클라이언트 생성
        client = chromadb.HttpClient(
            host=os.getenv("CHROMA_HOST", "localhost"),
            port=int(os.getenv("CHROMA_PORT", "8001")),
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "leadership_clinical_data")

        # 기존 컬렉션 삭제 (재초기화)
        try:
            client.delete_collection(name=collection_name)
            logger.info(f"기존 컬렉션 '{collection_name}' 삭제")
        except Exception:
            pass

        # 새 컬렉션 생성
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "리더십 임상 데이터"}
        )
        logger.info(f"새 컬렉션 '{collection_name}' 생성")

        # 데이터 임베딩
        documents = []
        metadatas = []
        ids = []

        for data in SAMPLE_CLINICAL_DATA:
            documents.append(data["content"].strip())

            metadata = data["metadata"].copy()
            if data["leadership_type"]:
                metadata["leadership_type"] = data["leadership_type"]

            metadatas.append(metadata)
            ids.append(data["id"])

        # ChromaDB에 추가
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        logger.info(f"✅ {len(documents)}개 문서 임베딩 완료")

        # 검증: 문서 수 확인
        count = collection.count()
        logger.info(f"현재 컬렉션 문서 수: {count}")

        # 테스트 검색
        results = collection.query(
            query_texts=["ENTJ의 강점은 무엇인가요?"],
            n_results=3
        )

        logger.info("테스트 검색 결과:")
        for i, doc in enumerate(results['documents'][0]):
            logger.info(f"  {i+1}. {doc[:100]}...")

        logger.info("✅ ChromaDB 초기화 완료!")

    except Exception as e:
        logger.error(f"❌ ChromaDB 초기화 실패: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(init_chromadb())
