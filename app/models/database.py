#kết nối MGDB và CRUD cơ bảnfrom pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
        return cls._instance
    
    def connect(self, connection_string="mongodb://localhost:27017/", db_name="noteapp"):
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            # Test connection
            self.client.admin.command('ping')
            print(f"✓ Connected to MongoDB: {db_name}")
            return True
        except ConnectionFailure as e:
            print(f"✗ MongoDB connection failed: {e}")
            return False
    
    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    def close(self):
        if self.client:
            self.client.close()