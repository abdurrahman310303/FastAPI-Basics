from fastapi import APIRouter, HTTPException, status, Query
from typing import List

from ..models.item import ItemResponse
from ..database.fake_db import fake_items_db

router = APIRouter()

@router.get("/search/", response_model=List[ItemResponse])
def search_items(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    matching_items = []

    for item in fake_items_db.get_all_items():
        if (q.lower() in item["name"].lower() or 
            (item.get("description") and q.lower() in item["description"].lower())):
            matching_items.append(item)
    
    if not matching_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No items found matching '{q}'"
        )
    
    return matching_items[skip:skip + limit]
