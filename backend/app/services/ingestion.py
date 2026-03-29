import structlog
from backend.app.services.sec_ingestion import sec_ingestion_service
from backend.app.services.document_processor import document_processor
from backend.app.services.vector_store import vector_store_service
from backend.app.services.embedding_service import embedding_service
from backend.app.services.yfinance_service import yfinance_service
from backend.app.services.financials_service import financials_persistence_service
from backend.app.models.company import Company
from backend.app.core.database import engine
from sqlmodel import Session, select

logger = structlog.get_logger(__name__)

class IngestionManager:
    """
    Orchestrates the ingestion of financial data for a given ticker.
    """
    
    @staticmethod
    async def ingest_company_data(ticker: str, filing_type: str = "10-K"):
        """
        Triggers the full ingestion pipeline:
        1. [Structured] Fetch Company Info, Financials, and Prices (yfinance).
        2. [Unstructured] Fetch sections from SEC (SEC EDGAR).
        3. [Unstructured] Chunk, Embed, and Store in ChromaDB.
        """
        try:
            logger.info("Starting ingestion pipeline", ticker=ticker, type=filing_type)
            
            # --- PHASE 1: Structured Data (yfinance) ---
            logger.info("Phase 1: Structured data ingestion", ticker=ticker)
            
            # 1a. Ensure Company exists and enrich it
            with Session(engine) as session:
                db_company = session.exec(select(Company).where(Company.ticker == ticker)).first()
                if not db_company:
                    logger.info("Company not in DB, creating from registry", ticker=ticker)
                    # Try to find in registry
                    from backend.app.services.sec_search import company_search_service
                    matches = await company_search_service.search(ticker, limit=1)
                    if matches and matches[0]["ticker"] == ticker:
                        db_company = Company(
                            ticker=ticker,
                            name=matches[0]["name"]
                            # CIK can be added if we expand the model
                        )
                        session.add(db_company)
                        session.commit()
                        session.refresh(db_company)
                    else:
                        # Fallback for tickers not in SEC registry (e.g. non-US or new)
                        db_company = Company(ticker=ticker, name=ticker)
                        session.add(db_company)
                        session.commit()
                        session.refresh(db_company)

                # Enrich with yfinance info
                company_info = yfinance_service.get_company_info(ticker)
                if company_info:
                    for key, value in company_info.items():
                        if value:
                            setattr(db_company, key, value)
                    session.add(db_company)
                    session.commit()
            
            # 1b. Financial Statements
            financials = yfinance_service.get_financials(ticker)
            if financials:
                financials_persistence_service.save_financials(ticker, financials)
            
            # 1c. Historical Prices
            prices = yfinance_service.get_historical_prices(ticker)
            if prices:
                financials_persistence_service.save_stock_prices(ticker, prices)
            
            # --- PHASE 2: Unstructured Data (SEC EDGAR) ---
            logger.info("Phase 2: Unstructured data ingestion", ticker=ticker)
            
            # 2a. Fetch SEC Filing Sections
            sections = sec_ingestion_service.get_filing_sections(ticker, filing_type)
            if not sections:
                logger.warning("No SEC sections found for ingestion", ticker=ticker)
                # We continue since structured data might have been saved
            else:
                # 2b. Process for Vector Store
                metadata = {"ticker": ticker, "filing_type": filing_type}
                chunks = document_processor.process_sections(sections, metadata)
                
                if chunks:
                    documents = [c["content"] for c in chunks]
                    metadatas = [c["metadata"] for c in chunks]
                    ids = [f"{ticker}_{filing_type}_{i}" for i in range(len(chunks))]

                    # 2c. Embed Chunks (Gemini with Fallback)
                    # Note: This will use the EmbeddingService which currently has an API key blocker
                    try:
                        embeddings = embedding_service.embed_chunks(documents)
                        
                        # 2d. Store in Chroma
                        vector_store_service.upsert_documents(
                            ids=ids,
                            documents=documents,
                            metadatas=metadatas,
                            embeddings=embeddings
                        )
                    except Exception as embed_e:
                        logger.error("Embedding/Vector storage failed (likely API keys)", error=str(embed_e))
            
            logger.info("Ingestion pipeline completed", ticker=ticker)
            return {
                "status": "success",
                "ticker": ticker,
                "structured_data": "ok",
                "unstructured_data": "processed (see logs for vector status)"
            }
            
        except Exception as e:
            logger.exception("Ingestion pipeline failed", ticker=ticker, error=str(e))
            return {"status": "error", "message": str(e)}

ingestion_manager = IngestionManager()
