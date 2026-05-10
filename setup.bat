@echo off
REM ════════════════════════════════════════════════════════════
REM News Intelligence - Local Development Startup Script
REM ════════════════════════════════════════════════════════════

echo.
echo 🚀 News Intelligence - Local Deployment Setup
echo ════════════════════════════════════════════════════════════
echo.

REM ── Step 1: Backend Setup ──
echo 📦 Setting up Backend...
cd backend

REM Check if .env exists
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo Please copy .env.example to .env and fill in your credentials:
    echo   - NEWSDATA_API_KEY (from https://newsdata.io/register)
    echo   - MONGODB_URI (your MongoDB connection string)
    echo.
    pause
    goto :eof
)

REM Check if venv exists
if not exist "venv" (
    echo 🔧 Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        goto :eof
    )
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    goto :eof
)

REM Download spaCy model
echo 🧠 Downloading spaCy NER model...
python -m spacy download en_core_web_sm -q

echo ✅ Backend setup complete!
echo.

REM ── Step 2: Frontend Setup ──
echo 📦 Setting up Frontend...
cd ..\frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo 🔧 Installing Node dependencies...
    call npm install
    if errorlevel 1 (
        echo ❌ Failed to install Node dependencies
        pause
        goto :eof
    )
) else (
    echo ✅ Node dependencies already installed
)

echo ✅ Frontend setup complete!
echo.

REM ── Summary ──
echo ════════════════════════════════════════════════════════════
echo ✅ Setup Complete!
echo ════════════════════════════════════════════════════════════
echo.
echo 📝 Next Steps:
echo   1. Open PowerShell Terminal #1 and run:
echo      cd backend
echo      venv\Scripts\activate
echo      uvicorn main:app --reload
echo.
echo   2. Open PowerShell Terminal #2 and run:
echo      cd frontend
echo      npm start
echo.
echo 🌐 Access your app:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
pause
