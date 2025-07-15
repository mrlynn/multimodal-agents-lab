# Multimodal Agents Lab - Development Guide

Based on analysis of `solutions.ipynb` and `multimodal_agents_lab_enhanced.ipynb`, here are the key findings and best practices for future development.

## 1. Common Code Patterns & Best Practices

### Error Handling Pattern
```python
try:
    # Main operation
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to download. Status code: {response.status_code}")
    # Process response
except Exception as e:
    show_error(f"Operation failed: {e}")
    return default_value
```

### Async Operation Pattern
Both notebooks use synchronous operations, but for production:
- Consider async MongoDB operations with motor
- Use async HTTP requests with aiohttp
- Implement concurrent PDF page processing

### Resource Management
```python
# Always create directories before saving files
Path("data/images").mkdir(parents=True, exist_ok=True)

# Clean up existing data before bulk operations
collection.delete_many({})
```

## 2. Testing & Validation Approaches

### Validation Framework (Enhanced Notebook)
```python
# Variable existence validation
validator.validate_variable_exists('var_name', locals(), expected_type)

# Custom validation
validator.validate_custom(
    condition,
    success_message,
    failure_message
)

# Connection validation
result = mongodb_client.admin.command("ping")
if result.get("ok") == 1:
    show_success("Connected!")
```

### Testing Strategy
1. **Unit Tests**: Test individual functions (vector search, embeddings)
2. **Integration Tests**: Test agent with real queries
3. **Edge Cases**: Empty results, connection failures, missing images

## 3. Debugging Tips & Common Issues

### Common Issues Identified

1. **MongoDB Connection Issues**
   - IP not whitelisted in Atlas
   - Wrong connection string format
   - Missing environment variables

2. **Vector Search Issues**
   - Index not in READY status
   - Wrong embedding dimensions (must be 1024 for Voyage)
   - Mismatched field paths

3. **PDF Processing Issues**
   - Network timeouts downloading large PDFs
   - Memory issues with high zoom factors
   - Missing data/images directory

### Debug Helpers
```python
# Always log intermediate results
show_info(f"Found {len(keys)} relevant images")
for i, (key, score) in enumerate(zip(keys, scores)):
    show_info(f"  {i+1}. {key} (score: {score:.4f})")

# Check index status explicitly
indexes = list(collection.list_search_indexes())
for idx in indexes:
    print(f"{idx.get('name')}: {idx.get('status')}")
```

## 4. MongoDB Index Configurations

### Vector Search Index
```python
{
    "name": "vector_index",
    "type": "vectorSearch",
    "definition": {
        "fields": [{
            "type": "vector",
            "path": "embedding",
            "numDimensions": 1024,  # Voyage multimodal-3
            "similarity": "cosine"
        }]
    }
}
```

### Session History Index
```python
# Create index for efficient session queries
history_collection.create_index("session_id")
```

### Best Practices
- Always verify index is READY before use
- Use appropriate numCandidates (150) and limit (2)
- Include score in projections for debugging

## 5. Performance Considerations

### PDF Processing Optimization
```python
zoom = 3.0  # Balance between quality and memory
mat = pymupdf.Matrix(zoom, zoom)

# Process in batches for large PDFs
for n in tqdm(range(pdf.page_count)):
    # Process page
    # Consider batch processing every N pages
```

### Vector Search Optimization
```python
pipeline = [{
    "$vectorSearch": {
        "index": VS_INDEX_NAME,
        "path": "embedding",
        "queryVector": query_embedding,
        "numCandidates": 150,  # Higher = better recall, slower
        "limit": 2,            # Adjust based on needs
    }
}]
```

### Memory Management
- Store only essential fields in history
- Implement TTL indexes for session cleanup
- Consider pagination for large histories

## 6. Key Architecture Components

### Core Classes/Functions

1. **Vector Search Tool**
   ```python
   get_information_for_question_answering(user_query: str) -> List[str]
   ```
   - Central retrieval mechanism
   - Handles embedding generation and search

2. **Tool Selection System**
   ```python
   select_tool(messages: List) -> FunctionCall | None
   ```
   - Decides when to use tools
   - Integrates with Gemini function calling

3. **Answer Generation Pipeline**
   ```python
   generate_answer(user_query: str, images: List = []) -> str
   ```
   - Orchestrates tool calls
   - Manages context and prompts

4. **Memory System**
   ```python
   store_chat_message(session_id, role, type, content)
   retrieve_session_history(session_id) -> List
   ```
   - Enables multi-turn conversations
   - Stores both text and image references

5. **ReAct Agent**
   ```python
   generate_answer_react(user_query: str, images: List = []) -> str
   ```
   - Implements reasoning loops
   - Self-correcting with max iterations

### Architecture Flow
```
User Query → Tool Selection → Vector Search → Context Assembly → LLM Generation → Response
     ↓                                                   ↑
     └──────────── Memory Storage ───────────────────────┘
```

## 7. Development Recommendations

### For Production Deployment
1. **Add comprehensive logging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   ```

2. **Implement retry logic**
   ```python
   from tenacity import retry, stop_after_attempt, wait_exponential
   
   @retry(stop=stop_after_attempt(3), wait=wait_exponential())
   def api_call():
       # API operation
   ```

3. **Add monitoring**
   - Track vector search latencies
   - Monitor LLM token usage
   - Log tool call patterns

4. **Security considerations**
   - Validate user inputs
   - Implement rate limiting
   - Secure API key storage

### Extension Ideas
1. **Multi-modal embeddings**: Support for video, audio
2. **Hybrid search**: Combine vector + text search
3. **Agent memory**: Long-term knowledge persistence
4. **Tool expansion**: Add web search, calculations
5. **Streaming responses**: For better UX

## 8. Configuration Best Practices

### Environment Setup
```python
# Centralize configuration
class Config:
    MONGODB_URI = os.getenv("MONGODB_URI")
    SERVERLESS_URL = os.getenv("SERVERLESS_URL")
    DB_NAME = "mongodb_aiewf"
    COLLECTION_NAME = "multimodal_workshop"
    VS_INDEX_NAME = "vector_index"
    LLM_MODEL = "gemini-2.0-flash"
    EMBEDDING_DIM = 1024
    MAX_SEARCH_RESULTS = 2
    REACT_MAX_ITERATIONS = 3
```

### Graceful Degradation
```python
# Fallback for missing components
try:
    from jupyter_lab_progress import LabProgress
except ImportError:
    # Define minimal fallback functions
    def show_info(msg): print(f"INFO: {msg}")
```

This guide provides a comprehensive overview of the patterns, practices, and architectural decisions in the multimodal agents lab, serving as a reference for future development and extensions.