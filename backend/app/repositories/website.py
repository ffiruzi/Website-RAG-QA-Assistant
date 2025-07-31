from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.website import Website
from app.schemas.website import WebsiteCreate, WebsiteUpdate
from app.repositories.base import BaseRepository


class WebsiteRepository(BaseRepository[Website, WebsiteCreate, WebsiteUpdate]):
    def __init__(self, db: Session):
        super().__init__(Website, db)

    def get_by_url(self, url: str) -> Optional[Website]:
        return self.db.query(Website).filter(Website.url == url).first()

    def get_active_websites(self) -> List[Website]:
        return self.db.query(Website).filter(Website.is_active == True).all()