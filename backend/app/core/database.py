from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base  # Use this import

from app.core.config import settings

# Create SQLite engine
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()  # This is now from sqlalchemy.orm

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()