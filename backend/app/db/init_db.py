import logging
from sqlalchemy.orm import Session
from app.models.website import Website
from app.core.config import settings

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """Initialize the database with initial data if needed."""
    try:
        # Check if we already have any websites
        website = db.query(Website).first()

        if not website:
            logger.info("Database is empty, creating initial data...")

            # Create a sample website
            sample_website = Website(
                url="https://example.com",
                name="Example Website",
                description="This is a sample website",
                is_active=True,
                sitemap_url="https://example.com/sitemap.xml"
            )

            db.add(sample_website)
            db.commit()
            logger.info("Initial data created")
        else:
            logger.info("Database already contains data, skipping initialization")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        db.rollback()