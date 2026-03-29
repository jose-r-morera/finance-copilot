import structlog
from backend.app.services.sec_ingestion import sec_ingestion_service
from backend.app.services.document_processor import document_processor
from backend.app.services.vector_store import vector_store_service
from backend.app.services.embedding_service import embedding_service

logger = structlog.get_logger(__name__)

class IngestionManager:
    """
    Orchestrates the ingestion of financial data for a given ticker.
    """
    
    @staticmethod
    async def ingest_company_data(ticker: str, filing_type: str = "10-K"):
        """
        Triggers the full ingestion pipeline:
        1. Fetch sections from SEC.
        2. Chunk sections.
        3. Embed chunks (Gemini).
        4. Store in Vector Database (Chroma).
        """
        try:
            logger.info("Starting ingestion pipeline", ticker=ticker, type=filing_type)
            
            # 1. Fetch SEC Filing Sections
            sections = sec_ingestion_service.get_filing_sections(ticker, filing_type)
            if not sections:
                logger.error("No sections found for ingestion", ticker=ticker)
                return {"status": "error", "message": f"No {filing_type} filings found for {ticker}"}
            
            # 2. Process for Vector Store
            metadata = {"ticker": ticker, "filing_type": filing_type}
            chunks = document_processor.process_sections(sections, metadata)
            if not chunks:
                logger.warning("No chunks generated from filing", ticker=ticker)
                return {"status": "error", "message": "No processable content found in filing"}
            
            documents = [c["content"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            ids = [f"{ticker}_{filing_type}_{i}" for i in range(len(chunks))]

            # 3. Embed Chunks (Gemini)
            embeddings = embedding_service.embed_chunks(documents)
            
            # 4. Store in Chroma
            vector_store_service.upsert_documents(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            logger.info("Ingestion pipeline completed successfully", ticker=ticker)
            return {
                "status": "success",
                "ticker": ticker,
                "sections_processed": list(sections.keys()),
                "total_chunks": len(chunks)
            }
            
        except Exception as e:
            logger.exception("Ingestion pipeline failed", ticker=ticker, error=str(e))
            return {"status": "error", "message": str(e)}

ingestion_manager = IngestionManager()
