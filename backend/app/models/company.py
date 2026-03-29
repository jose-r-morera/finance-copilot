from datetime import datetime
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class CompanyBase(SQLModel):
    ticker: str = Field(index=True, unique=True)
    name: str
    logo_url: str | None = None
    mission: str | None = None
    description: str | None = None
    industry: str | None = None
    sector: str | None = None
    market_cap: float | None = None
    enterprise_value: float | None = None
    shares_outstanding: float | None = None
    website: str | None = None
    risk_factors: str | None = Field(default=None, sa_column=Column(JSON)) # Use JSON/TEXT for large blocks
    business_summary: str | None = None
    mda_summary: str | None = None
    is_ingested: bool = Field(default=False)


class Company(CompanyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Note: Relationships can be added here once we have the other models defined.


class FinancialStatement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True)
    fiscal_year: int = Field(index=True)
    period: str = Field(default="FY")  # FY (Full Year), Q1, Q2, etc.
    
    # Key Metrics (Explicit fields for easy querying)
    revenue: float | None = None
    net_income: float | None = None
    total_assets: float | None = None
    total_liabilities: float | None = None
    operating_cash_flow: float | None = None
    
    # Store everything else in a dictionary (will be JSON in Postgres)
    all_metrics: dict = Field(default_factory=dict, sa_column=Column(JSON))
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class StockPrice(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id", index=True)
    date: datetime = Field(index=True)
    close_price: float
    volume: float | None = None
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Competitor(SQLModel, table=True):
    # ... (existing Competitor model)
    id: int | None = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id")
    peer_ticker: str
    peer_name: str
    closeness_score: float | None = None  # How similar is it?

    # company: Company = Relationship(back_populates="competitors")
