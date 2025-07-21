#!/usr/bin/env python3
"""
Migration Example: Converting from Manual to Library Approach

This script demonstrates how to migrate existing multimodal data
from the manual implementation to the pymongo-voyageai-multimodal library.
"""

import os
from pymongo import MongoClient
from pymongo_voyageai_multimodal import PyMongoVoyageAI, TextDocument, ImageDocument
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_existing_data():
    """
    Example migration from manual collection to library-managed collection.
    """
    
    # Step 1: Connect to existing manual collection
    manual_client = MongoClient(os.environ["MONGODB_ATLAS_CONNECTION_STRING"])
    manual_db = manual_client["mongodb_aiewf"]
    manual_collection = manual_db["multimodal_workshop"]
    
    # Step 2: Initialize new library client
    library_client = PyMongoVoyageAI.from_connection_string(
        connection_string=os.environ["MONGODB_ATLAS_CONNECTION_STRING"],
        database_name="multimodal_lab_simplified",
        collection_name="migrated_documents",
        s3_bucket_name=os.environ.get("S3_BUCKET_NAME", ""),
        voyageai_api_key=os.environ["VOYAGEAI_API_KEY"]
    )
    
    print("🔄 Starting migration...")
    
    # Step 3: Migrate existing documents
    existing_docs = list(manual_collection.find({}))
    print(f"Found {len(existing_docs)} documents to migrate")
    
    migrated_count = 0
    for doc in existing_docs:
        try:
            # Extract relevant fields
            doc_id = str(doc.get("_id", f"migrated_{migrated_count}"))
            
            # Check if it's an image document (has 'key' field)
            if "key" in doc:
                # For image documents, we'll need to handle them differently
                # In production, you'd load the actual image from the file path
                print(f"⚠️  Image document {doc_id} - requires manual image loading")
                # In real migration:
                # image = Image.open(doc["key"])
                # image_doc = ImageDocument(image=image, metadata={"original_key": doc["key"]})
                # library_client.add_documents([image_doc], ids=[doc_id])
            
            # Check if it's a text document
            elif "text" in doc or "content" in doc:
                text_content = doc.get("text", doc.get("content", ""))
                metadata = {k: v for k, v in doc.items() 
                           if k not in ["_id", "text", "content", "embedding"]}
                
                text_doc = TextDocument(text=text_content, metadata=metadata)
                library_client.add_documents([text_doc], ids=[doc_id])
                migrated_count += 1
                print(f"✅ Migrated text document: {doc_id}")
            
        except Exception as e:
            print(f"❌ Failed to migrate document {doc_id}: {e}")
    
    print(f"\n✅ Migration complete! Migrated {migrated_count} documents")
    
    # Step 4: Verify migration
    print("\n🔍 Verifying migration with test search...")
    test_results = library_client.similarity_search(
        query="test query",
        k=3
    )
    print(f"Search returned {len(test_results)} results")
    
    # Cleanup
    manual_client.close()
    library_client.close()

def create_hybrid_agent():
    """
    Example of using both manual and library approaches together.
    """
    
    # Initialize library client for new documents
    library_client = PyMongoVoyageAI.from_connection_string(
        connection_string=os.environ["MONGODB_ATLAS_CONNECTION_STRING"],
        database_name="hybrid_multimodal",
        collection_name="documents",
        s3_bucket_name=os.environ.get("S3_BUCKET_NAME", ""),
        voyageai_api_key=os.environ["VOYAGEAI_API_KEY"]
    )
    
    # You can still use manual MongoDB for custom operations
    manual_client = MongoClient(os.environ["MONGODB_ATLAS_CONNECTION_STRING"])
    manual_db = manual_client["hybrid_multimodal"]
    metadata_collection = manual_db["document_metadata"]
    
    def hybrid_search(query: str, k: int = 3):
        """
        Hybrid search using library for vector search and manual for metadata.
        """
        # Use library for vector search
        vector_results = library_client.similarity_search(query=query, k=k)
        
        # Enhance with manual metadata lookup
        enhanced_results = []
        for result in vector_results:
            doc_id = result.get("id")
            
            # Get additional metadata from manual collection
            metadata = metadata_collection.find_one({"document_id": doc_id})
            
            if metadata:
                result["custom_metadata"] = metadata
            
            enhanced_results.append(result)
        
        return enhanced_results
    
    return hybrid_search

if __name__ == "__main__":
    print("🚀 Multimodal Workshop Migration Example")
    print("=" * 50)
    
    # Check environment
    required_vars = [
        "MONGODB_ATLAS_CONNECTION_STRING",
        "VOYAGEAI_API_KEY"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        print("Please set these in your .env file")
        exit(1)
    
    print("\n1️⃣ Example: Migrating existing data")
    print("-" * 30)
    # Uncomment to run migration
    # migrate_existing_data()
    
    print("\n2️⃣ Example: Hybrid approach")
    print("-" * 30)
    hybrid_search_fn = create_hybrid_agent()
    print("✅ Created hybrid search function combining library and manual approaches")
    
    print("\n💡 Key Takeaways:")
    print("- The library handles embeddings and vector search automatically")
    print("- You can still use manual MongoDB for custom operations")
    print("- Migration requires re-processing images for embeddings")
    print("- Hybrid approaches give you the best of both worlds")