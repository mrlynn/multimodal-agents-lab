#!/usr/bin/env python3
"""
Standalone test script to debug why the agent returns "I DON'T KNOW"
Skips all setup and uses existing MongoDB data and index
"""

import os
import sys
from pathlib import Path
from pymongo import MongoClient
from PIL import Image
import numpy as np
import json
import requests
import pymupdf
from tqdm import tqdm
try:
    import voyageai
    VOYAGEAI_AVAILABLE = True
except ImportError:
    VOYAGEAI_AVAILABLE = False

# Add colored output for better debugging
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

def show_success(msg): print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")
def show_error(msg): print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")
def show_info(msg): print(f"{Colors.BLUE}ℹ️ {msg}{Colors.ENDC}")
def show_warning(msg): print(f"{Colors.YELLOW}⚠️ {msg}{Colors.ENDC}")

# Load environment variables from .env if available
env_path = Path('.') / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"\'')
    show_info("Loaded environment variables from .env file")

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://admin:mongodb@localhost:27017/")
SERVERLESS_URL = os.getenv("SERVERLESS_URL")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
DB_NAME = "mongodb_aiewf"
COLLECTION_NAME = "multimodal_workshop_voyageai"
VS_INDEX_NAME = "vector_index_voyageai"
PDF_URL = "https://arxiv.org/pdf/2501.12948"  # DeepSeek R1 paper
IMAGES_DIR = "data/images"
ZOOM_FACTOR = 3.0

print("\n" + "="*60)
print("MULTIMODAL AGENT DEBUG AND EXTRACTION TEST")
print("="*60 + "\n")

# Add command line options
EXTRACT_DATA = "--extract" in sys.argv or "-e" in sys.argv
SKIP_EXISTING = "--skip-existing" in sys.argv or "-s" in sys.argv

if len(sys.argv) > 1 and ("--help" in sys.argv or "-h" in sys.argv):
    print("Usage: python test_agent_debug.py [options]")
    print("Options:")
    print("  --extract, -e       Perform full PDF extraction and embedding generation")
    print("  --skip-existing, -s Skip extraction if data already exists")
    print("  --help, -h          Show this help message")
    sys.exit(0)

if EXTRACT_DATA:
    show_info("Running in EXTRACTION mode - will download, extract, and generate embeddings")
else:
    show_info("Running in DEBUG mode - will test existing data only")
    show_info("Use --extract to include full data pipeline")

# Step 1: Check MongoDB Connection
print("1. CHECKING MONGODB CONNECTION")
print("-" * 40)
try:
    mongodb_client = MongoClient(MONGODB_URI)
    result = mongodb_client.admin.command("ping")
    if result.get("ok") == 1:
        show_success(f"Connected to MongoDB at {MONGODB_URI}")
    else:
        show_error("MongoDB ping failed")
        sys.exit(1)
except Exception as e:
    show_error(f"MongoDB connection failed: {e}")
    sys.exit(1)

collection = mongodb_client[DB_NAME][COLLECTION_NAME]

# PDF Extraction Functions
def normalize_vector(v):
    """Normalize a vector to unit length."""
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v

def download_and_extract_pdf():
    """Download PDF and extract pages as images"""
    show_info("Starting PDF download and extraction...")
    
    # Create images directory
    Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)
    
    try:
        # Download the PDF
        show_info(f"Downloading PDF from {PDF_URL}...")
        response = requests.get(PDF_URL)
        
        if response.status_code != 200:
            show_error(f"Failed to download PDF. Status code: {response.status_code}")
            return []
        
        show_success(f"PDF downloaded successfully! Size: {len(response.content)} bytes")
        
        # Open PDF from memory
        pdf = pymupdf.Document(stream=response.content, filetype="pdf")
        show_success(f"PDF loaded! Pages: {pdf.page_count}")
        
        # Extract pages as images
        docs = []
        mat = pymupdf.Matrix(ZOOM_FACTOR, ZOOM_FACTOR)
        
        show_info(f"Extracting {pdf.page_count} pages as images...")
        
        for n in tqdm(range(pdf.page_count), desc="Extracting pages"):
            # Render PDF page
            pix = pdf[n].get_pixmap(matrix=mat)
            
            # Store image locally
            key = f"{IMAGES_DIR}/{n+1}.png"
            pix.save(key)
            
            # Create document metadata
            doc = {
                "key": key,
                "width": pix.width,
                "height": pix.height,
                "page_number": n + 1
            }
            docs.append(doc)
        
        show_success(f"Successfully extracted {len(docs)} pages as images!")
        return docs
        
    except Exception as e:
        show_error(f"PDF extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return []

def generate_embedding(data, input_type="document", model="voyage-multimodal-3"):
    """Generate embedding using VoyageAI client or fallback endpoint"""
    try:
        if VOYAGEAI_AVAILABLE and VOYAGE_API_KEY:
            # Use VoyageAI Python client
            voyage_client = voyageai.Client(api_key=VOYAGE_API_KEY)
            
            if isinstance(data, Image.Image):
                # For images, use multimodal embedding
                inputs = [[data]]  # VoyageAI expects nested list format
                response = voyage_client.multimodal_embed(
                    inputs=inputs, 
                    model=model, 
                    input_type=input_type
                )
                embedding = response.embeddings[0]
            else:
                # For text, use regular embedding
                response = voyage_client.embed(
                    texts=[str(data)],
                    model="voyage-2",
                    input_type=input_type
                )
                embedding = response.embeddings[0]
                
        elif SERVERLESS_URL:
            # Fallback to serverless endpoint
            if isinstance(data, Image.Image):
                import base64
                from io import BytesIO
                buffered = BytesIO()
                data.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                input_data = img_base64
            else:
                input_data = str(data)
            
            response = requests.post(
                url=SERVERLESS_URL,
                json={
                    "task": "get_embedding",
                    "data": {"input": input_data, "input_type": input_type},
                },
            )
            
            if response.status_code != 200:
                show_error(f"Serverless embedding failed: {response.status_code}")
                return None
            
            embedding = response.json()["embedding"]
        else:
            show_warning("No embedding service available, using random embedding for testing")
            np.random.seed(42)
            embedding = np.random.randn(1024).tolist()
        
        # Normalize the embedding
        normalized_embedding = normalize_vector(np.array(embedding)).tolist()
        return normalized_embedding
        
    except Exception as e:
        show_error(f"Embedding generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def generate_embeddings_for_docs(docs):
    """Generate embeddings for all document images"""
    show_info(f"Generating embeddings for {len(docs)} images...")
    
    embedded_docs = []
    batch_size = 10
    
    for i in tqdm(range(0, len(docs), batch_size), desc="Processing batches"):
        batch = docs[i:i+batch_size]
        
        for doc in batch:
            try:
                # Load the image
                img = Image.open(doc['key'])
                
                # Generate embedding
                embedding = generate_embedding(img, input_type="document")
                
                if embedding:
                    doc["embedding"] = embedding
                    embedded_docs.append(doc)
                else:
                    show_warning(f"Failed to generate embedding for {doc['key']}")
                    
            except Exception as e:
                show_error(f"Error processing {doc['key']}: {e}")
    
    show_success(f"Successfully generated embeddings for {len(embedded_docs)} documents!")
    return embedded_docs

def ingest_data_to_mongodb(embedded_docs):
    """Ingest embedded documents into MongoDB"""
    try:
        # Clear existing documents
        delete_result = collection.delete_many({})
        show_info(f"Deleted {delete_result.deleted_count} existing documents")
        
        # Insert new documents
        if embedded_docs:
            collection.insert_many(embedded_docs)
            doc_count = collection.count_documents({})
            show_success(f"Successfully ingested {doc_count} documents into {COLLECTION_NAME}!")
            return doc_count
        else:
            show_error("No embedded documents to ingest")
            return 0
            
    except Exception as e:
        show_error(f"Data ingestion failed: {e}")
        return 0

def create_vector_index():
    """Create vector search index if it doesn't exist"""
    try:
        # Check if index already exists
        existing_indexes = list(collection.list_search_indexes())
        index_exists = any(idx.get('name') == VS_INDEX_NAME for idx in existing_indexes)
        
        if index_exists:
            show_info(f"Index '{VS_INDEX_NAME}' already exists")
            return True
        
        # Define vector index configuration
        model = {
            "name": VS_INDEX_NAME,
            "type": "vectorSearch",
            "definition": {
                "fields": [
                    {
                        "type": "vector",
                        "path": "embedding",
                        "numDimensions": 1024,
                        "similarity": "cosine",
                    }
                ]
            },
        }
        
        show_info("Creating vector search index...")
        collection.create_search_index(model=model)
        show_success(f"Vector search index '{VS_INDEX_NAME}' created successfully!")
        return True
        
    except Exception as e:
        show_error(f"Index creation failed: {e}")
        return False

# Step 0: PDF Extraction (if requested)
if EXTRACT_DATA:
    print("\n0. PERFORMING PDF EXTRACTION AND EMBEDDING GENERATION")
    print("-" * 60)
    
    # Check if we should skip existing data
    if SKIP_EXISTING:
        existing_count = collection.count_documents({})
        if existing_count > 0:
            show_info(f"Found {existing_count} existing documents, skipping extraction")
            EXTRACT_DATA = False
    
    if EXTRACT_DATA:
        # Download and extract PDF
        docs = download_and_extract_pdf()
        
        if docs:
            # Generate embeddings
            embedded_docs = generate_embeddings_for_docs(docs)
            
            if embedded_docs:
                # Ingest to MongoDB
                doc_count = ingest_data_to_mongodb(embedded_docs)
                
                if doc_count > 0:
                    # Create vector index
                    create_vector_index()
                    show_success("Full extraction pipeline completed!")
                else:
                    show_error("Ingestion failed")
            else:
                show_error("Embedding generation failed")
        else:
            show_error("PDF extraction failed")

# Step 2: Check Collection Status
print("\n2. CHECKING COLLECTION STATUS")
print("-" * 40)
try:
    doc_count = collection.count_documents({})
    show_info(f"Documents in collection: {doc_count}")
    
    if doc_count == 0:
        show_error("No documents in collection! Need to run data ingestion first.")
        sys.exit(1)
    
    # Check a sample document
    sample_doc = collection.find_one()
    show_info(f"Sample document fields: {list(sample_doc.keys())}")
    
    if 'embedding' in sample_doc:
        show_success(f"Embedding exists, dimensions: {len(sample_doc['embedding'])}")
    else:
        show_error("No embedding field in documents!")
        sys.exit(1)
        
    if 'key' in sample_doc:
        show_info(f"Sample image path: {sample_doc['key']}")
        if Path(sample_doc['key']).exists():
            show_success(f"Sample image file exists")
        else:
            show_error(f"Sample image file NOT found: {sample_doc['key']}")
    
except Exception as e:
    show_error(f"Collection check failed: {e}")
    sys.exit(1)

# Step 3: Check Vector Search Index
print("\n3. CHECKING VECTOR SEARCH INDEX")
print("-" * 40)
try:
    indexes = list(collection.list_search_indexes())
    show_info(f"Found {len(indexes)} search indexes")
    
    index_ready = False
    for idx in indexes:
        name = idx.get('name', 'Unknown')
        status = idx.get('status', 'Unknown')
        if name == VS_INDEX_NAME:
            if status == 'READY':
                show_success(f"Index '{VS_INDEX_NAME}' is READY")
                index_ready = True
            else:
                show_error(f"Index '{VS_INDEX_NAME}' status: {status}")
    
    if not index_ready:
        show_error("Vector search index not ready!")
        sys.exit(1)
        
except Exception as e:
    show_error(f"Index check failed: {e}")

# Step 4: Test Embedding Generation
print("\n4. TESTING EMBEDDING GENERATION")
print("-" * 40)

def generate_embedding_simple(text_query):
    """Simple embedding generation for testing"""
    import requests
    
    if SERVERLESS_URL:
        try:
            response = requests.post(
                url=SERVERLESS_URL,
                json={
                    "task": "get_embedding",
                    "data": {"input": text_query, "input_type": "query"},
                },
            )
            if response.status_code == 200:
                embedding = response.json()["embedding"]
                show_success(f"Generated embedding via serverless, dimensions: {len(embedding)}")
                return embedding
            else:
                show_error(f"Serverless embedding failed: {response.status_code}")
                return None
        except Exception as e:
            show_error(f"Serverless request failed: {e}")
            return None
    else:
        show_warning("No serverless URL, using random embedding for testing")
        # Generate random embedding for testing
        np.random.seed(42)
        embedding = np.random.randn(1024).tolist()
        return embedding

test_query = "What is the Pass@1 accuracy of DeepSeek R1 on AIME 2024?"
show_info(f"Test query: '{test_query}'")
query_embedding = generate_embedding_simple(test_query)

if not query_embedding:
    show_error("Failed to generate query embedding")
    sys.exit(1)

# Step 5: Test Vector Search
print("\n5. TESTING VECTOR SEARCH")
print("-" * 40)

pipeline = [
    {
        "$vectorSearch": {
            "index": VS_INDEX_NAME,
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": 150,
            "limit": 2,
        }
    },
    {
        "$project": {
            "_id": 0,
            "key": 1,
            "page_number": 1,
            "score": {"$meta": "vectorSearchScore"},
        }
    },
]

try:
    results = list(collection.aggregate(pipeline))
    show_info(f"Vector search returned {len(results)} results")
    
    if results:
        for i, result in enumerate(results, 1):
            show_success(f"Result {i}: Page {result.get('page_number', 'N/A')}, "
                        f"Score: {result.get('score', 0):.4f}")
            img_path = result.get('key', '')
            if Path(img_path).exists():
                show_success(f"  ✓ Image exists: {img_path}")
                # Try to open it
                try:
                    img = Image.open(img_path)
                    show_success(f"  ✓ Can open image, size: {img.size}")
                except Exception as e:
                    show_error(f"  ✗ Cannot open image: {e}")
            else:
                show_error(f"  ✗ Image NOT found: {img_path}")
    else:
        show_error("No results from vector search!")
        
except Exception as e:
    show_error(f"Vector search failed: {e}")
    import traceback
    traceback.print_exc()

# Step 6: Test with Gemini (if available)
print("\n6. TESTING LLM INTEGRATION")
print("-" * 40)

try:
    # Try to get Gemini API key
    api_key = None
    if SERVERLESS_URL:
        import requests
        response = requests.post(
            url=SERVERLESS_URL, 
            json={"task": "get_api_key", "data": "google"}
        )
        if response.status_code == 200:
            api_key = response.json().get("api_key")
    
    if not api_key:
        api_key = os.getenv("GOOGLE_API_KEY")
    
    if api_key:
        from google import genai
        from google.genai import types
        
        gemini_client = genai.Client(api_key=api_key)
        show_success("Gemini client initialized")
        
        # Test with retrieved images
        if results:
            show_info("Testing LLM with retrieved images...")
            
            images_to_test = []
            for result in results[:2]:  # Use top 2 results
                img_path = result.get('key', '')
                if Path(img_path).exists():
                    try:
                        img = Image.open(img_path)
                        images_to_test.append(img)
                    except:
                        pass
            
            if images_to_test:
                show_info(f"Sending query with {len(images_to_test)} images to Gemini...")
                
                system_prompt = (
                    "Answer the questions based on the provided context only. "
                    "If the context is not sufficient, say I DON'T KNOW. "
                    "DO NOT use any other information to answer the question."
                )
                
                contents = [system_prompt, test_query] + images_to_test
                
                response = gemini_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(temperature=0.0),
                )
                
                answer = response.text
                show_success("Got response from Gemini!")
                print(f"\n{Colors.GREEN}ANSWER:{Colors.ENDC}")
                print("-" * 40)
                print(answer)
                print("-" * 40)
                
                if "I DON'T KNOW" in answer:
                    show_warning("⚠️ LLM returned 'I DON'T KNOW' despite having images!")
                    show_info("This suggests the images might not contain the answer, "
                             "or the prompt is too restrictive")
            else:
                show_error("No valid images to send to LLM")
        else:
            show_error("No vector search results to test with LLM")
            
    else:
        show_warning("No Gemini API key available, skipping LLM test")
        
except ImportError:
    show_warning("Google genai library not installed, skipping LLM test")
    show_info("Install with: pip install google-genai")
except Exception as e:
    show_error(f"LLM test failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "="*60)
print("DIAGNOSTICS COMPLETE")
print("="*60)

print("\nSUMMARY:")
if doc_count > 0:
    print(f"  ✓ MongoDB has {doc_count} documents")
if index_ready:
    print(f"  ✓ Vector index is ready")
if results:
    print(f"  ✓ Vector search works ({len(results)} results)")
else:
    print(f"  ✗ Vector search returned no results")

print("\nNEXT STEPS:")
if not results:
    print("  1. Check if embeddings were generated correctly")
    print("  2. Try a different query")
    print("  3. Check if the PDF was processed correctly")
    if not EXTRACT_DATA:
        print("  4. Try running with --extract to generate fresh data")
elif "I DON'T KNOW" in locals().get('answer', ''):
    print("  1. The images might not contain the answer to this specific query")
    print("  2. Try a simpler query that you know is in the document")
    print("  3. Consider relaxing the system prompt")

print("\nUSAGE EXAMPLES:")
print("  # Debug existing data only:")
print("  python test_agent_debug.py")
print()
print("  # Full extraction pipeline:")
print("  python test_agent_debug.py --extract")
print()
print("  # Skip extraction if data exists:")
print("  python test_agent_debug.py --extract --skip-existing")