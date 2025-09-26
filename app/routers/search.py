from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session
from typing import List

from ..models.item import ItemResponse
from ..database.database import get_db
from ..database.crud import item_crud

router = APIRouter()

@router.get("/search/", response_model=List[ItemResponse])
def search_items(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items = item_crud.search_items(db=db, query=q, skip=skip, limit=limit)
    
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No items found matching '{q}'"
        )
    
    # Convert to response format
    response_items = []
    for item in items:
        total_price = item.price + (item.tax or 0)
        response_items.append(ItemResponse(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            tax=item.tax,
            total_price=total_price,
            category=item.category,
            created_at=item.created_at,
            updated_at=item.updated_at
        ))
    
    return response_items
