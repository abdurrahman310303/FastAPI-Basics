from fastapi import APIRouter, HTTPException, status, Query, Path
from typing import List

from ..models.item import ItemResponse
from ..database.fake_db import fake_items_db

router = APIRouter()

@router.get("/categories/{category}/items", response_model=List[ItemResponse])
def get_items_by_category(
    category: str = Path(..., description="Category name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    items = [item for item in fake_items_db.get_all_items() if item.get("category") == category]

    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No items found in category '{category}'"
        )
    
    return items[skip:skip + limit]

@router.get("/categories", response_model=List[str])
def get_categories():
    categories = set()
    for item in fake_items_db.get_all_items():
        if item.get("category"):
            categories.add(item["category"])

    return list(categories)
