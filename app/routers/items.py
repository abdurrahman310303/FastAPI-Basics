from fastapi import APIRouter, HTTPException, status, Query, Path, Depends
from typing import List, Optional
from datetime import datetime

from ..models.item import Item, ItemResponse, ItemUpdate, MessageResponse
from ..database.fake_db import fake_items_db, get_current_timestamp

router = APIRouter()

@router.get("/items/", response_model=List[ItemResponse])
def read_items(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of items to be returned"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum Price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum Price filter")
):
    items = fake_items_db.get_all_items()

    if category:
        items = [item for item in items if item.get("category") == category]
    
    if min_price is not None:
        items = [item for item in items if item.get("price", 0) >= min_price]
    
    if max_price is not None:
        items = [item for item in items if item.get("price", 0) <= max_price]

    items = items[skip:skip + limit]
    
    return items

@router.get("/items/{item_id}", response_model=ItemResponse)
def read_item(
    item_id: int = Path(..., gt=0, description="ID of the item to retrieve"),
    include_tax: bool = Query(False, description="Include tax in response")
):
    if not fake_items_db.item_exists(item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )

    item = fake_items_db.get_item(item_id)

    if not include_tax:
        item_copy = item.copy()
        item_copy["tax"] = None
        item_copy["total_price"] = item_copy["price"]
        return item_copy
    
    return item

@router.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item: Item, 
    timestamp: datetime = Depends(get_current_timestamp)
):
    total_price = item.price + (item.tax or 0)

    new_item = ItemResponse(
        id=fake_items_db.item_counter,
        name=item.name,
        description=item.description,
        price=item.price,
        tax=item.tax,
        total_price=total_price,
        category=item.category,
        created_at=timestamp
    )

    item_dict = new_item.dict()
    item_id = fake_items_db.create_item(item_dict)
    item_dict["id"] = item_id

    return new_item

@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_update: ItemUpdate,
    item_id: int = Path(..., gt=0, description="ID of the item to update"),
    timestamp: datetime = Depends(get_current_timestamp)
):
    if not fake_items_db.item_exists(item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    existing_item = fake_items_db.get_item(item_id).copy()
    update_data = item_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        existing_item[field] = value

    existing_item["total_price"] = existing_item["price"] + (existing_item.get("tax") or 0)
    existing_item["updated_at"] = timestamp

    fake_items_db.update_item(item_id, existing_item)

    return ItemResponse(**existing_item)

@router.delete("/items/{item_id}", response_model=MessageResponse)
def delete_item(
    item_id: int = Path(..., gt=0, description="ID of the item to delete")
):
    if not fake_items_db.item_exists(item_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    deleted_item = fake_items_db.delete_item(item_id)

    return MessageResponse(
        message=f"Item '{deleted_item['name']}' deleted successfully",
        item_id=item_id
    )
