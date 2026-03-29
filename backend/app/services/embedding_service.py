from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from backend.app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)

class EmbeddingService:
    """
    Service to generate embeddings for text chunks using Google Gemini with OpenAI fallback.
    """
    
    def __init__(self):
        self.gemini_embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY
        )
        self.openai_embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.OPENAI_API_KEY
        )

    def embed_chunks(self, texts: list[str]) -> list[list[float]]:
        """
        Generates embeddings for a list of text strings.
        Tries Gemini first, falls back to OpenAI if it fails.
        """
        try:
            logger.info("Generating embeddings with Gemini", count=len(texts))
            return self.gemini_embeddings.embed_documents(texts)
        except Exception as e:
            if "API_KEY_INVALID" in str(e) or "400" in str(e) or "401" in str(e):
                logger.warning("Gemini embedding failed, falling back to OpenAI", error=str(e))
                try:
                    return self.openai_embeddings.embed_documents(texts)
                except Exception as oe:
                    logger.error("OpenAI embedding also failed, falling back to Chroma local", error=str(oe))
                    return None
            logger.error("Failed to generate embeddings", error=str(e))
            return None

    def embed_query(self, text: str) -> list[float]:
        """
        Generates an embedding for a single query string.
        """
        try:
            return self.gemini_embeddings.embed_query(text)
        except Exception as e:
            if "API_KEY_INVALID" in str(e) or "400" in str(e) or "401" in str(e):
                logger.warning("Gemini query embedding failed, falling back to OpenAI")
                try:
                    return self.openai_embeddings.embed_query(text)
                except Exception:
                    logger.error("OpenAI query embedding failed, falling back to Chroma local")
                    return None
            logger.error("Failed to generate query embedding", error=str(e))
            return None

embedding_service = EmbeddingService()
