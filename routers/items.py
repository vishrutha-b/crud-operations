from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter(prefix="/items", tags=["Items"])


@router.get("/", response_model=List[schemas.ItemResponse], summary="Get all items")
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve a paginated list of all items."""
    return crud.get_items(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=schemas.ItemResponse, summary="Get item by ID")
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Retrieve a single item by its ID."""
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return db_item


@router.post(
    "/",
    response_model=schemas.ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create item",
)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    """Create a new item in the database."""
    return crud.create_item(db, item)


@router.put("/{item_id}", response_model=schemas.ItemResponse, summary="Update item")
def update_item(item_id: int, item: schemas.ItemUpdate, db: Session = Depends(get_db)):
    """Update an existing item (supports partial updates)."""
    db_item = crud.update_item(db, item_id, item)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return db_item


@router.delete("/{item_id}", response_model=schemas.ItemResponse, summary="Delete item")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete an item by its ID."""
    db_item = crud.delete_item(db, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found"
        )
    return db_item
