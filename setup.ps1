# ════════════════════════════════════════════════════════════
# News Intelligence - Local Development Startup Script (PowerShell)
# ════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "🚀 News Intelligence - Local Deployment Setup" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Backend Setup ──
Write-Host "📦 Setting up Backend..." -ForegroundColor Yellow
Set-Location backend

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and fill in your credentials:" -ForegroundColor Yellow
    Write-Host "  - NEWSDATA_API_KEY (from https://newsdata.io/register)" -ForegroundColor Gray
    Write-Host "  - MONGODB_URI (your MongoDB connection string)" -ForegroundColor Gray
    Write-Host ""
    exit
}

# Check if venv exists
if (-not (Test-Path "venv")) {
    Write-Host "🔧 Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit
    }
}

# Activate venv
Write-Host "🔌 Activating Python virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📥 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    exit
}

# Download spaCy model
Write-Host "🧠 Downloading spaCy NER model..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm --quiet

Write-Host "✅ Backend setup complete!" -ForegroundColor Green
Write-Host ""

# ── Step 2: Frontend Setup ──
Write-Host "📦 Setting up Frontend..." -ForegroundColor Yellow
Set-Location ..\frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "🔧 Installing Node dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install Node dependencies" -ForegroundColor Red
        exit
    }
} else {
    Write-Host "✅ Node dependencies already installed" -ForegroundColor Green
}

Write-Host "✅ Frontend setup complete!" -ForegroundColor Green
Write-Host ""

# ── Summary ──
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Open PowerShell Terminal #1 and run:" -ForegroundColor White
Write-Host "     cd backend" -ForegroundColor Cyan
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "     uvicorn main:app --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Open PowerShell Terminal #2 and run:" -ForegroundColor White
Write-Host "     cd frontend" -ForegroundColor Cyan
Write-Host "     npm start" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Access your app:" -ForegroundColor Green
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   - Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
