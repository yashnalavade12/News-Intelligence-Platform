from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.config import get_settings
from services.fetcher import fetch_and_store
from services.ai_processor import process_unprocessed

settings = get_settings()
scheduler = AsyncIOScheduler()


async def _pipeline_job():
    print("🔄 Running scheduled pipeline …")
    await fetch_and_store()
    await process_unprocessed(batch_size=50)


def start_scheduler():
    scheduler.add_job(
        _pipeline_job,
        "interval",
        minutes=settings.FETCH_INTERVAL_MINUTES,
        id="news_pipeline",
        replace_existing=True,
    )
    scheduler.start()
    print(f"⏰ Scheduler started — runs every {settings.FETCH_INTERVAL_MINUTES} min")


def stop_scheduler():
    scheduler.shutdown(wait=False)
    print("⏹️ Scheduler stopped")
