# Quick Reference Guide

## Installation & Startup

### First Time Setup

```bash
# 1. Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env if needed

# 2. Frontend Setup
cd ..
npm install
copy .env.local.example .env.local
```

### Start Servers

**Option 1: Quick Start (Windows)**
```bash
start-all.bat
```

**Option 2: Manual**
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python main.py

# Terminal 2 - Frontend
npm run dev
```

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Common Tasks

### Upload a Document
1. Go to http://localhost:3000/admin
2. Drag & drop or click to select file
3. Wait for processing (status updates automatically)

### Ask Questions
1. Go to http://localhost:3000/chat
2. Type your question
3. Get answer with citations

### Check System Stats
```bash
curl http://localhost:8000/api/v1/admin/stats
```

## API Examples

### Upload Document
```bash
curl -X POST http://localhost:8000/api/v1/admin/upload \
  -F "file=@document.pdf" \
  -F "title=My Document"
```

### List Documents
```bash
curl http://localhost:8000/api/v1/admin/documents?page=1&per_page=10
```

### Submit Query
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this about?",
    "k": 8,
    "include_audio": false,
    "include_mindmap": false
  }'
```

### Get Query History
```bash
curl http://localhost:8000/api/v1/query/history?page=1&per_page=10
```

## File Locations

### Backend
- **Uploaded Files**: `backend/uploads/`
- **Vector Store**: `backend/vector_store/documents_index/`
- **Database**: `backend/vector_store/database.json`
- **Config**: `backend/.env`

### Frontend
- **Config**: `.env.local`

## Supported File Types

- PDF (`.pdf`)
- Word (`.doc`, `.docx`)
- Text (`.txt`)
- CSV (`.csv`)
- Excel (`.xlsx`, `.xls`)

Max file size: 50MB

## Configuration

### Backend (.env)
```env
PORT=8000                    # Server port
SECRET_KEY=change-me         # JWT secret
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=google/flan-t5-base
CHUNK_SIZE=1000             # Text chunk size
CHUNK_OVERLAP=200           # Chunk overlap
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port availability
netstat -ano | findstr :8000
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check port availability
netstat -ano | findstr :3000
```

### Models not downloading
- Ensure internet connection
- Models download to `~/.cache/huggingface/`
- First download takes 5-10 minutes
- Total size: ~1GB

### Upload fails
- Check file size (max 50MB)
- Verify file type is supported
- Check backend logs for errors
- Ensure `uploads/` directory exists

### Query returns no results
- Ensure documents are processed (status: "completed")
- Check vector store has data: `GET /api/v1/admin/stats`
- Try uploading a test document

## Development

### Backend Development
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
npm run dev
```

### View Logs
- Backend: Check terminal running `python main.py`
- Frontend: Check browser console (F12)

## Testing

### Test Backend Health
```bash
curl http://localhost:8000/health
```

### Test Document Upload
```bash
curl -X POST http://localhost:8000/api/v1/admin/upload \
  -F "file=@test.pdf"
```

### Test Query
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "k": 5}'
```

## Performance Tips

1. **First Startup**: Takes 2-3 minutes (model download)
2. **Document Processing**: 5-30 seconds per document
3. **Query Speed**: 1-3 seconds
4. **Memory Usage**: ~2GB for models
5. **Disk Space**: ~1GB for models + uploaded files

## Keyboard Shortcuts

### Chat Interface
- `Enter`: Send message
- `Shift+Enter`: New line

## Data Persistence

### What Persists
- ✅ Uploaded documents (`uploads/`)
- ✅ Vector embeddings (`vector_store/`)
- ✅ Document metadata (`database.json`)
- ✅ Query history

### What Doesn't Persist
- ❌ User sessions (in-memory)
- ❌ Temporary files

## Backup

### Backup Important Data
```bash
# Backup vector store and database
xcopy backend\vector_store backup\vector_store /E /I

# Backup uploaded documents
xcopy backend\uploads backup\uploads /E /I
```

### Restore
```bash
# Restore vector store
xcopy backup\vector_store backend\vector_store /E /I

# Restore documents
xcopy backup\uploads backend\uploads /E /I
```

## Reset Everything

```bash
# Stop servers
# Delete data directories
rmdir /s /q backend\uploads
rmdir /s /q backend\vector_store

# Restart servers (directories will be recreated)
```

## Environment Variables Reference

### Backend
| Variable | Default | Description |
|----------|---------|-------------|
| HOST | 0.0.0.0 | Server host |
| PORT | 8000 | Server port |
| DEBUG | True | Debug mode |
| SECRET_KEY | - | JWT secret |
| UPLOAD_DIR | ./uploads | Upload directory |
| VECTOR_STORE_DIR | ./vector_store | Vector store path |
| EMBEDDING_MODEL | all-MiniLM-L6-v2 | Embedding model |
| LLM_MODEL | flan-t5-base | Language model |
| CHUNK_SIZE | 1000 | Text chunk size |
| CHUNK_OVERLAP | 200 | Chunk overlap |

### Frontend
| Variable | Default | Description |
|----------|---------|-------------|
| NEXT_PUBLIC_API_URL | http://localhost:8000 | Backend API URL |

## Common Errors

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port already in use"
Change port in `.env` or kill process:
```bash
# Find process
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### "FAISS index not found"
Normal on first run. Index created after first document upload.

### "Model download failed"
Check internet connection. Models download from HuggingFace.

## Getting Help

1. Check logs in terminal
2. Check browser console (F12)
3. Review SETUP.md for detailed instructions
4. Check PROJECT_OVERVIEW.md for architecture details
5. Visit http://localhost:8000/docs for API documentation
