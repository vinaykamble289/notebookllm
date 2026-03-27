# RAG AI Assistant Backend

A FastAPI-based backend server with persistent FAISS vector storage for document-based question answering.

## Features

- **Document Upload & Processing**: Support for PDF, DOCX, TXT, CSV, XLSX
- **Persistent Vector Storage**: FAISS-based vector store that persists across restarts
- **RAG Pipeline**: LangChain-powered retrieval augmented generation
- **RESTful API**: Complete API for document management and querying
- **Background Processing**: Async document ingestion
- **Citation Support**: Returns source documents with answers

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration (email settings, etc.)

### 3. Run Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/json` - Login
- `POST /api/v1/auth/register` - Register
- `GET /api/v1/auth/me` - Get current user

### Admin/Documents
- `POST /api/v1/admin/upload` - Upload document
- `GET /api/v1/admin/documents` - List documents
- `GET /api/v1/admin/documents/{id}` - Get document details
- `DELETE /api/v1/admin/documents/{id}` - Delete document
- `POST /api/v1/admin/ingest/{id}` - Trigger document processing
- `GET /api/v1/admin/stats` - Get system statistics

### Query
- `POST /api/v1/query` - Submit a query
- `GET /api/v1/query/history` - Get query history
- `GET /api/v1/query/{id}` - Get query details

### Documents
- `GET /api/v1/documents/{id}/download` - Download document

## Architecture

### RAG Pipeline

1. **Document Upload**: Files are uploaded and saved to disk
2. **Processing**: Documents are parsed based on file type
3. **Chunking**: Text is split into chunks with overlap
4. **Embedding**: Chunks are embedded using sentence-transformers
5. **Storage**: Embeddings stored in FAISS vector store (persisted to disk)
6. **Query**: User queries are embedded and similar chunks retrieved
7. **Generation**: LLM generates answer based on retrieved context

### Vector Store Persistence

The FAISS vector store is saved to disk after each document addition:
- Location: `./vector_store/documents_index/`
- Automatically loaded on server startup
- Grows incrementally as documents are added

### Models Used

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`
- **LLM**: `google/flan-t5-base`

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── app/
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py    # Authentication endpoints
│   │       ├── admin.py   # Admin/document endpoints
│   │       ├── query.py   # Query endpoints
│   │       └── documents.py
│   ├── core/
│   │   ├── config.py      # Configuration
│   │   ├── rag_engine.py  # RAG engine with FAISS
│   │   └── document_processor.py  # Document parsing
│   └── models/
│       ├── database.py    # Simple JSON database
│       └── schemas.py     # Pydantic models
├── uploads/               # Uploaded documents (created automatically)
└── vector_store/          # FAISS index storage (created automatically)
```

## Notes

- The current implementation uses a simple JSON-based database for demo purposes
- For production, replace with PostgreSQL/MongoDB
- FAISS doesn't support easy deletion - consider Pinecone/Weaviate for production
- Email notifications can be configured in `.env`
- The vector store persists across server restarts
