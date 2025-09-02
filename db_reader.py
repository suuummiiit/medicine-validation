from pymongo import MongoClient
from typing import Optional, Dict, Any

class MedicineDB:
    def __init__(self, connection_string: str = "mongodb+srv://medicine:medicine@medicine.b8gwt4f.mongodb.net", 
                 database_name: str = "medicines", 
                 collection_name: str = "medicines"):
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
    
    def find_by_value(self, value: int) -> Optional[Dict[str, Any]]:
        try:
            document = self.collection.find_one({"value": value})
            return document
        except Exception as e:
            print(f"Error querying database: {e}")
            return None
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        try:
            document = self.collection.find_one({"name": name})
            return document
        except Exception as e:
            print(f"Error querying database: {e}")
            return None
    
    def close_connection(self):
        self.client.close()


# Convenience function for quick usage (by value)
def get_document_by_value(value: int, 
                         connection_string: str = "mongodb+srv://medicine:medicine@medicine.b8gwt4f.mongodb.net",
                         database_name: str = "medicines",
                         collection_name: str = "medicines") -> Optional[Dict[str, Any]]:
    db = MedicineDB(connection_string, database_name, collection_name)
    try:
        result = db.find_by_value(value)
        return result
    finally:
        db.close_connection()


# Convenience function for quick usage (by name)
def get_document_by_name(name: str, 
                        connection_string: str = "mongodb+srv://medicine:medicine@medicine.b8gwt4f.mongodb.net",
                        database_name: str = "medicines",
                        collection_name: str = "medicines") -> Optional[Dict[str, Any]]:
    db = MedicineDB(connection_string, database_name, collection_name)
    try:
        result = db.find_by_name(name)
        return result
    finally:
        db.close_connection()


# Example usage
if __name__ == "__main__":
    # Example 1: By value
    document = get_document_by_value(483920)
    if document:
        print(f"Found by value: {document}")
    else:
        print("Document not found by value")

    # Example 2: By name
    document = get_document_by_name("PANTOAGMA-D")
    if document:
        print(f"Found by name: {document}")
    else:
        print("Document not found by name")
