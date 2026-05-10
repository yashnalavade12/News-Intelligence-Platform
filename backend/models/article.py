from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ArticleBase(BaseModel):
    article_id: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    source_name: Optional[str] = None
    published_at: Optional[datetime] = None
    category: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    language: Optional[str] = "en"


class TopicLabel(BaseModel):
    label: str
    score: float


class ArticleProcessed(ArticleBase):
    summary: Optional[str] = None
    sentiment: Optional[str] = None           # positive | negative | neutral
    sentiment_score: Optional[float] = None   # 0.0 – 1.0
    entities: Optional[Dict[str, List[str]]] = {}   # { ORG: [...], PERSON: [...], GPE: [...] }
    topics: Optional[List[TopicLabel]] = []   # zero-shot labels + scores
    insights: Optional[List[str]] = []
    cluster_id: Optional[int] = None
    cluster_label: Optional[str] = None
    processed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ArticleOut(ArticleProcessed):
    id: Optional[str] = None

    class Config:
        from_attributes = True


class PaginatedArticles(BaseModel):
    total: int
    page: int
    page_size: int
    articles: List[ArticleOut]


class StatsOut(BaseModel):
    total_articles: int
    processed_articles: int
    positive: int
    negative: int
    neutral: int
    sources: List[str]
    top_topics: List[Dict[str, Any]]
    top_entities: List[Dict[str, Any]]
    clusters: List[Dict[str, Any]]
