from typing import Dict, Any
from datetime import datetime

class FakeDatabase:
    def __init__(self):
        self.items_db: Dict[int, Any] = {}
        self.item_counter: int = 1
    
    def get_all_items(self):
        return list(self.items_db.values())
    
    def get_item(self, item_id: int):
        return self.items_db.get(item_id)
    
    def create_item(self, item_data: dict):
        self.items_db[self.item_counter] = item_data
        current_id = self.item_counter
        self.item_counter += 1
        return current_id
    
    def update_item(self, item_id: int, item_data: dict):
        if item_id in self.items_db:
            self.items_db[item_id] = item_data
            return True
        return False
    
    def delete_item(self, item_id: int):
        return self.items_db.pop(item_id, None)
    
    def item_exists(self, item_id: int):
        return item_id in self.items_db

def get_current_timestamp():
    return datetime.now()

fake_items_db = FakeDatabase()
