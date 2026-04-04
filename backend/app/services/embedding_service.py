import structlog
import torch
from typing import Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from backend.app.core.config import settings

logger = structlog.get_logger(__name__)


class EmbeddingService:
    """
    Service to generate embeddings for text chunks.
    Supports Local (GPU-accelerated), Google Gemini, and OpenAI.
    """

    def __init__(self) -> None:
        self.embeddings: Any

        provider = settings.EMBEDDING_PROVIDER.lower()
        logger.info("Initializing Embedding Service", provider=provider)

        if provider == "google" and settings.GOOGLE_API_KEY:
            self.embeddings = GoogleGenerativeAIEmbeddings(  # type: ignore[assignment]
                model=settings.GEMINI_EMBEDDING_MODEL, google_api_key=settings.GOOGLE_API_KEY  # type: ignore[arg-type]
            )
        elif provider == "openai" and settings.OPENAI_API_KEY:
            self.embeddings = OpenAIEmbeddings(  # type: ignore[assignment]
                model="text-embedding-3-small", api_key=settings.OPENAI_API_KEY  # type: ignore[arg-type]
            )
        else:
            # Local Embedding (Fast, Free, Private)
            # Leveraging GPU if available (User has RTX 4070)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(
                "Using local embeddings", model=settings.LOCAL_EMBEDDING_MODEL, device=device
            )

            self.embeddings = HuggingFaceEmbeddings(
                model_name=settings.LOCAL_EMBEDDING_MODEL,
                model_kwargs={"device": device},
                encode_kwargs={"normalize_embeddings": True},
            )

    def embed_chunks(self, texts: list[str]) -> list[list[float]] | None:
        """
        Generates embeddings for a list of text strings.
        """
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(
                "Failed to generate embeddings", error=str(e), provider=settings.EMBEDDING_PROVIDER
            )
            return None

    def embed_query(self, text: str) -> list[float] | None:
        """
        Generates an embedding for a single query string.
        """
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(
                "Failed to generate query embedding",
                error=str(e),
                provider=settings.EMBEDDING_PROVIDER,
            )
            return None


embedding_service = EmbeddingService()
