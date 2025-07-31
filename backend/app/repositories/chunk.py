from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.chunk import Chunk
from app.schemas.chunk import ChunkCreate, ChunkUpdate
from app.repositories.base import BaseRepository


class ChunkRepository(BaseRepository[Chunk, ChunkCreate, ChunkUpdate]):
    def __init__(self, db: Session):
        super().__init__(Chunk, db)

    def get_by_page_id(self, page_id: int) -> List[Chunk]:
        """Get all chunks for a page."""
        return self.db.query(Chunk).filter(Chunk.page_id == page_id).all()

    def get_count_by_page_id(self, page_id: int) -> int:
        """Get the count of chunks for a page."""
        return self.db.query(Chunk).filter(Chunk.page_id == page_id).count()

    def delete_by_page_id(self, page_id: int) -> int:
        """Delete all chunks for a page."""
        return self.db.query(Chunk).filter(Chunk.page_id == page_id).delete()