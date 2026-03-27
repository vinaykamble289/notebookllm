# Frontend Setup & Configuration

## Current Configuration

The frontend is configured to connect to the backend API at:
- **API URL**: `http://localhost:8001`
- **Frontend URL**: `http://localhost:3000`

## Environment Variables

The API URL is configured in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Starting the Frontend

1. **Install dependencies** (if not already done):
```bash
npm install
```

2. **Start the development server**:
```bash
npm run dev
```

The frontend will start at `http://localhost:3000`

**Important**: After changing `.env.local`, you must restart the Next.js dev server for changes to take effect.

## Verifying API Connection

### Method 1: Browser Console
1. Open `http://localhost:3000/admin`
2. Open browser DevTools (F12)
3. Check the Console tab for any errors
4. Check the Network tab to see API requests

### Method 2: Test API Directly
Open browser console and run:
```javascript
fetch('http://localhost:8001/health')
  .then(r => r.json())
  .then(console.log)
```

Expected response:
```json
{
  "status": "healthy",
  "rag_engine": "initialized"
}
```

## Available Pages

### Admin Panel
**URL**: `http://localhost:3000/admin`

Features:
- Upload documents (PDF, DOCX, TXT, CSV, XLSX)
- View all uploaded documents
- Check processing status
- Download documents
- Delete documents

### Chat Interface
**URL**: `http://localhost:3000/chat`

Features:
- Ask questions about uploaded documents
- Get answers with citations
- View source documents
- Optional mindmap visualization
- Optional audio responses

### Home Page
**URL**: `http://localhost:3000`

Landing page with navigation to admin and chat.

## API Endpoints Used

The frontend uses these backend endpoints:

### Authentication
- `POST /api/v1/auth/login/json` - Login
- `POST /api/v1/auth/register` - Register
- `GET /api/v1/auth/me` - Get current user

### Documents
- `POST /api/v1/admin/upload` - Upload document
- `GET /api/v1/admin/documents` - List documents
- `GET /api/v1/admin/documents/{id}` - Get document
- `DELETE /api/v1/admin/documents/{id}` - Delete document
- `POST /api/v1/admin/ingest/{id}` - Trigger processing
- `GET /api/v1/admin/documents/{id}/status` - Get status
- `GET /api/v1/documents/{id}/download` - Download

### Query
- `POST /api/v1/query` - Submit question
- `GET /api/v1/query/history` - Query history

### Admin
- `GET /api/v1/admin/stats` - System statistics

## Troubleshooting

### CORS Errors
If you see CORS errors in the browser console:

1. **Verify backend is running**:
```bash
curl http://localhost:8001/health
```

2. **Check backend CORS configuration**:
The backend should allow `http://localhost:3000` in `backend/.env`:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

3. **Restart both servers**:
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
npm run dev
```

### Network Errors
If you see "Network Error" in console:

1. **Verify API URL**:
Check `.env.local` has correct URL:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

2. **Restart frontend** after changing `.env.local`:
```bash
npm run dev
```

3. **Check backend is accessible**:
```bash
curl http://localhost:8001/api/v1/admin/documents?page=1&per_page=10
```

### Upload Fails
If document upload fails:

1. **Check file size** (max 50MB)
2. **Check file type** (PDF, DOCX, TXT, CSV, XLSX)
3. **Check backend logs** for errors
4. **Verify backend has write permissions** to `uploads/` directory

### No Documents Showing
If documents list is empty:

1. **Upload a test document** via admin panel
2. **Wait for processing** (status should change to "completed")
3. **Check backend logs** for processing errors
4. **Verify vector store** is initialized:
```bash
curl http://localhost:8001/api/v1/admin/stats
```

## Development Tips

### Hot Reload
Next.js automatically reloads when you change files in `src/`.

### API Client
All API calls go through `src/lib/api.ts`. This file:
- Configures axios with base URL
- Adds authentication headers
- Handles errors globally
- Provides typed API methods

### Adding New API Endpoints
1. Add endpoint to backend
2. Add method to `src/lib/api.ts`
3. Use in components

Example:
```typescript
// In src/lib/api.ts
export const myApi = {
  getData: () => api.get('/v1/my-endpoint'),
};

// In component
import { myApi } from '@/lib/api';

const data = await myApi.getData();
```

## Testing the Integration

### Test 1: Upload Document
1. Go to `http://localhost:3000/admin`
2. Drag and drop a PDF file
3. Wait for upload to complete
4. Check status changes to "processing" then "completed"

### Test 2: Query Document
1. Go to `http://localhost:3000/chat`
2. Type a question about the uploaded document
3. Submit and wait for response
4. Verify citations are shown

### Test 3: View Statistics
1. Open browser console
2. Run:
```javascript
fetch('http://localhost:8001/api/v1/admin/stats')
  .then(r => r.json())
  .then(console.log)
```
3. Should show document count, chunk count, etc.

## Production Deployment

For production, update `.env.local` with your production API URL:
```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

And build:
```bash
npm run build
npm start
```

## Quick Start Checklist

- [ ] Backend running on port 8001
- [ ] `.env.local` has `NEXT_PUBLIC_API_URL=http://localhost:8001`
- [ ] Frontend running on port 3000
- [ ] Can access `http://localhost:3000/admin`
- [ ] Can access `http://localhost:3000/chat`
- [ ] No CORS errors in browser console
- [ ] Can upload a test document
- [ ] Can query the document

## Support

If you encounter issues:
1. Check browser console for errors
2. Check backend terminal for errors
3. Verify both servers are running
4. Check `FIXED_ISSUES.md` for common problems
5. Review `SETUP.md` for detailed setup instructions
