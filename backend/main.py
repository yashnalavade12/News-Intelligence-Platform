from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.database import connect_db, close_db, ensure_indexes
from routers.articles import router as articles_router
from services.scheduler import start_scheduler, stop_scheduler
from services.fetcher import fetch_and_store
from services.ai_processor import process_unprocessed


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    await ensure_indexes()
    # Seed initial data on first run
    await fetch_and_store(max_pages=10)
    await process_unprocessed(batch_size=100)
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()
    await close_db()


app = FastAPI(
    title="AI News Intelligence API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI News Intelligence API"}
