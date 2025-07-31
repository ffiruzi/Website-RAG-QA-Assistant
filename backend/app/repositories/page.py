from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.page import Page
from app.schemas.page import PageCreate, PageUpdate
from app.repositories.base import BaseRepository


class PageRepository(BaseRepository[Page, PageCreate, PageUpdate]):
    def __init__(self, db: Session):
        super().__init__(Page, db)

    def get_by_url(self, url: str) -> Optional[Page]:
        """Get a page by URL."""
        return self.db.query(Page).filter(Page.url == url).first()

    def get_by_website_id(self, website_id: int) -> List[Page]:
        """Get all pages for a website."""
        return self.db.query(Page).filter(Page.website_id == website_id).all()

    def get_indexed_count(self, website_id: int) -> int:
        """Get the count of indexed pages for a website."""
        return self.db.query(Page).filter(
            Page.website_id == website_id,
            Page.is_indexed == True
        ).count()

    def get_crawled_count(self, website_id: int) -> int:
        """Get the count of crawled pages for a website."""
        return self.db.query(Page).filter(
            Page.website_id == website_id,
            Page.last_crawled_at != None
        ).count()