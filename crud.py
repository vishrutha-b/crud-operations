from typing import List, Optional

from sqlalchemy.orm import Session

import models
import schemas


def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    """Fetch a single item by ID."""
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def get_items(db: Session, skip: int = 0, limit: int = 100) -> List[models.Item]:
    """Fetch a paginated list of all items."""
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_item(db: Session, item: schemas.ItemCreate) -> models.Item:
    """Create a new item."""
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_item(
    db: Session, item_id: int, item: schemas.ItemUpdate
) -> Optional[models.Item]:
    """Update an existing item (partial update supported)."""
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    update_data = item.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, item_id: int) -> Optional[models.Item]:
    """Delete an item by ID. Returns deleted item or None."""
    db_item = get_item(db, item_id)
    if not db_item:
        return None
    db.delete(db_item)
    db.commit()
    return db_item
