# 🚀 Multimodal Agents Workshop - Simplified Version

Build powerful multimodal AI agents with 90% less code using the `pymongo-voyageai-multimodal` library!

## 🎯 What's New?

This simplified workshop demonstrates the power of the new `pymongo-voyageai-multimodal` library, which combines:

- **MongoDB Atlas Vector Search**
- **Voyage AI's multimodal embeddings**
- **AWS S3 storage**
- **Automatic PDF processing**

All in a single, easy-to-use Python client!

## 📊 Comparison with Original Workshop

| Task | Original Lines of Code | Simplified Lines of Code | Reduction |
|------|------------------------|--------------------------|-----------|
| PDF Processing | ~50 lines | 2 lines | 96% |
| Embedding Generation | ~30 lines | 0 (automatic) | 100% |
| Vector Index Creation | ~20 lines | 0 (automatic) | 100% |
| Vector Search | ~40 lines | 1 line | 97.5% |
| **Total** | **~500+ lines** | **~50 lines** | **~90%** |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pymongo-voyageai-multimodal google-generativeai python-dotenv
```

### 2. Set Environment Variables

Create a `.env` file:

```env
MONGODB_ATLAS_CONNECTION_STRING=mongodb+srv://...
S3_BUCKET_NAME=your-bucket-name
VOYAGEAI_API_KEY=your-voyage-key
GOOGLE_API_KEY=your-gemini-key
```

### 3. Run the Workshop

```bash
jupyter notebook multimodal_agents_simplified.ipynb
```

## 🔑 Key Features

### 🎯 One-Line PDF Processing

**Before (Manual):**
```python
# Download, extract, save images, generate embeddings...
# ~50 lines of code
```

**After (Library):**
```python
images = client.url_to_images("https://arxiv.org/pdf/2501.12948")
client.add_documents(images)
```

### 🔍 Simplified Vector Search

**Before (Manual):**
```python
# Generate embeddings, create pipeline, execute aggregation...
# ~40 lines of code
```

**After (Library):**
```python
results = client.similarity_search("What is the accuracy?", k=2)
```

### 🏗️ Automatic Index Management

No more manual index creation! The library handles everything:
- Vector index creation
- Dimension detection
- Similarity metrics
- Index optimization

## 📚 Workshop Contents

1. **Environment Setup** - Initialize the unified client
2. **Document Processing** - Process PDFs with one line
3. **Vector Search** - Natural language search made simple
4. **AI Agent Creation** - Build Gemini-powered agents
5. **S3 Integration** - Load documents from cloud storage
6. **Mixed Content** - Handle both text and images

## 🛠️ Architecture

```
┌─────────────────────┐
│   Your Application  │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ pymongo-voyageai-   │
│    multimodal       │
├─────────────────────┤
│ • PDF Processing    │
│ • Embedding Gen     │
│ • Vector Index      │
│ • Search API        │
└──────────┬──────────┘
           │
    ┌──────┴──────┬─────────┬──────────┐
    ▼             ▼         ▼          ▼
┌────────┐  ┌─────────┐ ┌───────┐ ┌────────┐
│MongoDB │  │Voyage AI│ │AWS S3 │ │Gemini  │
│ Atlas  │  │   API   │ │       │ │  API   │
└────────┘  └─────────┘ └───────┘ └────────┘
```

## 💡 When to Use This Approach

### ✅ Perfect For:
- Rapid prototyping of multimodal search
- Production applications with standard requirements
- Teams wanting minimal maintenance
- Projects using AWS S3 for document storage
- Applications needing Voyage AI's multimodal embeddings

### ❌ Not Ideal For:
- Custom embedding models (only supports Voyage AI)
- Non-S3 storage backends
- Real-time document updates
- Complex preprocessing pipelines

## 🔄 Migrating from Manual Implementation

See `migration_example.py` for examples of:
- Converting existing collections
- Hybrid approaches (library + manual)
- Gradual migration strategies

## 🚀 Next Steps

1. **Complete the Workshop** - Build your first multimodal agent
2. **Explore S3 Integration** - Load documents from cloud storage
3. **Read the Comparison Guide** - Understand the differences
4. **Check the Library Docs** - [pymongo-voyageai.readthedocs.io](https://pymongo-voyageai.readthedocs.io/)

## 📖 Resources

- **Original Workshop**: For learning the concepts in detail
- **Simplified Workshop**: For rapid development
- **Comparison Guide**: `COMPARISON_GUIDE.md`
- **Migration Examples**: `migration_example.py`

## 🤝 Support

- Library Issues: [GitHub Issues](https://github.com/mongodb/pymongo-voyageai-multimodal)
- Workshop Questions: Create an issue in this repository
- MongoDB Support: [MongoDB Community Forums](https://www.mongodb.com/community/forums/)

---

**Happy coding!** 🎉 Build powerful multimodal AI applications with minimal code!