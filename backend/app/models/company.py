from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class CompanyBase(SQLModel):
    ticker: str = Field(index=True, unique=True)
    name: str
    logo_url: Optional[str] = None
    mission: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None

class Company(CompanyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships (to be added in later phases)
    # competitors: List["Competitor"] = Relationship(...)
    # reports: List["Report"] = Relationship(...)

class Competitor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id")
    peer_ticker: str
    peer_name: str
    closeness_score: Optional[float] = None # How similar is it?
    
    # company: Company = Relationship(back_populates="competitors")
