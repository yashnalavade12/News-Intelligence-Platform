# ⬡ NewsIntel — AI-Powered News Intelligence Platform

> End-to-end ML pipeline: NER · Zero-shot classification · Semantic embeddings · KMeans topic clustering · Sentiment analysis

---

## ML Pipeline Architecture

```
Raw Article Text
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 1 — Abstractive Summarization                        │
│  Model: sshleifer/distilbart-cnn-12-6                       │
│  Output: 1-2 sentence summary                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 2 — Sentiment Analysis                               │
│  Model: distilbert-base-uncased-finetuned-sst-2-english     │
│  Output: positive/negative/neutral + confidence score       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 3 — Named Entity Recognition (NER)                   │
│  Model: spaCy en_core_web_sm                                │
│  Output: PERSON, ORG, GPE, EVENT, PRODUCT entities          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 4 — Zero-Shot Topic Classification                   │
│  Model: facebook/bart-large-mnli                            │
│  Labels: AI, technology, finance, health, politics, ...     │
│  Output: top-3 topics + confidence scores (no training data)│
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage 5 — Semantic Embedding                               │
│  Model: all-MiniLM-L6-v2 (sentence-transformers)            │
│  Output: 384-dimensional dense vector (stored in MongoDB)   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼ (batch job, runs periodically)
┌─────────────────────────────────────────────────────────────┐
│  Stage 6 — Topic Clustering                                 │
│  Algorithm: KMeans on all stored embeddings                 │
│  Labels: TF-IDF top-words per cluster centroid              │
│  Output: cluster_id + cluster_label written back to DB      │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start (under 5 minutes)

### Prerequisites
- Python 3.10+, Node.js 18+
- MongoDB Atlas free tier
- [NewsData.io](https://newsdata.io) API key (free)

### 1. Clone
```bash
git clone https://github.com/YOUR_USERNAME/news-intelligence.git
cd news-intelligence
```

### 2. Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env   # fill in your keys
uvicorn main:app --reload --port 8000
```
> First run downloads HuggingFace models (~1.2GB total). Cached after that.

### 3. Frontend
```bash
cd ../frontend
npm install
cp .env.example .env   # REACT_APP_API_URL=http://localhost:8000
npm start
```
Open http://localhost:3000

---

## Features

### ML Pipeline (all models run locally, zero API cost)
| Stage | Model | Task |
|---|---|---|
| Summarization | `sshleifer/distilbart-cnn-12-6` | Abstractive 1-2 sentence summary |
| Sentiment | `distilbert-base-uncased-finetuned-sst-2-english` | +/- confidence scoring |
| NER | `spaCy en_core_web_sm` | Person, Org, Location, Event extraction |
| Zero-shot | `facebook/bart-large-mnli` | Topic classification without labelled data |
| Embeddings | `all-MiniLM-L6-v2` | 384-d semantic vectors for clustering |
| Clustering | `KMeans (sklearn)` + TF-IDF labels | Unsupervised topic grouping |

### Dashboard
- **ML Analytics Panel** — sentiment pie, zero-shot topic bar chart, NER org frequency, semantic cluster explorer
- **Interactive filtering** — click any chart element to filter the article grid
- **Article cards** — show topic confidence badges, NER entity chips, cluster label, insights
- **Search + filter** — full-text + sentiment + topic + cluster filters simultaneously

### API
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/articles` | List articles (search, sentiment, topic, cluster filters) |
| GET | `/api/articles/stats` | ML analytics: sentiment dist, top topics, NER entities, clusters |
| POST | `/api/articles/pipeline/run` | Trigger full ML pipeline |
| POST | `/api/articles/pipeline/cluster` | Re-run KMeans clustering |
| GET  | `/health` | Health check |

---

## Tech Stack

| Layer | Tech | Why |
|---|---|---|
| Backend | FastAPI + async | Non-blocking; critical for concurrent ML inference |
| Database | MongoDB + Motor | Flexible schema; stores variable-length entity dicts and embedding vectors |
| Summarization | distilbart-cnn | Fast distilled BART; good quality/speed tradeoff |
| Sentiment | distilbert-sst2 | Industry standard; calibrated confidence scores |
| NER | spaCy | Fastest production NER; structured entity types |
| Zero-shot | bart-large-mnli | No labelled data needed; highly generalizable |
| Embeddings | all-MiniLM-L6-v2 | 384d; best performance/size ratio in MTEB benchmarks |
| Clustering | sklearn KMeans | Simple, interpretable; TF-IDF auto-labelling |
| Scheduler | APScheduler | Async-native cron jobs |
| Frontend | React + Recharts | Component model; Recharts for lightweight charting |

---

## Deployment

**Backend → Render**
- Root: `backend/`, Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Note: use a plan with ≥512MB RAM for HuggingFace models

**Frontend → Vercel**
- Root: `frontend/`, set `REACT_APP_API_URL` to your Render URL

---

## Future Improvements
- [ ] Vector similarity search (swap KMeans for FAISS / MongoDB Atlas Vector Search)
- [ ] Fine-tune sentiment model on news-domain data
- [ ] Multi-language NER (spaCy multilingual model)
- [ ] LDA topic modelling as alternative to KMeans
- [ ] Trend detection — alert when a topic cluster grows rapidly
- [ ] Named entity co-occurrence graph (D3.js)
