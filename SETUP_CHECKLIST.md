# ✅ Pre-Deployment Checklist

## 1️⃣ Prerequisites Check

### System Requirements
- [ ] Python 3.9+ installed (`python --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] MongoDB connection string ready

### Verify Tools
```powershell
# Check Python
python --version

# Check Node.js
node --version
npm --version
```

---

## 2️⃣ API Credentials

### NewsData.io API Key
- [ ] Create account at https://newsdata.io/register
- [ ] Copy your API key from dashboard
- [ ] Key format: Should look like `xxxxxxxxxxxxx`

### MongoDB Connection
- [ ] You have your MongoDB URI ready
- [ ] Test connection locally or in cloud console
- [ ] URI format: 
  - Cloud: `mongodb+srv://user:password@cluster.mongodb.net/news_intelligence`
  - Local: `mongodb://localhost:27017`

---

## 3️⃣ Environment Configuration

### Create `.env` File
```powershell
cd backend
cp .env.example .env
```

### Fill in `.env`
```
NEWSDATA_API_KEY=<YOUR_API_KEY>
MONGODB_URI=<YOUR_MONGODB_URI>
DB_NAME=news_intelligence
FETCH_INTERVAL_MINUTES=60
NEWS_QUERY=technology,AI,science
NEWS_LANGUAGE=en
```

---

## 4️⃣ Backend Setup

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Download NLP model
python -m spacy download en_core_web_sm
```

**Verify Backend:**
```powershell
# Start the server
uvicorn main:app --reload

# In another terminal, test health endpoint
curl http://localhost:8000/health
```

✅ Expected: `{"status":"ok","service":"AI News Intelligence API"}`

---

## 5️⃣ Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Start dev server
npm start
```

✅ Should open http://localhost:3000 automatically

---

## 6️⃣ Verification Checklist

### Backend Running?
- [ ] `http://localhost:8000/health` returns `{"status": "ok"}`
- [ ] `http://localhost:8000/docs` shows Swagger UI
- [ ] Backend terminal shows no errors

### Frontend Running?
- [ ] `http://localhost:3000` loads the dashboard
- [ ] No console errors in browser DevTools
- [ ] Frontend can reach backend (check Network tab)

### Data Pipeline?
- [ ] Backend log shows articles being fetched
- [ ] MongoDB has documents in `news_intelligence.articles` collection
- [ ] Frontend displays article cards with data

---

## 7️⃣ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | Use `lsof -i :8000` to find process, then `kill -9 <PID>` |
| Port 3000 already in use | Change in frontend/.env or use `npm start -- --port 3001` |
| `.env` not found | Run `cp .env.example .env` in backend/ |
| spaCy model missing | Run `python -m spacy download en_core_web_sm` |
| MongoDB connection fails | Verify URI, check firewall, test with `mongosh` |
| CORS errors in browser | Backend CORS is enabled by default, restart backend |
| Dependencies failed to install | Update pip: `python -m pip install --upgrade pip` |

---

## 🚀 Quick Start Scripts

### Option A: Automated Setup (Windows)
```powershell
.\setup.ps1
```

### Option B: Manual Step-by-Step

**Terminal 1 - Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm start
```

---

## 📊 Expected Behavior

1. **First Launch**: Backend will:
   - Connect to MongoDB
   - Create indexes
   - Fetch initial news articles (10 pages)
   - Process articles through ML pipeline (takes 5-10 minutes)
   - Start background scheduler

2. **Frontend**: Will display:
   - Dashboard with article cards
   - Statistics bar at top
   - Filter options (sentiment, entities, topics)
   - Pagination controls

3. **Continuous**: Background scheduler will:
   - Fetch fresh news every 60 minutes
   - Process new articles through ML pipeline
   - Update MongoDB collection

---

## 📝 Troubleshooting Commands

```powershell
# Check Python virtual environment is active
# (Look for (venv) prefix in terminal)

# Check all ports in use
netstat -ano

# List specific port
netstat -ano | findstr :8000

# Kill process by port
taskkill /PID <PID> /F

# Check Python packages
pip list | grep fastapi

# Check MongoDB connection
mongosh "your_connection_string"

# Check frontend can reach backend
curl http://localhost:8000/health
```

---

## 🎯 Success Indicators

✅ **You're ready when you see:**
- Backend console: `✅ Connected to MongoDB`
- Backend console: Fetching/Processing articles...
- Frontend: Dashboard loads with article data
- No errors in browser console

---

**Questions?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed documentation.
