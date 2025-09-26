from fastapi import APIRouter, HTTPException, status, Query, Path, Depends
from sqlalchemy.orm import Session
from typing import List

from ..models.item import ItemResponse
from ..database.database import get_db
from ..database.crud import item_crud

router = APIRouter()

@router.get("/categories/{category}/items", response_model=List[ItemResponse])
def get_items_by_category(
    category: str = Path(..., description="Category name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    items = item_crud.get_all_items(db=db, skip=skip, limit=limit, category=category)

    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No items found in category '{category}'"
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

@router.get("/categories", response_model=List[str])
def get_categories(db: Session = Depends(get_db)):
    return item_crud.get_categories(db=db)
