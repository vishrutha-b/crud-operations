from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the item")
    description: Optional[str] = Field(None, description="Optional description")
    price: int = Field(..., ge=0, description="Price in cents (must be >= 0)")
    is_available: bool = Field(True, description="Whether the item is available")


class ItemCreate(ItemBase):
    """Schema for creating a new item."""

    pass


class ItemUpdate(BaseModel):
    """Schema for updating an item (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None


class ItemResponse(ItemBase):
    """Schema for item responses including DB fields."""

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
