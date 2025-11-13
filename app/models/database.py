# Kết nối MongoDB + tiện ích lấy collection (Singleton nhẹ)
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
            cls._instance.db_name = "noteapp"
            cls._instance.uri = "mongodb://localhost:27017/"
        return cls._instance

    def connect(self, connection_string=None, db_name=None) -> bool:
        """Mở kết nối nếu chưa mở. Gọi lại nhiều lần cũng an toàn."""
        if connection_string:
            self.uri = connection_string
        if db_name:
            self.db_name = db_name

        if self.client and self.db:
            # đã kết nối rồi
            return True

        try:
            self.client = MongoClient(self.uri)
            # ping để chắc chắn kết nối OK
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            print(f"✓ Connected to MongoDB: {self.db_name}")
            return True
        except ConnectionFailure as e:
            self.client = None
            self.db = None
            print(f"✗ MongoDB connection failed: {e}")
            return False

    @property
    def is_connected(self) -> bool:
        return self.client is not None and self.db is not None

    def get_collection(self, collection_name):
        """Bảo đảm đã connect trước khi trả về collection."""
        if not self.is_connected:
            ok = self.connect()
            if not ok:
                raise RuntimeError("Cannot connect to MongoDB. Check server/URI.")
        return self.db[collection_name]

    def close(self):
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            print("Database connection closed")
