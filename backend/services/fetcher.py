import httpx
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.config import get_settings
from core.database import get_db

settings = get_settings()

NEWSDATA_BASE = "https://newsdata.io/api/1/news"


def _make_id(title: str, url: str) -> str:
    raw = f"{title}{url}"
    return hashlib.md5(raw.encode()).hexdigest()


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def _clean_article(raw: Dict[str, Any]) -> Optional[Dict]:
    title = (raw.get("title") or "").strip()
    if not title or len(title) < 10:
        return None

    url = raw.get("link") or raw.get("url") or ""
    article_id = _make_id(title, url)

    content = raw.get("content") or raw.get("description") or ""
    description = raw.get("description") or ""

    return {
        "article_id": article_id,
        "title": title,
        "description": description[:500] if description else None,
        "content": content[:3000] if content else None,
        "url": url,
        "image_url": raw.get("image_url"),
        "source_name": raw.get("source_name") or raw.get("source_id"),
        "published_at": _parse_date(raw.get("pubDate")),
        "category": raw.get("category") or [],
        "keywords": raw.get("keywords") or [],
        "language": raw.get("language", "en"),
        "summary": None,
        "sentiment": None,
        "sentiment_score": None,
        "insights": [],
        "processed": False,
    }


async def fetch_and_store(max_pages: int = 5) -> int:
    """Fetch articles from NewsData.io with pagination, clean & deduplicate, store in MongoDB."""
    db = get_db()
    stored = 0
    next_page = None

    async with httpx.AsyncClient(timeout=30) as client:
        for _ in range(max_pages):
            params = {
                "apikey": settings.NEWSDATA_API_KEY,
                "q": settings.NEWS_QUERY,
                "language": settings.NEWS_LANGUAGE,
                "size": 10,
            }
            if next_page:
                params["page"] = next_page

            try:
                resp = await client.get(NEWSDATA_BASE, params=params)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"❌ Fetch error: {e}")
                break

            results: List[Dict] = data.get("results") or []
            next_page = data.get("nextPage")

            cleaned = [_clean_article(r) for r in results]
            cleaned = [a for a in cleaned if a is not None]

            if not cleaned:
                break

            for article in cleaned:
                try:
                    await db.articles.update_one(
                        {"article_id": article["article_id"]},
                        {"$setOnInsert": article},
                        upsert=True,
                    )
                    stored += 1
                except Exception as e:
                    print(f"⚠️ DB insert error: {e}")

            if not next_page:
                break

    print(f"✅ Fetched & stored {stored} articles")
    return stored
