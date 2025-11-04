# Lớp đại diện cho ghi chú
from datetime import datetime
from bson.objectid import ObjectId
from app.models.database import Database

class NoteModel:
    def __init__(self):
        self.db = Database()
        self.collection = self.db.get_collection("notes")
    
    def create(self, title, content, category="Ngày của Tôi", important=False, completed=False):
        note = {
            "title": title,
            "content": content,
            "category": category,
            "important": important,
            "completed": completed,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        result = self.collection.insert_one(note)
        return str(result.inserted_id)
    
    def read_all(self, category=None, important=None, completed=None):
        query = {}
        if category:
            query["category"] = category
        if important is not None:
            query["important"] = important
        if completed is not None:
            query["completed"] = completed
        
        notes = list(self.collection.find(query).sort("created_at", -1))
        # Convert ObjectId to string
        for note in notes:
            note["_id"] = str(note["_id"])
        return notes
    
    def read_by_id(self, note_id):
        note = self.collection.find_one({"_id": ObjectId(note_id)})
        if note:
            note["_id"] = str(note["_id"])
        return note
    
    def update(self, note_id, **kwargs):
        kwargs["updated_at"] = datetime.now()
        result = self.collection.update_one(
            {"_id": ObjectId(note_id)},
            {"$set": kwargs}
        )
        return result.modified_count > 0
    
    def delete(self, note_id):
        result = self.collection.delete_one({"_id": ObjectId(note_id)})
        return result.deleted_count > 0
    
    def toggle_completed(self, note_id):
        note = self.read_by_id(note_id)
        if note:
            return self.update(note_id, completed=not note["completed"])
        return False
    
    def toggle_important(self, note_id):
        note = self.read_by_id(note_id)
        if note:
            return self.update(note_id, important=not note["important"])
        return False