from fastapi import APIRouter, HTTPException, status, Query, Path, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from ..models.item import Item, ItemResponse, ItemUpdate, MessageResponse
from ..database.database import get_db
from ..database.crud import item_crud

router = APIRouter()

@router.get("/items/", response_model=List[ItemResponse])
def read_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items to be returned"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum Price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum Price filter"),
    db: Session = Depends(get_db)
):
    items = item_crud.get_all_items(
        db=db, 
        skip=skip, 
        limit=limit, 
        category=category, 
        min_price=min_price, 
        max_price=max_price
    )
    
    # Convert to response format with total_price
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

@router.get("/items/{item_id}", response_model=ItemResponse)
def read_item(
    item_id: int = Path(..., gt=0, description="ID of the item to retrieve"),
    include_tax: bool = Query(False, description="Include tax in response"),
    db: Session = Depends(get_db)
):
    db_item = item_crud.get_item_by_id(db, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )

    total_price = db_item.price + (db_item.tax or 0)
    
    response_item = ItemResponse(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        tax=db_item.tax if include_tax else None,
        total_price=total_price if include_tax else db_item.price,
        category=db_item.category,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at
    )
    
    return response_item

@router.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item: Item,
    db: Session = Depends(get_db)
):
    db_item = item_crud.create_item(db=db, item=item)
    total_price = db_item.price + (db_item.tax or 0)
    
    return ItemResponse(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        tax=db_item.tax,
        total_price=total_price,
        category=db_item.category,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at
    )

@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_update: ItemUpdate,
    item_id: int = Path(..., gt=0, description="ID of the item to update"),
    db: Session = Depends(get_db)
):
    db_item = item_crud.update_item(db=db, item_id=item_id, item_update=item_update)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    total_price = db_item.price + (db_item.tax or 0)
    
    return ItemResponse(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        tax=db_item.tax,
        total_price=total_price,
        category=db_item.category,
        created_at=db_item.created_at,
        updated_at=db_item.updated_at
    )

@router.delete("/items/{item_id}", response_model=MessageResponse)
def delete_item(
    item_id: int = Path(..., gt=0, description="ID of the item to delete"),
    db: Session = Depends(get_db)
):
    db_item = item_crud.delete_item(db=db, item_id=item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return MessageResponse(
        message=f"Item '{db_item.name}' deleted successfully",
        item_id=item_id
    )
