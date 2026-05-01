# 🚀 Deployment Guide

This guide will help you deploy your RAG Academic Assistant to production using free/affordable cloud services.

## 📋 Architecture Overview

- **Frontend**: Vercel (Next.js) - Free tier
- **Backend**: Railway (FastAPI) - $5/month with generous free trial
- **Vector Database**: Supabase (PostgreSQL + pgvector) - Free tier
- **File Storage**: Railway volumes or Supabase Storage - Free tier

## 🔧 Prerequisites

1. **Accounts needed**:
   - [Vercel](https://vercel.com) account
   - [Railway](https://railway.app) account  
   - [Supabase](https://supabase.com) account
   - [OpenRouter](https://openrouter.ai) API key

2. **Tools**:
   - Git repository (GitHub/GitLab)
   - Node.js 18+ (for local development)
   - Python 3.11+ (for local development)

## 🗄️ Step 1: Setup Supabase (Vector Database)

### 1.1 Create Supabase Project
1. Go to [Supabase](https://supabase.com) and create a new project
2. Choose a region close to your users
3. Set a strong database password
4. Wait for the project to be ready

### 1.2 Enable pgvector Extension
1. Go to **Database** → **Extensions**
2. Search for `vector` and enable the `pgvector` extension
3. This allows storing and querying vector embeddings

### 1.3 Create Tables (Optional - for future database integration)
```sql
-- Create documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    content TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    file_type VARCHAR(50)
);

-- Create embeddings table
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_text TEXT,
    embedding vector(384), -- Adjust dimension based on your model
    chunk_index INTEGER
);

-- Create index for vector similarity search
CREATE INDEX ON document_embeddings USING ivfflat (embedding vector_cosine_ops);
```

### 1.4 Get Connection Details
1. Go to **Settings** → **Database**
2. Copy the connection string (URI format)
3. Note down the project URL and API keys

## 🚂 Step 2: Deploy Backend to Railway

### 2.1 Prepare Repository
1. Ensure your code is in a Git repository
2. Make sure `railway.toml` and `Dockerfile` are in the root directory

### 2.2 Deploy to Railway
1. Go to [Railway](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository
4. Railway will automatically detect the Python app

### 2.3 Configure Environment Variables
In Railway dashboard, go to **Variables** and add:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Security (Generate strong values)
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (Update after Vercel deployment)
ALLOWED_ORIGINS=https://your-app.vercel.app

# OpenRouter AI (Required)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_APP_NAME=RAG-Academic-Assistant

# Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
REASONING_MODEL=deepseek/deepseek-chat
REASONING_MAX_TOKENS=2048
REASONING_TEMPERATURE=0.7
ENABLE_REASONING=true

# Vector Store
FAISS_INDEX_NAME=documents_index
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# File Storage
UPLOAD_DIR=./uploads
VECTOR_STORE_DIR=./vector_store

# Database (Supabase)
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

### 2.4 Add Persistent Storage (Optional)
1. In Railway, go to **Settings** → **Volumes**
2. Add volume: `/app/uploads` (for file uploads)
3. Add volume: `/app/vector_store` (for FAISS index)

### 2.5 Deploy and Test
1. Railway will automatically deploy
2. Check logs for any errors
3. Test the health endpoint: `https://your-app.railway.app/health`

## 🌐 Step 3: Deploy Frontend to Vercel

### 3.1 Prepare Frontend
1. Update `vercel.json` with your backend URL
2. Ensure `package.json` has correct build scripts

### 3.2 Deploy to Vercel
1. Go to [Vercel](https://vercel.com)
2. Click **"New Project"**
3. Import your Git repository
4. Vercel will auto-detect Next.js

### 3.3 Configure Environment Variables
In Vercel dashboard, go to **Settings** → **Environment Variables**:

```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_NAME=RAG Academic Assistant
NEXT_PUBLIC_VERSION=2.0.0
```

### 3.4 Update CORS
1. Go back to Railway
2. Update `ALLOWED_ORIGINS` to include your Vercel URL:
   ```bash
   ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
   ```

## 🔧 Step 4: Configuration Updates

### 4.1 Update API Base URL
Update `src/lib/api.ts` if needed:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### 4.2 Update Backend CORS
Ensure your backend allows your frontend domain in `backend/app/core/config.py`.

## 🧪 Step 5: Testing Deployment

### 5.1 Test Backend
```bash
# Health check
curl https://your-backend.railway.app/health

# Test API
curl https://your-backend.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

### 5.2 Test Frontend
1. Visit your Vercel URL
2. Try registering/logging in
3. Test document upload
4. Test query functionality

## 📊 Step 6: Monitoring and Maintenance

### 6.1 Railway Monitoring
- Check **Metrics** tab for CPU/Memory usage
- Monitor **Logs** for errors
- Set up **Alerts** for downtime

### 6.2 Vercel Monitoring
- Check **Analytics** for performance
- Monitor **Functions** tab for errors
- Review **Speed Insights**

### 6.3 Supabase Monitoring
- Check **Database** → **Reports** for usage
- Monitor **API** usage in dashboard
- Set up **Webhooks** for alerts

## 💰 Cost Breakdown

### Free Tier Limits:
- **Vercel**: 100GB bandwidth, 1000 serverless function invocations
- **Railway**: $5 credit (≈500 hours), then $5/month
- **Supabase**: 500MB database, 2GB bandwidth, 50MB file storage

### Scaling Options:
- **Railway Pro**: $20/month (8GB RAM, priority support)
- **Vercel Pro**: $20/month (unlimited bandwidth)
- **Supabase Pro**: $25/month (8GB database, 250GB bandwidth)

## 🔒 Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use strong database passwords
- [ ] Enable HTTPS only
- [ ] Configure proper CORS origins
- [ ] Set up rate limiting
- [ ] Enable Supabase RLS (Row Level Security)
- [ ] Use environment variables for all secrets
- [ ] Enable 2FA on all accounts

## 🚨 Troubleshooting

### Common Issues:

1. **CORS Errors**
   - Check ALLOWED_ORIGINS in Railway
   - Ensure frontend URL is correct

2. **Database Connection**
   - Verify DATABASE_URL format
   - Check Supabase project status

3. **File Upload Issues**
   - Check Railway volume mounts
   - Verify UPLOAD_DIR permissions

4. **OpenRouter API Errors**
   - Verify API key is correct
   - Check rate limits and credits

### Getting Help:
- Railway: [Discord](https://discord.gg/railway)
- Vercel: [Discord](https://discord.gg/vercel)
- Supabase: [Discord](https://discord.supabase.com)

## 🎉 Next Steps

After successful deployment:
1. Set up custom domain (optional)
2. Configure CDN for file uploads
3. Set up monitoring and alerts
4. Implement backup strategies
5. Add CI/CD pipelines
6. Set up staging environment

---

**Need help?** Check the troubleshooting section or reach out to the respective platform support channels.