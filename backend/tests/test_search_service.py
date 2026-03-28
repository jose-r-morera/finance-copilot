import pytest

from backend.app.services.sec_search import CompanySearchService


@pytest.mark.asyncio
async def test_search_ranking() -> None:
    # Mock some data
    CompanySearchService._registry = [
        {"ticker": "AAPL", "name": "Apple Inc.", "cik": "0000320193"},
        {"ticker": "AP", "name": "Ampco-Pittsburgh Corp", "cik": "0000006176"},
        {"ticker": "MSFT", "name": "Microsoft Corp", "cik": "0000789019"},
    ]
    CompanySearchService._is_initialized = True

    # Test exact ticker match
    res1 = await CompanySearchService.search("AAPL")
    assert res1[0]["ticker"] == "AAPL"

    # Test prefix match (ranked)
    res2 = await CompanySearchService.search("AP")
    # "AP" (exact ticker) should be first, then "AAPL" (prefix ticker)
    assert res2[0]["ticker"] == "AP"
    assert res2[1]["ticker"] == "AAPL"

    # Test name search
    res3 = await CompanySearchService.search("Micro")
    assert res3[0]["ticker"] == "MSFT"


@pytest.mark.asyncio
async def test_search_limit() -> None:
    CompanySearchService._registry = [
        {"ticker": str(i), "name": f"Company {i}", "cik": str(i)} for i in range(10)
    ]
    CompanySearchService._is_initialized = True

    res = await CompanySearchService.search("Company", limit=3)
    assert len(res) == 3
