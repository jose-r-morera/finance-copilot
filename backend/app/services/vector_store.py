import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)

class VectorStoreService:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            settings=ChromaSettings(allow_reset=True, anonymized_telemetry=False)
        )
        self.collection_name = settings.CHROMA_COLLECTION_NAME

    def get_or_create_collection(self):
        """
        Retrieves the default collection or creates it if it doesn't exist.
        """
        try:
            return self.client.get_or_create_collection(name=self.collection_name)
        except Exception as e:
            logger.error("Failed to get or create Chroma collection", error=str(e), collection=self.collection_name)
            raise

    def heartbeat(self) -> bool:
        """
        Checks if the ChromaDB service is responsive.
        """
        try:
            self.client.heartbeat()
            return True
        except Exception as e:
            logger.warning("ChromaDB heartbeat failed", error=str(e))
            return False

    def upsert_documents(self, ids: list[str], documents: list[str], metadatas: list[dict] | None = None, embeddings: list[list[float]] | None = None):
        """
        Upserts documents into the collection.
        """
        collection = self.get_or_create_collection()
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        logger.info("Upserted documents to Chroma", count=len(ids))

    def query(self, query_texts: list[str], n_results: int = 5):
        """
        Queries the collection for similar documents.
        """
        collection = self.get_or_create_collection()
        return collection.query(
            query_texts=query_texts,
            n_results=n_results
        )

vector_store_service = VectorStoreService()
