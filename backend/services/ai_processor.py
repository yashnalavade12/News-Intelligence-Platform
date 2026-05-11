"""
ML Pipeline — the core of the project.

Stages per article:
  1. Summarization       — distilbart-cnn-12-6 (abstractive)
  2. Sentiment Analysis  — distilbert-sst2 (+ confidence score)
  3. NER                 — spaCy en_core_web_sm (persons, orgs, GPE, events)
  4. Zero-Shot Category  — facebook/bart-large-mnli (topic tagging without labelled data)
  5. Semantic Embedding  — all-MiniLM-L6-v2 (384-d vector, stored for clustering)

Batch job:
  6. Topic Clustering    — KMeans on stored embeddings (run periodically, not per-article)
"""

from __future__ import annotations
import re
import json
import numpy as np
from typing import List, Tuple, Dict, Any
from core.database import get_db

# ──────────────────────────────────────────────────────────────────────────────
# Lazy model loading — nothing loads until first call
# ──────────────────────────────────────────────────────────────────────────────
_summarizer        = None
_sentiment_pipe    = None
_zero_shot_pipe    = None
_sentence_model    = None
_nlp               = None   # spaCy

ZERO_SHOT_LABELS = [
    "politics", "technology", "finance", "health", "science",
    "climate", "sports", "AI", "war & conflict", "business",
]


def _get_summarizer():
    global _summarizer
    if _summarizer is None:
        from transformers import pipeline
        print("⏳ Loading summarizer …")
        _summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=-1)
        print("✅ Summarizer ready")
    return _summarizer


def _get_sentiment():
    global _sentiment_pipe
    if _sentiment_pipe is None:
        from transformers import pipeline
        print("⏳ Loading sentiment model …")
        _sentiment_pipe = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1,
        )
        print("✅ Sentiment ready")
    return _sentiment_pipe


def _get_zero_shot():
    global _zero_shot_pipe
    if _zero_shot_pipe is None:
        from transformers import pipeline
        print("⏳ Loading zero-shot classifier …")
        _zero_shot_pipe = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=-1)
        print("✅ Zero-shot classifier ready")
    return _zero_shot_pipe


def _get_sentence_model():
    global _sentence_model
    if _sentence_model is None:
        from sentence_transformers import SentenceTransformer
        print("⏳ Loading sentence embeddings model …")
        _sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✅ Sentence model ready")
    return _sentence_model


def _get_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        print("⏳ Loading spaCy NER …")
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess, sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
            _nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy NER ready")
    return _nlp


# ──────────────────────────────────────────────────────────────────────────────
# Stage 1 — Summarization
# ──────────────────────────────────────────────────────────────────────────────
def _summarize(text: str) -> str:
    if not text or len(text) < 60:
        return (text or "").strip()
    try:
        out = _get_summarizer()(text[:1024], max_length=80, min_length=20, do_sample=False)
        return out[0]["summary_text"].strip()
    except Exception as e:
        print(f"⚠️ Summarization: {e}")
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return " ".join(sentences[:2])


# ──────────────────────────────────────────────────────────────────────────────
# Stage 2 — Sentiment
# ──────────────────────────────────────────────────────────────────────────────
def _sentiment(text: str) -> Tuple[str, float]:
    if not text:
        return "neutral", 0.5
    try:
        r = _get_sentiment()(text[:512])[0]
        label = r["label"].lower()
        score = round(r["score"], 4)
        return label if label in ("positive", "negative") else "neutral", score
    except Exception as e:
        print(f"⚠️ Sentiment: {e}")
        return "neutral", 0.5


# ──────────────────────────────────────────────────────────────────────────────
# Stage 3 — Named Entity Recognition (spaCy)
# ──────────────────────────────────────────────────────────────────────────────
def _extract_entities(text: str) -> Dict[str, List[str]]:
    """Returns dict: { PERSON: [...], ORG: [...], GPE: [...], EVENT: [...] }"""
    if not text:
        return {}
    try:
        doc = _get_nlp()(text[:1000])
        entities: Dict[str, List[str]] = {}
        for ent in doc.ents:
            if ent.label_ in ("PERSON", "ORG", "GPE", "EVENT", "PRODUCT", "NORP"):
                bucket = entities.setdefault(ent.label_, [])
                if ent.text not in bucket:
                    bucket.append(ent.text)
        return {k: v[:5] for k, v in entities.items()}
    except Exception as e:
        print(f"⚠️ NER: {e}")
        return {}


# ──────────────────────────────────────────────────────────────────────────────
# Stage 4 — Zero-Shot Topic Classification
# ──────────────────────────────────────────────────────────────────────────────
def _classify_topics(text: str) -> List[Dict[str, Any]]:
    """Returns top-3 topic labels with confidence scores."""
    if not text:
        return []
    try:
        out = _get_zero_shot()(text[:512], ZERO_SHOT_LABELS, multi_label=True)
        pairs = sorted(zip(out["labels"], out["scores"]), key=lambda x: -x[1])
        return [{"label": l, "score": round(s, 4)} for l, s in pairs[:3] if s > 0.15]
    except Exception as e:
        print(f"⚠️ Zero-shot: {e}")
        return []


# ──────────────────────────────────────────────────────────────────────────────
# Stage 5 — Semantic Embedding
# ──────────────────────────────────────────────────────────────────────────────
def _embed(text: str) -> List[float]:
    if not text:
        return []
    try:
        vec = _get_sentence_model().encode(text[:512], normalize_embeddings=True)
        return vec.tolist()
    except Exception as e:
        print(f"⚠️ Embedding: {e}")
        return []


# ──────────────────────────────────────────────────────────────────────────────
# Insights builder — structured from all ML outputs
# ──────────────────────────────────────────────────────────────────────────────
def _build_insights(
    summary: str,
    entities: Dict[str, List[str]],
    topics: List[Dict],
    keywords: List[str],
) -> List[str]:
    insights = []

    if topics:
        top = topics[0]
        insights.append(f"Primary topic: {top['label']} ({top['score']*100:.0f}% confidence).")

    if entities.get("ORG"):
        insights.append(f"Organizations mentioned: {', '.join(entities['ORG'][:3])}.")
    if entities.get("PERSON"):
        insights.append(f"Key people: {', '.join(entities['PERSON'][:3])}.")
    if entities.get("GPE"):
        insights.append(f"Locations referenced: {', '.join(entities['GPE'][:3])}.")

    kws = [k for k in (keywords or []) if len(k) > 3][:4]
    if kws:
        insights.append(f"Keywords: {', '.join(kws)}.")

    # Stats heuristic on summary
    nums = re.findall(r"\b\d[\d,.]*\s?(?:billion|million|trillion|%|percent)?\b", summary)
    if nums:
        insights.append(f"Notable figures: {', '.join(nums[:3])}.")

    return insights[:5]


# ──────────────────────────────────────────────────────────────────────────────
# Stage 6 — Topic Clustering (batch, runs separately)
# ──────────────────────────────────────────────────────────────────────────────
async def run_topic_clustering(n_clusters: int = 8) -> Dict[str, Any]:
    """
    Load all embeddings from DB → KMeans → write cluster_id + cluster_label back.
    Returns cluster label summary.
    """
    from sklearn.cluster import KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer

    db = get_db()
    cursor = await db.execute(
        "SELECT id, embedding, title, summary FROM articles WHERE embedding != '[]' AND processed = 1"
    )
    rows = await cursor.fetchall()

    if len(rows) < n_clusters:
        print(f"⚠️ Not enough articles for clustering ({len(rows)})")
        return {}

    ids = [r["id"] for r in rows]
    vecs = np.array([json.loads(r["embedding"]) for r in rows], dtype="float32")
    texts = [f"{r['title'] or ''} {r['summary'] or ''}" for r in rows]

    # KMeans clustering
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(vecs)

    # TF-IDF label per cluster
    tfidf = TfidfVectorizer(max_features=500, stop_words="english")
    tfidf.fit(texts)
    vocab = np.array(tfidf.get_feature_names_out())
    cluster_names: Dict[int, str] = {}
    for cid in range(n_clusters):
        indices = np.where(labels == cid)[0]
        cluster_texts = [texts[i] for i in indices]
        if not cluster_texts:
            cluster_names[cid] = f"Topic {cid}"
            continue
        centroid = tfidf.transform(cluster_texts).toarray().mean(axis=0)
        top_words = vocab[centroid.argsort()[-3:][::-1]]
        cluster_names[cid] = " / ".join(top_words)

    # Write back to DB
    for doc_id, cluster_id in zip(ids, labels):
        await db.execute(
            "UPDATE articles SET cluster_id = ?, cluster_label = ? WHERE id = ?",
            (int(cluster_id), cluster_names[int(cluster_id)], doc_id),
        )
    await db.commit()

    print(f"✅ Clustered {len(rows)} articles into {n_clusters} topics")
    return cluster_names


# ──────────────────────────────────────────────────────────────────────────────
# Main batch processor
# ──────────────────────────────────────────────────────────────────────────────
async def process_unprocessed(batch_size: int = 20) -> int:
    db = get_db()
    cursor = await db.execute(
        "SELECT * FROM articles WHERE processed = 0 LIMIT ?", (batch_size,)
    )
    articles = await cursor.fetchall()

    if not articles:
        print("ℹ️  No unprocessed articles.")
        return 0

    count = 0
    for article in articles:
        raw = article["content"] or article["description"] or article["title"] or ""
        title = article["title"] or ""
        try:
            keywords = json.loads(article["keywords"]) if article["keywords"] else []
        except (json.JSONDecodeError, TypeError):
            keywords = []

        # Run all ML stages
        summary   = _summarize(raw)
        sentiment, sent_score = _sentiment(summary or raw)
        entities  = _extract_entities(f"{title}. {summary}")
        topics    = _classify_topics(f"{title}. {summary}")
        embedding = _embed(f"{title}. {summary}")
        insights  = _build_insights(summary, entities, topics, keywords)

        await db.execute(
            """UPDATE articles SET
                summary = ?, sentiment = ?, sentiment_score = ?,
                entities = ?, topics = ?, embedding = ?,
                insights = ?, processed = 1
               WHERE id = ?""",
            (
                summary, sentiment, sent_score,
                json.dumps(entities), json.dumps(topics), json.dumps(embedding),
                json.dumps(insights), article["id"],
            ),
        )
        count += 1

    await db.commit()
    print(f"✅ ML-processed {count} articles")
    return count
