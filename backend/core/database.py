"""
SQLite database layer — replaces MongoDB for zero-config deployment.
Uses aiosqlite for async access. JSON columns store complex fields.
"""

import aiosqlite
import sqlite3
import os
import json
from core.config import get_settings

settings = get_settings()
DB_PATH = settings.DB_PATH

_db: aiosqlite.Connection = None


async def connect_db():
    global _db
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    _db = await aiosqlite.connect(DB_PATH)
    _db.row_factory = sqlite3.Row
    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute("PRAGMA synchronous=NORMAL")
    print("✅ Connected to SQLite")


async def close_db():
    global _db
    if _db:
        await _db.close()
        print("🔌 Disconnected from SQLite")


def get_db() -> aiosqlite.Connection:
    return _db


def row_to_dict(row) -> dict:
    """Convert sqlite3.Row to a dict, parsing JSON columns."""
    if row is None:
        return None
    d = dict(row)
    for key in ("category", "keywords", "topics", "insights", "embedding"):
        if key in d and isinstance(d[key], str):
            try:
                d[key] = json.loads(d[key])
            except (json.JSONDecodeError, TypeError):
                d[key] = []
    if "entities" in d and isinstance(d["entities"], str):
        try:
            d["entities"] = json.loads(d["entities"])
        except (json.JSONDecodeError, TypeError):
            d["entities"] = {}
    if "processed" in d:
        d["processed"] = bool(d["processed"])
    return d


async def ensure_indexes():
    db = get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            content TEXT,
            url TEXT,
            image_url TEXT,
            source_name TEXT,
            published_at TEXT,
            category TEXT DEFAULT '[]',
            keywords TEXT DEFAULT '[]',
            language TEXT DEFAULT 'en',
            summary TEXT,
            sentiment TEXT,
            sentiment_score REAL,
            entities TEXT DEFAULT '{}',
            topics TEXT DEFAULT '[]',
            embedding TEXT DEFAULT '[]',
            insights TEXT DEFAULT '[]',
            cluster_id INTEGER,
            cluster_label TEXT,
            processed INTEGER DEFAULT 0,
            created_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_published ON articles(published_at DESC);
        CREATE INDEX IF NOT EXISTS idx_sentiment ON articles(sentiment);
        CREATE INDEX IF NOT EXISTS idx_processed ON articles(processed);
        CREATE INDEX IF NOT EXISTS idx_cluster ON articles(cluster_id);
    """)
    await db.commit()
    print("📑 Tables & indexes ensured")
