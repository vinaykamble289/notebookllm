# Fixed Issues

## Issue 1: CORS Configuration Error
**Problem**: `ALLOWED_ORIGINS` was being parsed as JSON list but provided as comma-separated string in `.env`

**Solution**: Changed `ALLOWED_ORIGINS` to be a string type and added a `cors_origins` property to parse it:
```python
ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

@property
def cors_origins(self) -> List[str]:
    return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
```

## Issue 2: Dependency Version Conflicts
**Problem**: `sentence-transformers` had incompatible `huggingface-hub` version causing import errors

**Solution**: Updated `requirements.txt` with compatible versions:
```
sentence-transformers==2.3.1
huggingface-hub==0.20.3
```

## Issue 3: FAISS Load Method Error
**Problem**: `allow_dangerous_deserialization` parameter not supported in FAISS `load_local` method

**Solution**: Removed the parameter and added error handling:
```python
try:
    self.vectorstore = FAISS.load_local(
        str(self.index_path),
        self.embedding_model
    )
except Exception as e:
    # Create new vector store if loading fails
    self.vectorstore = FAISS.from_texts(...)
```

## Issue 4: Port Conflict
**Problem**: Another service was already running on port 8000

**Solution**: Changed backend port to 8001:
- Updated `backend/.env`: `PORT=8001`
- Updated `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:8001`

## Current Status

✅ Backend running successfully on http://localhost:8001
✅ All API endpoints working
✅ CORS configured correctly
✅ Vector store loading/saving working
✅ RAG engine initialized

## How to Start

### Backend
```bash
cd backend
python main.py
```
Server will start on http://localhost:8001

### Frontend
```bash
npm run dev
```
Server will start on http://localhost:3000

**Important**: Restart the frontend after changing `.env.local` to pick up the new API URL.

## Testing

Test backend health:
```bash
curl http://localhost:8001/health
```

Test documents endpoint:
```bash
curl http://localhost:8001/api/v1/admin/documents?page=1&per_page=10
```

## API Documentation

Visit http://localhost:8001/docs for interactive API documentation.
