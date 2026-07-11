# Gurukul — RAG Academic Assistant

An AI-powered academic assistant that lets you upload documents and ask questions against them. Answers come with cited sources so you can trace every response back to the original material.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | FastAPI, LangChain, Python 3.11 |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Search | FAISS (persisted to disk) |
| LLM / Reasoning | OpenRouter (DeepSeek, configurable) |
| Document Parsing | PyMuPDF, python-docx, pandas |

## Features

- **Multi-format document upload** — PDF, DOCX, TXT, CSV, XLSX
- **Persistent vector store** — FAISS index saved to disk, survives restarts and grows incrementally
- **Academic reasoning engine** — multi-step chain-of-thought via OpenRouter
- **Cited responses** — every answer references the exact source chunk with confidence score
- **Mind-map & Mermaid rendering** — visual knowledge graphs from query results
- **Admin panel** — manage documents, view system stats, trigger re-ingestion
- **Auth** — JWT-based login/register

---

## Project Structure

```
.
├── src/                        # Next.js frontend
│   ├── app/                    # App router pages
│   │   ├── page.tsx            # Landing page
│   │   ├── chat/               # Chat interface
│   │   ├── admin/              # Admin panel
│   │   └── auth/               # Login / Register
│   ├── components/
│   │   ├── chat/               # ChatInterface, MessageBubble, CitationDisplay, etc.
│   │   ├── admin/              # DocumentUpload, DocumentList
│   │   └── ui/                 # Button, Input
│   ├── hooks/                  # useAuth, useAcademicQuery
│   └── lib/                    # api.ts (all API calls), utils.ts
│
├── backend/                    # FastAPI backend
│   ├── main.py                 # Application entry point
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── api/v1/             # auth, admin, query, documents routers
│       ├── core/               # rag_engine, reasoning_engine, document_processor, config
│       └── models/             # schemas, database
│
├── vercel.json                 # Frontend deployment (Vercel)
├── railway.toml                # Backend deployment (Railway)
├── Dockerfile                  # Backend container
├── docker-compose.yml          # Local full-stack dev environment
├── init.sql                    # Local PostgreSQL + pgvector setup
└── DEPLOYMENT_GUIDE.md         # Step-by-step production deployment
```

---

## Local Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- An [OpenRouter](https://openrouter.ai) API key

### 1. Clone and install

```bash
git clone <your-repo-url>
cd frontend   # or whatever the root folder is named
npm install
```

### 2. Configure environment

**Frontend** — copy and fill in the backend URL:
```bash
cp .env.local.example .env.local
```
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** — copy and fill in secrets:
```bash
cp backend/.env.example backend/.env
```

Key variables to set in `backend/.env`:
```env
SECRET_KEY=generate-a-random-string
OPENROUTER_API_KEY=your-openrouter-key
ALLOWED_ORIGINS=http://localhost:3000
ENABLE_REASONING=true
REASONING_MODEL=deepseek/deepseek-chat
```

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start the frontend

```bash
# from repo root
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Docker alternative

```bash
# Copy and fill your OpenRouter key first
cp backend/.env.example backend/.env

docker-compose up -d
```

This starts the backend, frontend, and a local PostgreSQL + pgvector instance together.

---

## API Overview

### Auth `/api/v1/auth`
| Method | Path | Description |
|---|---|---|
| POST | `/login/json` | Login, returns JWT |
| POST | `/register` | Register new user |
| GET | `/me` | Get current user |

### Admin `/api/v1/admin`
| Method | Path | Description |
|---|---|---|
| POST | `/upload` | Upload document |
| GET | `/documents` | List documents |
| DELETE | `/documents/{id}` | Delete document |
| POST | `/ingest/{id}` | Trigger processing |
| GET | `/stats` | System stats |

### Query `/api/v1/query`
| Method | Path | Description |
|---|---|---|
| POST | `/` | Submit a question |
| GET | `/history` | Query history |
| GET | `/{id}` | Query details |

### Documents `/api/v1/documents`
| Method | Path | Description |
|---|---|---|
| GET | `/{id}/download` | Download source file |

Full API docs available at `http://localhost:8000/docs` when the backend is running.

---

## Deployment

See **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** for complete instructions.

**Summary:**
1. **Supabase** — free PostgreSQL + pgvector database
2. **Railway** — deploy the FastAPI backend (from root, uses `Dockerfile`)
3. **Vercel** — deploy the Next.js frontend

Minimum required environment variables for production:

```env
# Backend (Railway)
SECRET_KEY=<strong-random-string>
OPENROUTER_API_KEY=<your-key>
ALLOWED_ORIGINS=https://your-app.vercel.app
DATABASE_URL=postgresql://...  # from Supabase

# Frontend (Vercel)
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

## Environment Variables Reference

### Frontend

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | ✅ | Backend base URL |

### Backend

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | JWT signing key |
| `OPENROUTER_API_KEY` | ✅ | — | OpenRouter API key |
| `ALLOWED_ORIGINS` | ✅ | — | Comma-separated CORS origins |
| `REASONING_MODEL` | — | `deepseek/deepseek-chat` | OpenRouter model for reasoning |
| `ENABLE_REASONING` | — | `true` | Toggle reasoning engine |
| `EMBEDDING_MODEL` | — | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `CHUNK_SIZE` | — | `1000` | Document chunk size |
| `CHUNK_OVERLAP` | — | `200` | Chunk overlap size |
| `DATABASE_URL` | — | — | PostgreSQL URI (production) |

---

## Notes & Known Limitations

- The vector store uses FAISS on disk. It does not support efficient single-document deletion — deleting a document removes it from the metadata but its vectors remain until a full re-index. For production at scale, consider Pinecone or Weaviate.
- The default LLM is routed through OpenRouter. Model choice is configurable via `REASONING_MODEL`.
- File uploads are stored on the local filesystem. On Railway this requires a persistent volume mount at `/app/uploads`. For long-term production, use object storage (S3, Supabase Storage, Cloudinary).
