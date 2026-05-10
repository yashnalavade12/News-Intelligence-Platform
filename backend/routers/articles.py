from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from collections import Counter
from core.database import get_db
from models.article import PaginatedArticles, ArticleOut, StatsOut
from services.fetcher import fetch_and_store
from services.ai_processor import process_unprocessed, run_topic_clustering

router = APIRouter(prefix="/api/articles", tags=["articles"])


def _serialize(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id", ""))
    doc.pop("embedding", None)   # never send 384-d vectors to frontend
    return doc


@router.get("", response_model=PaginatedArticles)
async def get_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    sentiment: Optional[str] = Query(None, pattern="^(positive|negative|neutral)$"),
    topic: Optional[str] = Query(None),
    cluster_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
):
    db = get_db()
    query: dict = {"processed": True}

    if sentiment:
        query["sentiment"] = sentiment
    if topic:
        query["topics.label"] = topic
    if cluster_id is not None:
        query["cluster_id"] = cluster_id
    if search:
        query["$or"] = [
            {"title":       {"$regex": search, "$options": "i"}},
            {"summary":     {"$regex": search, "$options": "i"}},
            {"source_name": {"$regex": search, "$options": "i"}},
        ]

    total  = await db.articles.count_documents(query)
    skip   = (page - 1) * page_size
    cursor = db.articles.find(query).sort("published_at", -1).skip(skip).limit(page_size)
    docs   = await cursor.to_list(length=page_size)

    return PaginatedArticles(
        total=total, page=page, page_size=page_size,
        articles=[_serialize(d) for d in docs],
    )


@router.get("/stats", response_model=StatsOut)
async def get_stats():
    db = get_db()
    total     = await db.articles.count_documents({})
    processed = await db.articles.count_documents({"processed": True})
    positive  = await db.articles.count_documents({"sentiment": "positive"})
    negative  = await db.articles.count_documents({"sentiment": "negative"})
    neutral   = await db.articles.count_documents({"sentiment": "neutral"})
    sources   = [s for s in await db.articles.distinct("source_name") if s][:20]

    # Aggregate top zero-shot topics
    pipeline_topics = [
        {"$match":   {"processed": True}},
        {"$unwind":  "$topics"},
        {"$group":   {"_id": "$topics.label", "count": {"$sum": 1}, "avg_score": {"$avg": "$topics.score"}}},
        {"$sort":    {"count": -1}},
        {"$limit":   8},
    ]
    top_topics = [
        {"label": r["_id"], "count": r["count"], "avg_score": round(r["avg_score"], 3)}
        async for r in db.articles.aggregate(pipeline_topics)
    ]

    # Aggregate top NER entities (ORG)
    pipeline_ner = [
        {"$match":   {"processed": True, "entities.ORG": {"$exists": True}}},
        {"$unwind":  "$entities.ORG"},
        {"$group":   {"_id": "$entities.ORG", "count": {"$sum": 1}}},
        {"$sort":    {"count": -1}},
        {"$limit":   10},
    ]
    top_entities = [
        {"name": r["_id"], "count": r["count"]}
        async for r in db.articles.aggregate(pipeline_ner)
    ]

    # Cluster summary
    pipeline_clusters = [
        {"$match":  {"cluster_label": {"$exists": True}}},
        {"$group":  {"_id": {"id": "$cluster_id", "label": "$cluster_label"}, "count": {"$sum": 1}}},
        {"$sort":   {"count": -1}},
    ]
    clusters = [
        {"id": r["_id"]["id"], "label": r["_id"]["label"], "count": r["count"]}
        async for r in db.articles.aggregate(pipeline_clusters)
    ]

    return StatsOut(
        total_articles=total, processed_articles=processed,
        positive=positive, negative=negative, neutral=neutral,
        sources=sources, top_topics=top_topics,
        top_entities=top_entities, clusters=clusters,
    )


@router.get("/{article_id}", response_model=ArticleOut)
async def get_article(article_id: str):
    db  = get_db()
    doc = await db.articles.find_one({"article_id": article_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Article not found")
    return _serialize(doc)


@router.post("/pipeline/run")
async def trigger_pipeline():
    fetched   = await fetch_and_store(max_pages=5)
    processed = await process_unprocessed(batch_size=50)
    await run_topic_clustering(n_clusters=8)
    return {"fetched": fetched, "processed": processed, "status": "ok"}


@router.post("/pipeline/cluster")
async def trigger_clustering(n_clusters: int = 8):
    names = await run_topic_clustering(n_clusters=n_clusters)
    return {"clusters": names}
