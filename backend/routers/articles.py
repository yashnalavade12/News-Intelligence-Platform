import json
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from core.database import get_db, row_to_dict
from services.fetcher import fetch_and_store
from services.ai_processor import process_unprocessed, run_topic_clustering

router = APIRouter(prefix="/api/articles", tags=["articles"])


def _serialize(row) -> dict:
    d = row_to_dict(row)
    d["id"] = str(d.pop("id", ""))
    d.pop("embedding", None)   # never send 384-d vectors to frontend
    return d


@router.get("")
async def get_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    sentiment: Optional[str] = Query(None, pattern="^(positive|negative|neutral)$"),
    topic: Optional[str] = Query(None),
    cluster_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
):
    db = get_db()
    conditions = ["processed = 1"]
    params = []

    if sentiment:
        conditions.append("sentiment = ?")
        params.append(sentiment)
    if topic:
        conditions.append("EXISTS (SELECT 1 FROM json_each(topics) WHERE json_extract(value, '$.label') = ?)")
        params.append(topic)
    if cluster_id is not None:
        conditions.append("cluster_id = ?")
        params.append(cluster_id)
    if search:
        conditions.append("(title LIKE ? OR summary LIKE ? OR source_name LIKE ?)")
        like = f"%{search}%"
        params.extend([like, like, like])

    where = " AND ".join(conditions)

    # Count
    cursor = await db.execute(f"SELECT COUNT(*) as cnt FROM articles WHERE {where}", params)
    row = await cursor.fetchone()
    total = row["cnt"]

    # Fetch page
    offset = (page - 1) * page_size
    cursor = await db.execute(
        f"SELECT * FROM articles WHERE {where} ORDER BY published_at DESC LIMIT ? OFFSET ?",
        params + [page_size, offset],
    )
    rows = await cursor.fetchall()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "articles": [_serialize(r) for r in rows],
    }


@router.get("/stats")
async def get_stats():
    db = get_db()

    # Basic counts
    cur = await db.execute("SELECT COUNT(*) as c FROM articles")
    total = (await cur.fetchone())["c"]

    cur = await db.execute("SELECT COUNT(*) as c FROM articles WHERE processed = 1")
    processed = (await cur.fetchone())["c"]

    cur = await db.execute("SELECT COUNT(*) as c FROM articles WHERE sentiment = 'positive'")
    positive = (await cur.fetchone())["c"]

    cur = await db.execute("SELECT COUNT(*) as c FROM articles WHERE sentiment = 'negative'")
    negative = (await cur.fetchone())["c"]

    cur = await db.execute("SELECT COUNT(*) as c FROM articles WHERE sentiment = 'neutral'")
    neutral = (await cur.fetchone())["c"]

    cur = await db.execute(
        "SELECT DISTINCT source_name FROM articles WHERE source_name IS NOT NULL LIMIT 20"
    )
    sources = [r["source_name"] for r in await cur.fetchall()]

    # Top zero-shot topics (using json_each)
    cur = await db.execute("""
        SELECT
            json_extract(je.value, '$.label') as label,
            COUNT(*) as count,
            AVG(json_extract(je.value, '$.score')) as avg_score
        FROM articles, json_each(articles.topics) AS je
        WHERE articles.processed = 1
        GROUP BY label
        ORDER BY count DESC
        LIMIT 8
    """)
    top_topics = [
        {"label": r["label"], "count": r["count"], "avg_score": round(r["avg_score"], 3)}
        for r in await cur.fetchall()
    ]

    # Top NER entities (ORG)
    cur = await db.execute("""
        SELECT
            je.value as name,
            COUNT(*) as count
        FROM articles, json_each(json_extract(articles.entities, '$.ORG')) AS je
        WHERE articles.processed = 1
          AND json_extract(articles.entities, '$.ORG') IS NOT NULL
        GROUP BY name
        ORDER BY count DESC
        LIMIT 10
    """)
    top_entities = [{"name": r["name"], "count": r["count"]} for r in await cur.fetchall()]

    # Cluster summary
    cur = await db.execute("""
        SELECT cluster_id, cluster_label, COUNT(*) as count
        FROM articles
        WHERE cluster_label IS NOT NULL
        GROUP BY cluster_id, cluster_label
        ORDER BY count DESC
    """)
    clusters = [
        {"id": r["cluster_id"], "label": r["cluster_label"], "count": r["count"]}
        for r in await cur.fetchall()
    ]

    return {
        "total_articles": total,
        "processed_articles": processed,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "sources": sources,
        "top_topics": top_topics,
        "top_entities": top_entities,
        "clusters": clusters,
    }


@router.get("/{article_id}")
async def get_article(article_id: str):
    db = get_db()
    cursor = await db.execute("SELECT * FROM articles WHERE article_id = ?", (article_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Article not found")
    return _serialize(row)


@router.post("/pipeline/run")
async def trigger_pipeline():
    fetched   = await fetch_and_store()
    processed = await process_unprocessed(batch_size=50)
    await run_topic_clustering(n_clusters=8)
    return {"fetched": fetched, "processed": processed, "status": "ok"}


@router.post("/pipeline/cluster")
async def trigger_clustering(n_clusters: int = 8):
    names = await run_topic_clustering(n_clusters=n_clusters)
    return {"clusters": names}
