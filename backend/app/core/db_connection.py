import os
from pymongo import MongoClient
from pymongo.database import Database
from .config import settings # Assuming config is in the same core directory
from dotenv import load_dotenv

load_dotenv()

class MongoManager:
    """Manages the single connection pool to the MongoDB database."""
    def __init__(self, mongo_url: str):
        print("Initializing MongoDB connection pool...")
        try:
            self.client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping') # Verify connection
            print("MongoDB connection successful.")
        except Exception as e:
            print(f"FATAL: Error connecting to MongoDB: {e}")
            self.client = None
    
    def get_client(self) -> MongoClient:
        if not self.client:
            raise ConnectionError("MongoDB client is not available.")
        return self.client

    def get_database(self) -> Database:
        """Returns the database instance specified in settings."""
        return self.get_client()[settings.MONGODB_DB]

    def close_connection(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

# --- Singleton Instance ---
# This part runs when the module is imported, creating one connection manager.
mongo_url = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_manager = MongoManager(mongo_url=mongo_url)

# --- Dependency Function ---
# This is the function that your repository needs to import.
def get_db() -> Database:
    """FastAPI dependency to get the database instance."""
    return mongo_manager.get_database()
