from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from backend.app.core.config import settings

# Database engine initialization
# In Docker, DATABASE_URL should be: postgresql://user:pass@db:5432/db
if settings.DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set and could not be assembled.")

engine = create_engine(
    settings.DATABASE_URL, echo=True if settings.APP_ENV == "development" else False
)


def init_db() -> None:
    """Initialize database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting an async-compatible session."""
    with Session(engine) as session:
        yield session
