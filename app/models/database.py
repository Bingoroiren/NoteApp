"""
Database connection and management module
"""
import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one database connection"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection"""
        if self._client is None:
            try:
                mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
                db_name = os.getenv('DB_NAME', 'noteapp_db')
                
                self._client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
                self._db = self._client[db_name]
                
                # Test connection
                self._client.server_info()
                logger.info(f"Successfully connected to MongoDB: {db_name}")
                
                # Create indexes
                self._create_indexes()
                
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Notes collection indexes
            notes = self._db.notes
            notes.create_index([("title", "text"), ("content", "text")])
            notes.create_index([("created_date", DESCENDING)])
            notes.create_index([("due_date", ASCENDING)])
            notes.create_index([("tags", ASCENDING)])
            notes.create_index([("category", ASCENDING)])
            notes.create_index([("is_starred", DESCENDING)])
            notes.create_index([("priority", ASCENDING)])
            
            # Attachments collection indexes
            attachments = self._db.attachments
            attachments.create_index([("note_id", ASCENDING)])
            
            # Audit log indexes
            audit = self._db.audit_log
            audit.create_index([("timestamp", DESCENDING)])
            audit.create_index([("note_id", ASCENDING)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {str(e)}")
    
    def get_database(self):
        """Get database instance"""
        return self._db
    
    def get_collection(self, collection_name):
        """Get a specific collection"""
        return self._db[collection_name]
    
    def close_connection(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            logger.info("Database connection closed")
    
    def test_connection(self):
        """Test if database connection is active"""
        try:
            self._client.server_info()
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {str(e)}")
            return False
    
    def backup_database(self, backup_path=None):
        """Create a backup of the database"""
        try:
            if backup_path is None:
                backup_path = os.getenv('BACKUP_LOCATION', './backups/')
            
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_path, f"backup_{timestamp}.json")
            
            # Export all collections
            import json
            backup_data = {}
            
            for collection_name in self._db.list_collection_names():
                collection = self._db[collection_name]
                documents = list(collection.find())
                
                # Convert ObjectId to string
                for doc in documents:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                
                backup_data[collection_name] = documents
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Backup created successfully: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return None
    
    def restore_database(self, backup_file):
        """Restore database from a backup file"""
        try:
            import json
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            for collection_name, documents in backup_data.items():
                collection = self._db[collection_name]
                
                if documents:
                    # Clear existing data
                    collection.delete_many({})
                    # Insert backup data
                    collection.insert_many(documents)
            
            logger.info(f"Database restored successfully from: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {str(e)}")
            return False
    
    def get_statistics(self):
        """Get database statistics"""
        try:
            stats = {
                'total_notes': self._db.notes.count_documents({}),
                'starred_notes': self._db.notes.count_documents({'is_starred': True}),
                'archived_notes': self._db.notes.count_documents({'is_archived': True}),
                'total_attachments': self._db.attachments.count_documents({}),
                'database_size': self._client.admin.command('dbstats')['dataSize']
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}


# Create global database instance
db_instance = Database()