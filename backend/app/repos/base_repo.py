import logging
import inspect
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from bson import ObjectId
from bson.errors import InvalidId
from typing import List, Dict, Any, Optional

# Import the custom logger instance
from app.core.logger import logs

class BaseRepo:
    """
    A generic base repository with common database operations.
    This class enforces the soft-delete policy using an 'is_deleted' flag.
    """
    def __init__(self, collection: Collection):
        """
        Initializes the repository with a specific MongoDB collection.
        :param collection: A PyMongo Collection instance.
        """
        self.collection = collection

    def create(self, data: Dict[str, Any]) -> ObjectId:
        """
        Creates a new document in the collection.
        All new documents are automatically set to 'is_deleted: False'.
        """
        try:
            data['is_deleted'] = False
            result = self.collection.insert_one(data)
            return result.inserted_id
        except PyMongoError as e:
            logs.define_logger(level=logging.CRITICAL, loggName=inspect.stack()[0], message=f"Database error during document creation: {e}")
            raise

    def create_many(self, data_list: List[Dict[str, Any]]) -> int:
        """Creates multiple new documents in the collection."""
        if not data_list:
            return 0
        try:
            for doc in data_list:
                doc['is_deleted'] = False
            result = self.collection.insert_many(data_list)
            return len(result.inserted_ids)
        except PyMongoError as e:
            logs.define_logger(level=logging.CRITICAL, loggName=inspect.stack()[0], message=f"Database error during bulk document creation: {e}")
            raise

    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Finds a single non-deleted document by its string ID.
        Returns None if the document is not found or is marked as deleted.
        """
        try:
            return self.collection.find_one({"_id": ObjectId(doc_id), "is_deleted": False})
        except InvalidId:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Invalid ObjectId format for doc_id: '{doc_id}'.")
            return None
        except PyMongoError as e:
            logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Database error finding document by ID '{doc_id}': {e}")
            raise

    def get_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Finds the first non-deleted document that matches the query.
        """
        try:
            query['is_deleted'] = False
            return self.collection.find_one(query)
        except PyMongoError as e:
            logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Database error finding one document with query '{query}': {e}")
            raise

    def get_all(self, query: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
        """
        Finds all non-deleted documents that match the query.
        """
        try:
            query['is_deleted'] = False
            return list(self.collection.find(query))
        except PyMongoError as e:
            logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Database error finding all documents with query '{query}': {e}")
            raise

    def update(self, doc_id: str, update_data: Dict[str, Any]) -> int:
        """
        Updates a document by its string ID.
        Returns the number of documents modified.
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(doc_id)}, 
                {"$set": update_data}
            )
            return result.modified_count
        except InvalidId:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Invalid ObjectId format for doc_id: '{doc_id}'.")
            return 0
        except PyMongoError as e:
            logs.define_logger(level=logging.ERROR, loggName=inspect.stack()[0], message=f"Database error updating document with ID '{doc_id}': {e}")
            raise

    def delete_soft(self, doc_id: str) -> int:
        """
        Soft-deletes a document by setting 'is_deleted' to True.
        This is the standard, recommended way to delete.
        """
        return self.update(doc_id, {"is_deleted": True})
    
    def delete_hard(self, doc_id: str) -> int:
        """
        Permanently deletes a document from the database.
        Use this with caution.
        """
        try:
            result = self.collection.delete_one({"_id": ObjectId(doc_id)})
            return result.deleted_count
        except InvalidId:
            logs.define_logger(level=logging.WARNING, loggName=inspect.stack()[0], message=f"Invalid ObjectId format for doc_id: '{doc_id}'.")
            return 0
        except PyMongoError as e:
            logs.define_logger(level=logging.CRITICAL, loggName=inspect.stack()[0], message=f"Database error during hard delete for document ID '{doc_id}': {e}")
            raise