from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the Item")
    description: Optional[str] = Field(None, max_length=500, description="Item description")
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    tax: Optional[float] = Field(None, ge=0, description="Tax must be 0 or greater")
    category: Optional[str] = Field(None, description="Item category")

class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    total_price: float
    category: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def __init__(self, **data):
        # Calculate total_price if not provided
        if 'total_price' not in data:
            price = data.get('price', 0)
            tax = data.get('tax', 0) or 0
            data['total_price'] = price + tax
        super().__init__(**data)

class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    tax: Optional[float] = Field(None, ge=0)
    category: Optional[str] = None

class MessageResponse(BaseModel):
    message: str
    item_id: Optional[int] = None