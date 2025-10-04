"""
Vector Database 서비스
ChromaDB를 사용한 임상 데이터 저장 및 검색
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class VectorDBService:
    """Vector DB 서비스 (싱글톤)"""

    def __init__(self):
        self.client: Optional[chromadb.HttpClient] = None
        self.collection: Optional[chromadb.Collection] = None
        self.connected: bool = False

    async def connect(self) -> None:
        """ChromaDB 연결"""
        if self.connected:
            logger.info("ChromaDB가 이미 연결되어 있습니다.")
            return

        try:
            logger.info(f"ChromaDB 연결 중: {settings.chroma_url}")

            # HttpClient로 연결
            self.client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                settings=ChromaSettings(
                    anonymized_telemetry=False
                )
            )

            # 컬렉션 가져오기 또는 생성
            try:
                self.collection = self.client.get_collection(
                    name=settings.CHROMA_COLLECTION_NAME
                )
                logger.info(f"✅ 기존 컬렉션 로드: {settings.CHROMA_COLLECTION_NAME}")
            except Exception:
                logger.info(f"컬렉션 생성 중: {settings.CHROMA_COLLECTION_NAME}")
                self.collection = self.client.create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"description": "리더십 임상 데이터"}
                )
                logger.info(f"✅ 새 컬렉션 생성: {settings.CHROMA_COLLECTION_NAME}")

            self.connected = True

        except Exception as e:
            logger.error(f"ChromaDB 연결 실패: {e}", exc_info=True)
            self.connected = False
            raise

    async def health_check(self) -> bool:
        """
        ChromaDB 헬스체크

        Returns:
            bool: 연결 상태
        """
        try:
            if not self.client:
                await self.connect()

            # Heartbeat 확인
            heartbeat = self.client.heartbeat()
            logger.info(f"ChromaDB 헬스체크: {heartbeat}")
            return True

        except Exception as e:
            logger.error(f"ChromaDB 헬스체크 실패: {e}")
            return False

    async def search_similar_documents(
        self,
        query: str,
        leadership_type: Optional[str] = None,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        유사 문서 검색

        Args:
            query: 검색 쿼리
            leadership_type: 리더십 유형 필터 (선택)
            top_k: 반환할 문서 수

        Returns:
            List[Dict]: 검색 결과 리스트
                - id: 문서 ID
                - content: 문서 내용
                - metadata: 메타데이터
                - distance: 거리 (낮을수록 유사)
        """
        if not self.connected:
            await self.connect()

        if top_k is None:
            top_k = settings.RAG_TOP_K

        try:
            logger.info(f"문서 검색: query='{query}', type={leadership_type}, top_k={top_k}")

            # 메타데이터 필터 구성
            where_filter = None
            if leadership_type:
                where_filter = {"leadership_type": leadership_type}

            # 검색 수행
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter
            )

            # 결과 포맷팅
            documents = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    doc = {
                        "id": results['ids'][0][i],
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else 0.0
                    }
                    documents.append(doc)

            logger.info(f"검색 결과: {len(documents)}개 문서")
            return documents

        except Exception as e:
            logger.error(f"문서 검색 실패: {e}", exc_info=True)
            return []

    async def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """
        문서 추가

        Args:
            documents: 문서 내용 리스트
            metadatas: 메타데이터 리스트
            ids: 문서 ID 리스트

        Returns:
            bool: 성공 여부
        """
        if not self.connected:
            await self.connect()

        try:
            logger.info(f"문서 추가 중: {len(documents)}개")

            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"✅ {len(documents)}개 문서 추가 완료")
            return True

        except Exception as e:
            logger.error(f"문서 추가 실패: {e}", exc_info=True)
            return False

    async def get_collection_count(self) -> int:
        """
        컬렉션 내 문서 수 조회

        Returns:
            int: 문서 수
        """
        if not self.connected:
            await self.connect()

        try:
            count = self.collection.count()
            logger.info(f"컬렉션 문서 수: {count}")
            return count

        except Exception as e:
            logger.error(f"문서 수 조회 실패: {e}")
            return 0


# 싱글톤 인스턴스
vector_db_service = VectorDBService()
