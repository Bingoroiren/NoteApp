# Model thao tác dữ liệu Note
from bson import ObjectId
from app.models.database import Database


class NoteModel:
    def __init__(self):
        self.db = Database()
        self.db.connect()  # ❗ bắt buộc
        self.collection = self.db.get_collection("notes")

    # CREATE
    def create(self, title, category="My Day", content="", important=False):
        doc = {
            "title": title,
            "content": content,
            "category": category,
            "important": important,
            "completed": False,
        }
        self.collection.insert_one(doc)
        return doc

    # READ
    def read_all(self, category=None):
        q = {"category": category} if category else {}
        return list(self.collection.find(q))

    # UPDATE: toggle done
    def toggle_completed(self, note_id):
        oid = ObjectId(note_id) if not isinstance(note_id, ObjectId) else note_id
        doc = self.collection.find_one({"_id": oid})
        if not doc:
            return
        new_state = not doc.get("completed", False)
        self.collection.update_one({"_id": oid}, {"$set": {"completed": new_state}})

    # (tuỳ chọn) DELETE
    def delete(self, note_id):
        oid = ObjectId(note_id) if not isinstance(note_id, ObjectId) else note_id
        self.collection.delete_one({"_id": oid})
