from fastapi import FastAPI, HTTPException, status, Query, Path, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title = "FastAPI Learning Project",
    description = "A comprehensive FastAPI Project",
    version = "1.0.0"
)

class Item(BaseModel):
    name : str = Field(..., min_length=1, max_length=100, description = "Name of the Item")
    description : Optional[str] = Field(None, max_length=500, description="Item description")
    price : float = Field(..., gt=0, description="Price must be greater than 0")
    tax: Optional[float] = Field(None, ge=0, description="Tax must be 0 or greater")
    category : Optional[str] = Field(None, description="Item category")


class ItemResponse(BaseModel):
    id : int
    name : str
    description : Optional[str] = None
    price : float
    tax : Optional[float] = None
    total_price : float
    category : Optional[str] = None
    created_at : datetime


class ItemUpdate(BaseModel):

    name : Optional[str] = Field(None, min_length=1, max_length=100)
    description : Optional[str] = Field(None, max_length=500)
    price : Optional[float] = Field(None, gt=0)
    tax : Optional[float] = Field(None, ge=0)
    category : Optional[str] = None


class MessageResponse(BaseModel):
    message : str
    item_id : Optional[int] = None


fake_items_db = {}
item_counter = 1


def get_current_timestamp():
    return datetime.now()


@app.get('/',response_model=dict)
def read_root():
    return {
        "Hello" : "This is my first FastAPI Practice",
        "Version" : "1.0.0",
        "edpoints" : {
            "docs" : "/docs",
            "items" : "/items/",
            "health" : "/health"
        }
    }

@app.get("/health", response_model=dict)
def health_check():
    return {
        "status" : "healthy",
        "timestamp" : datetime.now(),
        "total_items" : len(fake_items_db)
    }

@app.get("/items/", response_model=List[ItemResponse])
def read_items(
    skip : int = Query(0, ge=0, description = "Number of items to skip"),
    limit : int = Query(10, ge=1, le=100, description="Maximum number of items to be returned"),
    category : Optional[str] = Query(None, description="Filter by category"),
    min_price : Optional[float] = Query(None, ge=0, description="Minimum Price filter"),
    max_price : Optional[float] = Query(None, ge=0, description="Maximum Price filter")
):
    items = list(fake_items_db.values())

    if category:
        items = [item for item in items if item.get("category") == category]
    
    if min_price is not None:
        items = [item for item in items if item.get("price", 0) >= min_price]
    
    if max_price is not None:
        items = [item for item in items if item.get("price",0) <= max_price]
    

    items = items[skip:skip + limit]
    
    return items


@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(
    item_id : int = Path(..., gt=0, description="ID of the item to retrieve"),
    include_tax : bool = Query(False, description="Include tax in response")
):
    if item_id not in fake_items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )

    item = fake_items_db[item_id]

    if not include_tax:
        item_copy = item.copy()
        item_copy["tax"] = None
        item_copy["total_price"] = item_copy["price"]
        return item_copy
    
    return item



@app.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item : Item, 
    timestamp : datetime = Depends(get_current_timestamp)
):
    global item_counter

    total_price = item.price + (item.tax or 0)

    new_item = ItemResponse(
        id=item_counter,
        name=item.name,
        description=item.description,
        price=item.price,
        tax=item.tax,
        total_price=total_price,
        category=item.category,
        created_at=timestamp
    )

    fake_items_db[item_counter] = new_item.dict()
    item_counter += 1

    return new_item



@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_update: ItemUpdate,
    item_id: int = Path(..., gt=0, description="ID of the item to update"),
    timestamp: datetime = Depends(get_current_timestamp)
):
    
    if item_id not in fake_items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    existing_item = fake_items_db[item_id].copy()

    update_data = item_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        existing_item[field] = value

    existing_item["total_price"] = existing_item["price"] + (existing_item.get("tax") or 0)
    existing_item["updated_at"] = timestamp

    fake_items_db[item_id] = existing_item

    return ItemResponse(**existing_item)


@app.delete("/items/{item_id}",response_model=MessageResponse)
def delete_item(
    item_id : int = Path(..., gt=0, description="ID of the item to delete")
):
    if item_id not in fake_items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    deleted_item = fake_items_db.pop(item_id)

    return MessageResponse(
        message=f"Item '{deleted_item['name']}' deleted successfully",
        item_id=item_id
    )

@app.get("/categories/{category}/items", response_model=List[ItemResponse])
def get_items_by_category(
    category : str = Path(..., description="Category name"),
    skip : int = Query(0, ge=0),
    limit : int = Query(10, ge=1, le=100)
):
    items = [item for item in fake_items_db.values() if item.get("category") == category]

    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No items found in category '{category}'"
        )
    
    return items[skip:skip + limit]

@app.get("/categories", response_model=List[str])
def get_categories():
    categories = set()
    for item in fake_items_db.values():
        if item.get("category"):
            categories.add(item["category"])

    return list(categories)


@app.get("/search/", response_model=List[ItemResponse])
def search_items(
    q : str = Query(..., min_length=1, description="Search query"),
    skip : int = Query(0, ge=0),
    limit : int = Query(10, ge=1, le=100)
):
    matching_items = []

    for item in fake_items_db.values():
        if (q.lower() in item["name"].lower() or 
            (item.get("description") and q.lower() in item["description"].lower())):
            matching_items.append(item)
    
    if not matching_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No items found matching '{q}'"
        )
    return matching_items[skip:skip + limit]