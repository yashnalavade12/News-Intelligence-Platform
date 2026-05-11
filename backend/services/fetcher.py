"""
RSS Feed Fetcher — replaces NewsData.io API.
Fetches from free public RSS feeds (BBC, Ars Technica, Hacker News, etc.)
Zero API keys needed.
"""

import feedparser
import hashlib
import json
from datetime import datetime
from time import mktime
from typing import Optional
from core.database import get_db

RSS_FEEDS = [
    ("BBC Technology", "http://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("BBC Science", "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("Hacker News", "https://hnrss.org/newest?points=50&count=30"),
    ("NASA Breaking", "https://www.nasa.gov/news-release/feed/"),
    ("NPR Science", "https://feeds.npr.org/1007/rss.xml"),
    ("Phys.org", "https://phys.org/rss-feed/"),
]


def _make_id(title: str, url: str) -> str:
    raw = f"{title}{url}"
    return hashlib.md5(raw.encode()).hexdigest()


def _parse_date(entry) -> Optional[str]:
    for attr in ("published_parsed", "updated_parsed"):
        parsed = getattr(entry, attr, None)
        if parsed:
            try:
                return datetime.fromtimestamp(mktime(parsed)).isoformat()
            except Exception:
                continue
    return datetime.utcnow().isoformat()


def _clean_entry(entry, source_name: str) -> Optional[dict]:
    title = (getattr(entry, "title", "") or "").strip()
    if not title or len(title) < 10:
        return None

    url = getattr(entry, "link", "") or ""
    article_id = _make_id(title, url)

    # Get description / summary
    description = (getattr(entry, "summary", "") or "").strip()
    # Strip HTML tags from description
    import re
    description = re.sub(r"<[^>]+>", "", description).strip()
    content = getattr(entry, "content", [{}])
    if isinstance(content, list) and content:
        content = content[0].get("value", description)
    else:
        content = description
    content = re.sub(r"<[^>]+>", "", str(content)).strip()

    # Try to get image
    image_url = None
    if hasattr(entry, "media_content") and entry.media_content:
        image_url = entry.media_content[0].get("url")
    elif hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        image_url = entry.media_thumbnail[0].get("url")

    # Get categories/tags
    categories = []
    if hasattr(entry, "tags"):
        categories = [t.get("term", "") for t in entry.tags if t.get("term")]

    return {
        "article_id": article_id,
        "title": title,
        "description": description[:500] if description else None,
        "content": content[:3000] if content else None,
        "url": url,
        "image_url": image_url,
        "source_name": source_name,
        "published_at": _parse_date(entry),
        "category": json.dumps(categories[:5]),
        "keywords": json.dumps([]),
        "language": "en",
        "summary": None,
        "sentiment": None,
        "sentiment_score": None,
        "entities": json.dumps({}),
        "topics": json.dumps([]),
        "embedding": json.dumps([]),
        "insights": json.dumps([]),
        "cluster_id": None,
        "cluster_label": None,
        "processed": 0,
        "created_at": datetime.utcnow().isoformat(),
    }


async def fetch_and_store(**kwargs) -> int:
    """Fetch articles from RSS feeds, clean & deduplicate, store in MongoDB."""
    db = get_db()
    articles_collection = db["articles"]
    stored = 0

    for source_name, feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            entries = feed.entries or []
            print(f"📡 {source_name}: {len(entries)} entries")
        except Exception as e:
            print(f"❌ Feed error ({source_name}): {e}")
            continue

        for entry in entries:
            article = _clean_entry(entry, source_name)
            if not article:
                continue
            try:
                # Convert JSON strings to actual objects for MongoDB
                article_doc = {
                    "title": article["title"],
                    "description": article["description"],
                    "content": article["content"],
                    "url": article["url"],
                    "image_url": article["image_url"],
                    "source": article["source_name"],
                    "published_at": article["published_at"],
                    "category": json.loads(article["category"]),
                    "keywords": json.loads(article["keywords"]),
                    "language": article["language"],
                    "summary": article["summary"],
                    "sentiment": article["sentiment"],
                    "sentiment_score": article["sentiment_score"],
                    "entities": json.loads(article["entities"]),
                    "topics": json.loads(article["topics"]),
                    "embedding": json.loads(article["embedding"]),
                    "insights": json.loads(article["insights"]),
                    "cluster_id": article["cluster_id"],
                    "cluster_label": article["cluster_label"],
                    "processed": bool(article["processed"]),
                    "created_at": article["created_at"],
                }
                
                # Try to insert; if URL exists, skip (duplicate)
                result = await articles_collection.update_one(
                    {"url": article["url"]},
                    {"$setOnInsert": article_doc},
                    upsert=True
                )
                
                if result.upserted_id or result.matched_count == 0:
                    stored += 1
                    
            except Exception as e:
                print(f"⚠️ DB insert error: {e}")

    print(f"✅ Fetched & stored {stored} articles from RSS feeds")
    return stored
