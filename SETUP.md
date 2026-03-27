# RAG AI Assistant - Complete Setup Guide

This project consists of a Next.js frontend and a FastAPI backend with persistent FAISS vector storage for document-based RAG (Retrieval Augmented Generation).

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   Next.js       │  HTTP   │   FastAPI        │  Query  │   FAISS Vector  │
│   Frontend      │ ──────> │   Backend        │ ──────> │   Store (Disk)  │
│   (Port 3000)   │         │   (Port 8000)    │         │   Persistent    │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     │ Process
                                     ▼
                            ┌──────────────────┐
                            │  Document Parser │
                            │  PDF/DOCX/TXT    │
                            │  CSV/XLSX        │
                            └──────────────────┘
```

## Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **Git**

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (web server)
- LangChain (RAG framework)
- Sentence Transformers (embeddings)
- FAISS (vector store)
- Transformers (LLM)
- Document parsers (PyMuPDF, python-docx, etc.)

**Note:** First installation may take 5-10 minutes as it downloads ML models.

### 5. Configure Environment

```bash
copy .env.example .env
```

Edit `.env` and update:
- `SECRET_KEY` - Change to a secure random string
- `SMTP_USER`, `SMTP_PASSWORD` - Your email credentials (optional)
- Other settings as needed

### 6. Start Backend Server

```bash
python main.py
```

Or use the batch file (Windows):
```bash
start.bat
```

The backend will:
- Start on `http://localhost:8000`
- Create `uploads/` directory for documents
- Create `vector_store/` directory for FAISS index
- Load existing vector store if available
- Initialize embedding model and LLM

**First startup may take 2-3 minutes** as models are downloaded.

### 7. Verify Backend

Open `http://localhost:8000/docs` to see the API documentation.

## Frontend Setup

### 1. Navigate to Project Root

```bash
cd ..
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment

```bash
copy .env.local.example .env.local
```

The default configuration points to `http://localhost:8000`.

### 4. Start Frontend

```bash
npm run dev
```

The frontend will start on `http://localhost:3000`.

## Usage

### 1. Upload Documents

1. Navigate to `http://localhost:3000/admin`
2. Upload PDF, DOCX, TXT, CSV, or XLSX files
3. Documents are automatically processed and added to vector store
4. Processing happens in background

### 2. Chat with Documents

1. Navigate to `http://localhost:3000/chat`
2. Ask questions about uploaded documents
3. Get answers with citations
4. Optionally enable mindmap visualization

### 3. Monitor Documents

- View all documents in admin panel
- Check processing status
- Trigger manual reprocessing if needed
- Download documents

## How It Works

### Document Processing Pipeline

1. **Upload**: File uploaded via API
2. **Parse**: Document parsed based on type (PDF → PyMuPDF, DOCX → python-docx, etc.)
3. **Chunk**: Text split into chunks (1000 chars with 200 overlap)
4. **Embed**: Each chunk embedded using sentence-transformers
5. **Store**: Embeddings saved to FAISS index on disk
6. **Persist**: Index automatically saved and reloaded on restart

### Query Pipeline

1. **User Query**: Question submitted via chat interface
2. **Embed Query**: Question embedded using same model
3. **Retrieve**: FAISS finds top-k similar chunks
4. **Generate**: LLM generates answer based on retrieved context
5. **Citations**: Source documents returned with answer

### Persistent Vector Store

- **Location**: `backend/vector_store/documents_index/`
- **Format**: FAISS index files
- **Behavior**: 
  - Automatically loaded on server startup
  - Grows incrementally as documents added
  - Persists across server restarts
  - Acts as a "memory pool" for all documents

## API Endpoints

### Document Management
- `POST /api/v1/admin/upload` - Upload document
- `GET /api/v1/admin/documents` - List all documents
- `DELETE /api/v1/admin/documents/{id}` - Delete document
- `POST /api/v1/admin/ingest/{id}` - Reprocess document

### Query
- `POST /api/v1/query` - Ask a question
- `GET /api/v1/query/history` - View query history

### Stats
- `GET /api/v1/admin/stats` - System statistics

## Troubleshooting

### Backend Issues

**Models not downloading:**
- Ensure internet connection
- Models download on first run (~500MB)
- Check `~/.cache/huggingface/` directory

**Port 8000 already in use:**
- Change `PORT` in `.env`
- Update `NEXT_PUBLIC_API_URL` in frontend `.env.local`

**FAISS errors:**
- Delete `vector_store/` directory and restart
- Ensure sufficient disk space

### Frontend Issues

**API connection failed:**
- Verify backend is running on port 8000
- Check CORS settings in backend
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

**Upload fails:**
- Check file size (max 50MB)
- Verify file type is supported
- Check backend logs

## Production Considerations

For production deployment:

1. **Database**: Replace JSON database with PostgreSQL/MongoDB
2. **Vector Store**: Consider Pinecone, Weaviate, or Qdrant for better scalability
3. **Authentication**: Implement proper JWT authentication
4. **File Storage**: Use S3 or similar for document storage
5. **Caching**: Add Redis for query caching
6. **Monitoring**: Add logging and monitoring
7. **Security**: Enable HTTPS, rate limiting, input validation

## Models Used

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (80MB)
- **LLM**: `google/flan-t5-base` (990MB)

You can change these in `backend/.env`:
```
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=google/flan-t5-base
```

## File Structure

```
project/
├── backend/                    # FastAPI backend
│   ├── main.py                # Entry point
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Configuration
│   ├── app/
│   │   ├── api/v1/           # API routes
│   │   ├── core/             # RAG engine, document processor
│   │   └── models/           # Data models
│   ├── uploads/              # Uploaded documents (auto-created)
│   └── vector_store/         # FAISS index (auto-created)
├── src/                       # Next.js frontend
│   ├── app/                  # Pages
│   ├── components/           # React components
│   └── lib/                  # API client
├── .env.local                # Frontend config
└── SETUP.md                  # This file
```

## Support

For issues or questions:
1. Check backend logs in terminal
2. Check frontend console in browser
3. Verify all dependencies installed
4. Ensure models downloaded successfully
