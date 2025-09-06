from pymongo.collection import Collection
from typing import Any, Dict, List, Optional

class BaseRepo:
    """
    Base repository with generic CRUD operations for MongoDB.
    """

    def __init__(self, collection: Collection):
        """
        Initializes the repository with a MongoDB collection.

        :param collection: A PyMongo Collection instance.
        """
        self._collection = collection

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new document in the collection.

        :param data: A dictionary representing the document to create.
        :return: The created document.
        """
        inserted = self._collection.insert_one(data)
        created_doc = self._collection.find_one({"_id": inserted.inserted_id})
        return created_doc

    def find_one_by(self, filter_query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Finds a single document matching the filter query.

        :param filter_query: A dictionary for the find query.
        :return: A single document or None.
        """
        return self._collection.find_one(filter_query)

    def find_by(self, filter_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Finds all documents matching the filter query.

        :param filter_query: A dictionary for the find query.
        :return: A list of documents.
        """
        return list(self._collection.find(filter_query))

    def update_one(self, filter_query: Dict[str, Any], update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Updates a single document matching the filter query.

        :param filter_query: A dictionary to find the document to update.
        :param update_data: A dictionary with the data to update.
        :return: The updated document or None.
        """
        self._collection.update_one(filter_query, {"$set": update_data})
        return self.find_one_by(filter_query)

    def delete_one(self, filter_query: Dict[str, Any]) -> bool:
        """
        Deletes a single document matching the filter query.

        :param filter_query: A dictionary to find the document to delete.
        :return: True if a document was deleted, False otherwise.
        """
        result = self._collection.delete_one(filter_query)
        return result.deleted_count > 0