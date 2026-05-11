import json
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from bson.objectid import ObjectId
from core.database import get_db
from services.fetcher import fetch_and_store
from services.ai_processor import process_unprocessed, run_topic_clustering

router = APIRouter(prefix="/api/articles", tags=["articles"])


def _serialize(doc) -> dict:
    """Convert MongoDB document to dict for API response."""
    if not doc:
        return None
    doc["id"] = str(doc.pop("_id", ""))
    doc.pop("embedding", None)  # never send 384-d vectors to frontend
    return doc


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
    articles_collection = db["articles"]
    
    # Build filter
    filter_dict = {"processed": True}
    
    if sentiment:
        filter_dict["sentiment"] = sentiment
    
    if topic:
        filter_dict["topics.label"] = topic
    
    if cluster_id is not None:
        filter_dict["cluster_id"] = cluster_id
    
    if search:
        filter_dict["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"summary": {"$regex": search, "$options": "i"}},
            {"source": {"$regex": search, "$options": "i"}},
        ]
    
    # Count
    total = await articles_collection.count_documents(filter_dict)
    
    # Fetch page
    offset = (page - 1) * page_size
    cursor = articles_collection.find(filter_dict).sort("published_at", -1).skip(offset).limit(page_size)
    articles = await cursor.to_list(page_size)
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "articles": [_serialize(doc) for doc in articles],
    }


@router.get("/stats")
async def get_stats():
    db = get_db()
    articles_collection = db["articles"]
    
    # Basic counts
    total = await articles_collection.count_documents({})
    processed = await articles_collection.count_documents({"processed": True})
    positive = await articles_collection.count_documents({"sentiment": "positive"})
    negative = await articles_collection.count_documents({"sentiment": "negative"})
    neutral = await articles_collection.count_documents({"sentiment": "neutral"})
    
    # Get unique sources
    sources = await articles_collection.distinct("source", {"source": {"$exists": True}})
    sources = sources[:20]
    
    # Top topics
    top_topics = await articles_collection.aggregate([
        {"$match": {"processed": True, "topics": {"$exists": True}}},
        {"$unwind": "$topics"},
        {"$group": {
            "_id": "$topics.label",
            "count": {"$sum": 1},
            "avg_score": {"$avg": "$topics.score"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 8}
    ]).to_list(8)
    
    top_topics_list = [
        {"label": t["_id"], "count": t["count"], "avg_score": round(t["avg_score"], 3)}
        for t in top_topics
    ]
    
    # Top entities (ORG)
    top_entities = await articles_collection.aggregate([
        {"$match": {"processed": True, "entities.ORG": {"$exists": True}}},
        {"$unwind": "$entities.ORG"},
        {"$group": {
            "_id": "$entities.ORG",
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]).to_list(10)
    
    top_entities_list = [
        {"name": e["_id"], "count": e["count"]}
        for e in top_entities
    ]
    
    # Cluster summary
    clusters = await articles_collection.aggregate([
        {"$match": {"cluster_label": {"$exists": True, "$ne": None}}},
        {"$group": {
            "_id": {"cluster_id": "$cluster_id", "cluster_label": "$cluster_label"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}
    ]).to_list(None)
    
    clusters_list = [
        {"id": c["_id"]["cluster_id"], "label": c["_id"]["cluster_label"], "count": c["count"]}
        for c in clusters
    ]
    
    return {
        "total_articles": total,
        "processed_articles": processed,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "sources": sources,
        "top_topics": top_topics_list,
        "top_entities": top_entities_list,
        "clusters": clusters_list,
    }


@router.get("/{article_id}")
async def get_article(article_id: str):
    db = get_db()
    articles_collection = db["articles"]
    
    try:
        obj_id = ObjectId(article_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid article ID")
    
    doc = await articles_collection.find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return _serialize(doc)


@router.post("/pipeline/run")
async def trigger_pipeline():
    fetched = await fetch_and_store()
    processed = await process_unprocessed(batch_size=50)
    await run_topic_clustering(n_clusters=8)
    return {"fetched": fetched, "processed": processed, "status": "ok"}


@router.post("/pipeline/cluster")
async def trigger_clustering(n_clusters: int = 8):
    names = await run_topic_clustering(n_clusters=n_clusters)
    return {"clusters": names}
