from sqlmodel import Session, create_engine, SQLModel
from backend.app.core.config import settings

# Database engine initialization
# In Docker, DATABASE_URL should be: postgresql://user:pass@db:5432/db
engine = create_engine(
    settings.DATABASE_URL, 
    echo=True if settings.APP_ENV == "development" else False
)

def init_db():
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for getting an async-compatible session."""
    with Session(engine) as session:
        yield session
