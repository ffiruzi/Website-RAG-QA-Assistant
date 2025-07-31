from typing import List, Optional, Type, TypeVar, Generic, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc, desc, func
from pydantic import BaseModel
from app.models.base import TimeStampedBase
import logging

ModelType = TypeVar("ModelType", bound=TimeStampedBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving {self.model.__name__} with id {id}: {str(e)}")
            self.db.rollback()
            return None

    def get_all(self, skip: int = 0, limit: int = 100, order_by: str = "id", sort_order: str = "asc") -> List[
        ModelType]:
        try:
            sort_column = getattr(self.model, order_by, None)
            if sort_column is None:
                sort_column = getattr(self.model, "id")
                logger.warning(f"Sort column {order_by} not found, using 'id' instead")

            sort_method = asc if sort_order.lower() == "asc" else desc
            return self.db.query(self.model).order_by(sort_method(sort_column)).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving all {self.model.__name__}: {str(e)}")
            self.db.rollback()
            return []

    def get_filtered(self, skip: int = 0, limit: int = 100, order_by: str = "id", sort_order: str = "asc", **filters) -> \
    List[ModelType]:
        """Get filtered entities with pagination and sorting."""
        try:
            # Get sort column
            sort_column = getattr(self.model, order_by, None)
            if sort_column is None:
                sort_column = getattr(self.model, "id")
                logger.warning(f"Sort column {order_by} not found, using 'id' instead")

            # Build query
            query = self.db.query(self.model)

            # Apply filters - only use valid model attributes
            valid_filters = {}
            for key, value in filters.items():
                if hasattr(self.model, key):
                    valid_filters[key] = value
                else:
                    logger.warning(f"Filter attribute {key} not found on {self.model.__name__}")

            if valid_filters:
                query = query.filter_by(**valid_filters)

            # Apply sorting and pagination
            sort_method = asc if sort_order.lower() == "asc" else desc
            return query.order_by(sort_method(sort_column)).offset(skip).limit(limit).all()

        except SQLAlchemyError as e:
            logger.error(f"Error retrieving filtered {self.model.__name__}: {str(e)}")
            self.db.rollback()
            return []

    def count_filtered(self, **filters) -> int:
        """Count filtered entities."""
        try:
            # Build query
            query = self.db.query(func.count(self.model.id))

            # Apply filters - only use valid model attributes
            valid_filters = {}
            for key, value in filters.items():
                if hasattr(self.model, key):
                    valid_filters[key] = value
                else:
                    logger.warning(f"Filter attribute {key} not found on {self.model.__name__}")

            if valid_filters:
                query = query.filter_by(**valid_filters)

            return query.scalar() or 0

        except SQLAlchemyError as e:
            logger.error(f"Error counting filtered {self.model.__name__}: {str(e)}")
            self.db.rollback()
            return 0

    def create(self, obj_in: CreateSchemaType) -> Optional[ModelType]:
        try:
            # Handle when obj_in is already a dict
            if isinstance(obj_in, dict):
                obj_data = obj_in
            # Handle when obj_in is a Pydantic model (either v1 or v2)
            else:
                obj_data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in.dict()

            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            self.db.rollback()
            return None

    def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        try:
            db_obj = self.get(id)
            if db_obj is None:
                return None

            # Handle when obj_in is already a dict
            if isinstance(obj_in, dict):
                update_data = obj_in
            # Handle when obj_in is a Pydantic model (either v1 or v2)
            else:
                update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in.dict(
                    exclude_unset=True)

            for field in update_data:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, update_data[field])

            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} with id {id}: {str(e)}")
            self.db.rollback()
            return None

    def delete(self, id: int) -> bool:
        try:
            db_obj = self.get(id)
            if db_obj is None:
                return False

            self.db.delete(db_obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__} with id {id}: {str(e)}")
            self.db.rollback()
            return False

    def filter_by(self, **kwargs) -> List[ModelType]:
        try:
            return self.db.query(self.model).filter_by(**kwargs).all()
        except SQLAlchemyError as e:
            logger.error(f"Error filtering {self.model.__name__} by {kwargs}: {str(e)}")
            self.db.rollback()
            return []