from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from .database import ItemDB
from ..models.item import Item, ItemUpdate

class ItemCRUD:
    def get_all_items(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100, 
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[ItemDB]:
        query = db.query(ItemDB)
        
        if category:
            query = query.filter(ItemDB.category == category)
        
        if min_price is not None:
            query = query.filter(ItemDB.price >= min_price)
            
        if max_price is not None:
            query = query.filter(ItemDB.price <= max_price)
        
        return query.offset(skip).limit(limit).all()

    def get_item_by_id(self, db: Session, item_id: int) -> Optional[ItemDB]:
        return db.query(ItemDB).filter(ItemDB.id == item_id).first()

    def create_item(self, db: Session, item: Item) -> ItemDB:
        db_item = ItemDB(
            name=item.name,
            description=item.description,
            price=item.price,
            tax=item.tax or 0.0,
            category=item.category,
            created_at=datetime.utcnow()
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def update_item(self, db: Session, item_id: int, item_update: ItemUpdate) -> Optional[ItemDB]:
        db_item = self.get_item_by_id(db, item_id)
        if not db_item:
            return None
        
        update_data = item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db_item.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_item)
        return db_item

    def delete_item(self, db: Session, item_id: int) -> Optional[ItemDB]:
        db_item = self.get_item_by_id(db, item_id)
        if db_item:
            db.delete(db_item)
            db.commit()
            return db_item
        return None

    def get_categories(self, db: Session) -> List[str]:
        categories = db.query(ItemDB.category).filter(ItemDB.category.isnot(None)).distinct().all()
        return [cat[0] for cat in categories if cat[0]]

    def search_items(
        self, 
        db: Session, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ItemDB]:
        search = f"%{query.lower()}%"
        return db.query(ItemDB).filter(
            (ItemDB.name.ilike(search)) | 
            (ItemDB.description.ilike(search))
        ).offset(skip).limit(limit).all()

# Create CRUD instance
item_crud = ItemCRUD()
