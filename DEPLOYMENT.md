# 📋 Local Deployment Guide - News Intelligence

## Prerequisites
- Python 3.9+ ✓
- Node.js 16+ ✓
- MongoDB (local or remote) - You have connection ready ✓
- NewsData.io API key (free tier available)

---

## Step 1: Backend Setup

### 1.1 Create Environment File
```bash
cd backend
cp .env.example .env
```

### 1.2 Edit `.env` with your credentials
```
NEWSDATA_API_KEY=<YOUR_API_KEY>          # Get from https://newsdata.io/register
MONGODB_URI=<YOUR_MONGODB_URI>           # You already have this
DB_NAME=news_intelligence
FETCH_INTERVAL_MINUTES=60
NEWS_QUERY=technology,AI,science
NEWS_LANGUAGE=en
```

### 1.3 Install Python Dependencies
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model (required for NER)
python -m spacy download en_core_web_sm
```

### 1.4 Start Backend Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✓ Backend will run at: http://localhost:8000
✓ API Documentation: http://localhost:8000/docs
✓ Health check: http://localhost:8000/health

---

## Step 2: Frontend Setup

### 2.1 Install Dependencies
```bash
cd frontend
npm install
```

### 2.2 Start Development Server
```bash
npm start
```

✓ Frontend will run at: http://localhost:3000
✓ Automatically opens in browser

---

## Step 3: Verify Everything Works

1. **Backend Health**: Visit http://localhost:8000/health
   - Should return: `{"status": "ok", "service": "AI News Intelligence API"}`

2. **API Docs**: Visit http://localhost:8000/docs
   - Interactive Swagger UI with all endpoints

3. **Frontend**: Visit http://localhost:3000
   - Dashboard should load with article data

4. **MongoDB**: Check database
   ```bash
   # If using MongoDB locally
   mongosh
   > use news_intelligence
   > db.articles.countDocuments()
   ```

---

## Troubleshooting

### MongoDB Connection Issues
- Verify URI format: `mongodb+srv://user:password@cluster/dbname` or `mongodb://localhost:27017`
- Check username/password are URL-encoded if they contain special characters
- Test connection: `mongosh "your_connection_string"`

### Backend Won't Start
```bash
# Clear any existing processes
lsof -i :8000  # Check what's using port 8000
kill -9 <PID>  # Kill the process

# Or use different port
uvicorn main:app --reload --port 8001
```

### Frontend Can't Connect to Backend
- Ensure backend is running on port 8000
- Check `frontend/package.json` has correct proxy: `"proxy": "http://localhost:8000"`
- Clear browser cache: Ctrl+Shift+Del

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

---

## Performance Notes

The ML pipeline processes articles in 6 stages:
1. **Summarization** (2-3s per article)
2. **Sentiment Analysis** (0.5s)
3. **Named Entity Recognition** (1s)
4. **Zero-Shot Classification** (2-3s)
5. **Semantic Embeddings** (1-2s)
6. **Topic Clustering** (batch job, runs periodically)

Initial data processing may take 5-10 minutes. Check backend logs for progress.

---

## Next Steps

1. ✅ Get NewsData.io API key
2. ✅ Create `.env` file with credentials
3. ✅ Install backend dependencies
4. ✅ Install frontend dependencies
5. ✅ Start both servers
6. ✅ Verify at http://localhost:3000

**Need help?** Check the API docs at http://localhost:8000/docs
