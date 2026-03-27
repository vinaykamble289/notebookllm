# RAG AI Assistant - Project Overview

## Summary

A full-stack RAG (Retrieval Augmented Generation) application with:
- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **Backend**: FastAPI + LangChain + FAISS
- **Vector Store**: Persistent FAISS index (disk-based memory pool)
- **Document Support**: PDF, DOCX, TXT, CSV, XLSX

## Key Features

### 1. Persistent Vector Storage
- FAISS vector store saved to disk
- Automatically loads on server restart
- Acts as a growing memory pool for all documents
- No data loss between sessions

### 2. Document Processing
- Multi-format support (PDF, DOCX, TXT, CSV, XLSX)
- Automatic text extraction and chunking
- Background processing with status tracking
- Incremental addition to vector store

### 3. RAG Pipeline
- Sentence-transformers for embeddings
- FAISS for similarity search
- Flan-T5 for answer generation
- Citation support with source tracking

### 4. Complete API
All frontend API calls implemented:
- ✅ Authentication (login, register, logout)
- ✅ Document upload with progress tracking
- ✅ Document listing with pagination
- ✅ Document deletion
- ✅ Manual ingestion trigger
- ✅ Document status checking
- ✅ Query submission with citations
- ✅ Query history
- ✅ System statistics
- ✅ Document download

## API Endpoints Implemented

### Authentication (`/api/v1/auth`)
```
POST   /login/json          - User login
POST   /register            - User registration
GET    /me                  - Get current user
POST   /logout              - User logout
```

### Admin (`/api/v1/admin`)
```
POST   /upload              - Upload document
GET    /documents           - List documents (paginated)
GET    /documents/{id}      - Get document details
DELETE /documents/{id}      - Delete document
POST   /ingest/{id}         - Trigger document processing
GET    /documents/{id}/status - Get processing status
GET    /stats               - System statistics
```

### Query (`/api/v1/query`)
```
POST   /                    - Submit query
GET    /history             - Query history (paginated)
GET    /{id}                - Query details
```

### Documents (`/api/v1/documents`)
```
GET    /{id}/download       - Download document
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LangChain**: RAG framework
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Text embeddings
- **Transformers**: LLM (Flan-T5)
- **PyMuPDF**: PDF processing
- **python-docx**: DOCX processing
- **pandas**: CSV/XLSX processing

### Frontend
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **React Dropzone**: File uploads
- **React Markdown**: Message rendering

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Admin Panel  │  │ Chat Interface│  │ Navigation   │     │
│  │ - Upload     │  │ - Query      │  │              │     │
│  │ - List Docs  │  │ - Citations  │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Auth API     │  │ Admin API    │  │ Query API    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                            │                                 │
│  ┌─────────────────────────┴──────────────────────┐        │
│  │              RAG Engine                         │        │
│  │  ┌──────────────┐  ┌──────────────┐           │        │
│  │  │ Doc Processor│  │ Vector Store │           │        │
│  │  │ - PDF        │  │ - FAISS      │           │        │
│  │  │ - DOCX       │  │ - Embeddings │           │        │
│  │  │ - TXT/CSV    │  │ - Persistent │           │        │
│  │  └──────────────┘  └──────────────┘           │        │
│  │                                                 │        │
│  │  ┌──────────────┐  ┌──────────────┐           │        │
│  │  │ Embedder     │  │ LLM          │           │        │
│  │  │ MiniLM-L6    │  │ Flan-T5      │           │        │
│  │  └──────────────┘  └──────────────┘           │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Persistent Storage                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Uploads/     │  │ vector_store/│  │ database.json│     │
│  │ (Documents)  │  │ (FAISS Index)│  │ (Metadata)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Document Upload Flow
```
1. User uploads file via frontend
2. Frontend sends multipart/form-data to /api/v1/admin/upload
3. Backend saves file to uploads/
4. Background task processes document:
   a. Parse file (PDF/DOCX/etc)
   b. Split into chunks
   c. Generate embeddings
   d. Add to FAISS index
   e. Save index to disk
5. Status updated to "completed"
6. Optional: Email notification sent
```

### Query Flow
```
1. User submits question via chat interface
2. Frontend sends query to /api/v1/query
3. Backend:
   a. Embeds query using same model
   b. FAISS retrieves top-k similar chunks
   c. LLM generates answer from context
   d. Extracts citations from sources
4. Response returned with answer + citations
5. Query saved to history
```

## File Structure

```
project/
├── backend/
│   ├── main.py                      # FastAPI app entry
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Config template
│   ├── start.bat                    # Windows startup script
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── auth.py             # Auth endpoints
│   │   │   ├── admin.py            # Document management
│   │   │   ├── query.py            # Query endpoints
│   │   │   └── documents.py        # Document download
│   │   ├── core/
│   │   │   ├── config.py           # Settings
│   │   │   ├── rag_engine.py       # RAG pipeline + FAISS
│   │   │   ├── document_processor.py # File parsing
│   │   │   └── email_service.py    # Email notifications
│   │   └── models/
│   │       ├── database.py         # Simple JSON DB
│   │       └── schemas.py          # Pydantic models
│   ├── uploads/                    # Uploaded files (auto-created)
│   └── vector_store/               # FAISS index (auto-created)
│       ├── documents_index/        # FAISS files
│       └── database.json           # Metadata
├── src/
│   ├── app/                        # Next.js pages
│   │   ├── admin/page.tsx         # Admin panel
│   │   ├── chat/page.tsx          # Chat interface
│   │   └── page.tsx               # Home
│   ├── components/
│   │   ├── admin/
│   │   │   ├── DocumentUpload.tsx
│   │   │   └── DocumentList.tsx
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   └── CitationDisplay.tsx
│   │   └── ui/                    # Reusable components
│   └── lib/
│       └── api.ts                 # API client
├── .env.local.example             # Frontend config
├── start-all.bat                  # Start both servers
├── SETUP.md                       # Setup instructions
└── PROJECT_OVERVIEW.md            # This file
```

## Quick Start

### Option 1: Automated (Windows)
```bash
start-all.bat
```

### Option 2: Manual

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
npm install
npm run dev
```

## Configuration

### Backend (.env)
```env
# Server
PORT=8000
DEBUG=True

# Security
SECRET_KEY=your-secret-key

# Models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=google/flan-t5-base

# Email (optional)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Key Implementation Details

### 1. Persistent Vector Store
The FAISS index is saved to disk after every document addition:
```python
self.vectorstore.save_local(str(self.index_path))
```

On startup, it's loaded:
```python
self.vectorstore = FAISS.load_local(
    str(self.index_path),
    self.embedding_model,
    allow_dangerous_deserialization=True
)
```

### 2. Background Processing
Documents are processed asynchronously:
```python
background_tasks.add_task(process_document_background, doc_id, file_path)
```

### 3. Incremental Addition
New documents are added to existing index:
```python
self.vectorstore.add_documents(chunks)
```

### 4. Citation Extraction
Source documents are tracked and returned:
```python
citations = extract_citations(result["source_documents"])
```

## Limitations & Future Improvements

### Current Limitations
1. **FAISS Deletion**: FAISS doesn't support easy deletion (requires rebuild)
2. **Simple Database**: Uses JSON file instead of real database
3. **No Authentication**: JWT auth is simplified
4. **Local Storage**: Files stored locally (not cloud)
5. **Single User**: No multi-tenancy

### Recommended Improvements
1. **Vector DB**: Replace FAISS with Pinecone/Weaviate/Qdrant
2. **Database**: Use PostgreSQL or MongoDB
3. **Storage**: Use S3 for document storage
4. **Auth**: Implement proper JWT with refresh tokens
5. **Caching**: Add Redis for query caching
6. **Monitoring**: Add logging, metrics, tracing
7. **Testing**: Add unit and integration tests
8. **Deployment**: Containerize with Docker

## Performance Notes

- **First Startup**: 2-3 minutes (model downloads)
- **Document Processing**: 5-30 seconds depending on size
- **Query Response**: 1-3 seconds
- **Vector Store Size**: ~1MB per 100 document chunks
- **Memory Usage**: ~2GB (models in memory)

## Testing

### Test Document Upload
```bash
curl -X POST http://localhost:8000/api/v1/admin/upload \
  -F "file=@test.pdf" \
  -F "title=Test Document"
```

### Test Query
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this document about?", "k": 5}'
```

## Support & Documentation

- **API Docs**: http://localhost:8000/docs
- **Setup Guide**: SETUP.md
- **Backend README**: backend/README.md

## License

This project is for educational/demo purposes.
