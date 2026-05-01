# 🚀 RAG Academic Assistant - Production Deployment

A complete deployment setup for your RAG Academic Assistant using modern cloud platforms.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (Vercel)      │◄──►│   (Railway)     │◄──►│  (Supabase)     │
│   Next.js       │    │   FastAPI       │    │  PostgreSQL     │
│   React         │    │   Python        │    │  + pgvector     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Deployment Files Created

- `vercel.json` - Vercel deployment configuration
- `railway.toml` - Railway deployment configuration  
- `Dockerfile` - Container configuration for backend
- `docker-compose.yml` - Local development environment
- `.env.production` - Production environment variables template
- `DEPLOYMENT_GUIDE.md` - Detailed step-by-step deployment guide
- `deploy.bat` / `deploy.sh` - Automated deployment helper scripts

## 🚀 Quick Start

### 1. Prepare for Deployment
```bash
# Windows
deploy.bat

# Linux/Mac
./deploy.sh
```

### 2. Follow the Deployment Guide
Open `DEPLOYMENT_GUIDE.md` and follow the step-by-step instructions.

## 🌐 Platform Choices

### Frontend: Vercel
- **Why**: Excellent Next.js support, global CDN, automatic deployments
- **Cost**: Free tier (100GB bandwidth, 1000 function invocations)
- **Scaling**: $20/month for Pro (unlimited bandwidth)

### Backend: Railway
- **Why**: Simple Python deployment, persistent storage, good free tier
- **Cost**: $5 credit trial, then $5/month
- **Alternative**: Render (similar pricing and features)

### Database: Supabase
- **Why**: PostgreSQL + pgvector for vector search, generous free tier
- **Cost**: Free tier (500MB database, 2GB bandwidth)
- **Alternative**: Neon, PlanetScale (for non-vector use cases)

## 🔧 Environment Variables

### Frontend (.env.production)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_APP_NAME=RAG Academic Assistant
```

### Backend (Railway Environment Variables)
```bash
# Core
SECRET_KEY=your-super-secret-key
OPENROUTER_API_KEY=your-openrouter-key
ALLOWED_ORIGINS=https://your-app.vercel.app

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# AI Models
REASONING_MODEL=deepseek/deepseek-chat
ENABLE_REASONING=true
```

## 🧪 Local Development

### Using Docker Compose
```bash
# Set your OpenRouter API key
export OPENROUTER_API_KEY=your-key-here

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (new terminal)
npm install
npm run dev
```

## 📊 Monitoring & Maintenance

### Health Checks
- Backend: `https://your-backend.railway.app/health`
- Frontend: Monitor Vercel dashboard
- Database: Check Supabase dashboard

### Logs
- **Railway**: Dashboard → Logs tab
- **Vercel**: Dashboard → Functions tab
- **Supabase**: Dashboard → Logs & Reports

### Scaling Triggers
- **CPU/Memory**: >80% sustained usage
- **Response Time**: >2 seconds average
- **Error Rate**: >5% of requests
- **Database**: >80% storage used

## 🔒 Security Checklist

- [ ] Strong SECRET_KEY generated
- [ ] Database passwords are secure
- [ ] CORS origins properly configured
- [ ] HTTPS enforced on all endpoints
- [ ] API keys stored as environment variables
- [ ] Rate limiting enabled (if needed)
- [ ] File upload size limits set
- [ ] Input validation implemented

## 💰 Cost Estimation

### Monthly Costs (USD)
| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Vercel | $0 | $20/month |
| Railway | $5 credit | $5-20/month |
| Supabase | $0 | $25/month |
| OpenRouter | Pay-per-use | ~$5-50/month |
| **Total** | **~$5/month** | **$55-95/month** |

### Usage Estimates
- **Light usage**: 100 queries/day → ~$5/month
- **Medium usage**: 1000 queries/day → ~$25/month  
- **Heavy usage**: 10000 queries/day → ~$75/month

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Node.js/Python versions
   - Verify all dependencies in package.json/requirements.txt
   - Check build logs for specific errors

2. **CORS Errors**
   - Verify ALLOWED_ORIGINS includes your frontend URL
   - Check protocol (http vs https)
   - Ensure no trailing slashes

3. **Database Connection**
   - Verify DATABASE_URL format
   - Check Supabase project status
   - Test connection from Railway logs

4. **API Key Issues**
   - Verify OpenRouter API key is valid
   - Check rate limits and credits
   - Ensure key has proper permissions

### Getting Help
- **Railway**: [Discord](https://discord.gg/railway) | [Docs](https://docs.railway.app)
- **Vercel**: [Discord](https://discord.gg/vercel) | [Docs](https://vercel.com/docs)
- **Supabase**: [Discord](https://discord.supabase.com) | [Docs](https://supabase.com/docs)

## 🎯 Next Steps

After successful deployment:

1. **Custom Domain**: Add your own domain to Vercel
2. **CDN**: Configure file upload CDN (Cloudinary, AWS S3)
3. **Monitoring**: Set up Sentry, LogRocket, or similar
4. **Backup**: Implement database backup strategy
5. **CI/CD**: Add GitHub Actions for automated deployments
6. **Testing**: Set up staging environment
7. **Analytics**: Add user analytics and usage tracking

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review platform-specific documentation
3. Check community forums and Discord channels
4. Create an issue in your repository with detailed logs

---

**Happy Deploying! 🚀**