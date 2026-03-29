import structlog
from backend.app.services.image_scraper import image_scraper_service
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
            
            import asyncio
            from functools import partial

            # --- PHASE 0: Initial Identity (Instant) ---
            logger.info("Phase 0: Initial identity creation", ticker=ticker)
            with Session(engine) as session:
                db_company = session.exec(select(Company).where(Company.ticker == ticker)).first()
                if not db_company:
                    # Instant commit with ticker as name initially
                    db_company = Company(ticker=ticker, name=ticker)
                    session.add(db_company)
                    session.commit()
                    session.refresh(db_company)
                    logger.info("Phase 0: Committed initial identity (ticker only)", ticker=ticker)
                    
                    # Background refinement from registry (non-blocking for this phase)
                    from backend.app.services.sec_search import company_search_service
                    matches = await company_search_service.search(ticker, limit=1)
                    if matches and matches[0]["ticker"] == ticker:
                        db_company.name = matches[0]["name"]
                        session.add(db_company)
                        session.commit()
                        logger.info("Phase 0: Refined identity from registry", ticker=ticker)

            # --- PHASE 1-3: Parallel Data Fetching ---
            # Fetch Metadata, Financials, and Prices concurrently to reduce total latency
            logger.info("Starting parallel data fetch (yfinance)", ticker=ticker)
            
            tasks = [
                yfinance_service.get_company_info(ticker),
                yfinance_service.get_financials(ticker),
                yfinance_service.get_historical_prices(ticker)
            ]
            
            # Run all yf calls in parallel
            company_info, financials, prices = await asyncio.gather(*tasks)
            
            # --- Save Meta Phase ---
            if company_info:
                with Session(engine) as session:
                    db_company = session.exec(select(Company).where(Company.ticker == ticker)).first()
                    if db_company:
                        # Fallback for Mission (First 1-2 sentences of description)
                        if not company_info.get("mission") and company_info.get("description"):
                            desc = company_info["description"]
                            sentences = desc.split(". ")
                            mission = sentences[0].strip()
                            if len(mission) < 50 and len(sentences) > 1:
                                mission = mission + ". " + sentences[1].strip()
                            if not mission.endswith("."):
                                mission += "."
                            company_info["mission"] = mission
                        
                        for key, value in company_info.items():
                            if value and key != "logo_url":
                                setattr(db_company, key, value)
                        session.add(db_company)
                        session.commit()
                        logger.info("Phase 1: Committed metadata enrichment", ticker=ticker)

            # --- Save Financials/Prices Phase ---
            if financials:
                financials_persistence_service.save_financials(ticker, financials)
            if prices:
                financials_persistence_service.save_stock_prices(ticker, prices)
            logger.info("Phase 3: Committed financials and prices", ticker=ticker)

            # --- PHASE 2: Logo Scraping (Variable) ---
            # Logo scraping is now done AFTER metadata is committed so we have the website
            if company_info and company_info.get("website"):
                scraped_logo = image_scraper_service.get_logo_for_ticker(ticker, company_info.get("website"))
                if scraped_logo:
                    with Session(engine) as session:
                        db_company = session.exec(select(Company).where(Company.ticker == ticker)).first()
                        if db_company:
                            db_company.logo_url = scraped_logo
                            session.add(db_company)
                            session.commit()
                            logger.info("Phase 2: Committed logo", ticker=ticker)
            
            # --- PHASE 4: Unstructured Data (SEC EDGAR) ---
            logger.info("Phase 4: Unstructured data ingestion", ticker=ticker)
            
            # 2a. Fetch SEC Filing Sections
            sec_data = await sec_ingestion_service.get_filing_sections(ticker, filing_type)
            sections = sec_data.get("sections", {})
            filing_url = sec_data.get("url")
            
            if not sections:
                logger.warning("No SEC sections found for ingestion", ticker=ticker)
            else:
                # Save primary sections to SQL for reliability
                with Session(engine) as session:
                    db_company = session.exec(select(Company).where(Company.ticker == ticker)).first()
                    if db_company:
                        db_company.risk_factors = sections.get("Item 1A")
                        db_company.business_summary = sections.get("Item 1")
                        db_company.mda_summary = sections.get("Item 7")
                        db_company.latest_filing_url = filing_url
                        session.add(db_company)
                        session.commit()
                        logger.info("Saved SEC sections and URL to PostgreSQL", ticker=ticker)

                # 2b. Process for Vector Store (ChromaDB)
                metadata = {
                    "ticker": ticker, 
                    "filing_type": filing_type,
                    "source_url": filing_url,
                    "accession": sec_data.get("accession")
                }
                chunks = document_processor.process_sections(sections, metadata)
                
                if chunks:
                    documents = [c["content"] for c in chunks]
                    metadatas = [c["metadata"] for c in chunks]
                    ids = [f"{ticker}_{filing_type}_{i}" for i in range(len(chunks))]

                    # 2c. Embed Chunks (with Fallback to local via None)
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
                        logger.error("Chroma storage failed", error=str(embed_e))
            
            # --- FINAL: Mark Ingestion Complete ---
            with Session(engine) as session:
                db_company = session.exec(select(Company).where(Company.ticker == ticker)).first()
                if db_company:
                    db_company.is_ingested = True
                    session.add(db_company)
                    session.commit()
                    logger.info("Ingestion officially marked as complete", ticker=ticker)

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
