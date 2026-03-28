from datetime import datetime

from sqlmodel import Field, SQLModel


class CompanyBase(SQLModel):
    ticker: str = Field(index=True, unique=True)
    name: str
    logo_url: str | None = None
    mission: str | None = None
    description: str | None = None
    industry: str | None = None
    sector: str | None = None


class Company(CompanyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (to be added in later phases)
    # competitors: List["Competitor"] = Relationship(...)
    # reports: List["Report"] = Relationship(...)


class Competitor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.id")
    peer_ticker: str
    peer_name: str
    closeness_score: float | None = None  # How similar is it?

    # company: Company = Relationship(back_populates="competitors")
