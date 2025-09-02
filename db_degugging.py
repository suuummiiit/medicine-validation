from pymongo import MongoClient
from typing import Optional, Dict, Any

class MedicineDB:
    def __init__(self, connection_string: str = "mongodb+srv://medicine:medicine@medicine.b8gwt4f.mongodb.net", 
                 database_name: str = "medicines", 
                 collection_name: str = "medicines"):
        """
        Initialize the MongoDB connection
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
            collection_name: Name of the collection
        """
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]
    
    def find_by_value(self, value: int) -> Optional[Dict[str, Any]]:
        """
        Find a document by its value field
        
        Args:
            value: The value to search for
            
        Returns:
            The document if found, None otherwise
        """
        try:
            document = self.collection.find_one({"value": value})
            return document
        except Exception as e:
            print(f"Error querying database: {e}")
            return None
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find a document by its name field
        
        Args:
            name: The name to search for
            
        Returns:
            The document if found, None otherwise
        """
        try:
            document = self.collection.find_one({"name": name})
            return document
        except Exception as e:
            print(f"Error querying database: {e}")
            return None
    
    def close_connection(self):
        """Close the MongoDB connection"""
        self.client.close()

# Convenience function for quick usage
def get_document_by_value(value: int, 
                         connection_string: str = "mongodb+srv://medicine:medicine@medicine.b8gwt4f.mongodb.net",
                         database_name: str = "medicines",
                         collection_name: str = "medicines") -> Optional[Dict[str, Any]]:
    """
    Quick function to get a document by value
    
    Args:
        value: The value to search for
        connection_string: MongoDB connection string
        database_name: Name of the database
        collection_name: Name of the collection
        
    Returns:
        The document if found, None otherwise
    """
    db = MedicineDB(connection_string, database_name, collection_name)
    try:
        result = db.find_by_value(value)
        return result
    finally:
        db.close_connection()

# Example usage
if __name__ == "__main__":
    # Debug: Let's check connection and collection info
    medicine_db = MedicineDB()
    
    try:
        # Check if we can connect
        print("Testing connection...")
        print(f"Database names: {medicine_db.client.list_database_names()}")
        print(f"Collections in 'medicines' db: {medicine_db.db.list_collection_names()}")
        
        # Check total document count
        total_docs = medicine_db.collection.count_documents({})
        print(f"Total documents in collection: {total_docs}")
        
        # Get a sample document to see the structure
        sample = medicine_db.collection.find_one()
        print(f"Sample document: {sample}")
        
        # Now try to find specific values
        print("\nSearching for documents...")
        document = medicine_db.find_by_value(483920)
        if document:
            print(f"Found 483920: {document}")
        else:
            print("Document with value 483920 not found")
        
        # Try the other value too
        document = medicine_db.find_by_value(912457)
        if document:
            print(f"Found 912457: {document}")
        else:
            print("Document with value 912457 not found")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        medicine_db.close_connection()