import React, { useState, useCallback } from "react";
import { useArticles, useStats } from "../hooks/useArticles";
import { triggerPipeline } from "../utils/api";
import MLInsightsPanel from "../components/MLInsightsPanel";
import FilterBar from "../components/FilterBar";
import ArticleCard from "../components/ArticleCard";
import Pagination from "../components/Pagination";

const PAGE_SIZE = 12;

const s = {
  root: { minHeight: "100vh", background: "var(--bg)", display: "flex", flexDirection: "column" },
  header: { borderBottom: "1px solid var(--border)", padding: "0 40px", background: "rgba(11,12,14,0.92)", position: "sticky", top: 0, zIndex: 50, backdropFilter: "blur(14px)" },
  headerInner: { maxWidth: 1300, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", height: 58 },
  logo: { fontFamily: "var(--font-display)", fontSize: 19, fontWeight: 900, display: "flex", alignItems: "center", gap: 8 },
  logoAccent: { color: "var(--amber)" },
  badge: { fontSize: 10, fontFamily: "var(--font-mono)", background: "var(--amber-glow)", border: "1px solid var(--amber-dim)", color: "var(--amber)", padding: "2px 8px", borderRadius: 20, letterSpacing: "0.06em" },
  live: { display: "flex", alignItems: "center", gap: 6 },
  dot: { width: 7, height: 7, borderRadius: "50%", background: "var(--green)" },
  liveLabel: { fontSize: 10.5, color: "var(--green)", fontFamily: "var(--font-mono)", letterSpacing: "0.06em" },
  main: { flex: 1, maxWidth: 1300, margin: "0 auto", width: "100%", padding: "32px 40px" },
  heroRow: { display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 16, marginBottom: 24, flexWrap: "wrap" },
  title: { fontFamily: "var(--font-display)", fontSize: 34, fontWeight: 900, lineHeight: 1.1, background: "linear-gradient(90deg,var(--text) 55%,var(--amber) 100%)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" },
  sub: { fontSize: 13, color: "var(--text-muted)", marginTop: 5 },
  modelStack: { display: "flex", gap: 7, flexWrap: "wrap" },
  modelChip: (color) => ({ fontSize: 10.5, fontFamily: "var(--font-mono)", padding: "3px 9px", borderRadius: 20, background: `${color}18`, border: `1px solid ${color}44`, color }),
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(310px,1fr))", gap: 18, marginBottom: 12 },
  empty: { gridColumn: "1/-1", textAlign: "center", padding: "70px 0", color: "var(--text-muted)", fontFamily: "var(--font-display)", fontSize: 18 },
  skeleton: (i) => ({ background: "var(--bg-2)", border: "1px solid var(--border)", borderRadius: "var(--radius)", height: 340, backgroundImage: "linear-gradient(90deg,var(--bg-2) 0%,var(--bg-3) 50%,var(--bg-2) 100%)", backgroundSize: "800px 100%", animation: `shimmer 1.4s ${i*0.05}s infinite linear` }),
  footer: { borderTop: "1px solid var(--border)", padding: "16px 40px", textAlign: "center", fontSize: 11.5, color: "var(--text-muted)" },
};

const MODEL_CHIPS = [
  { label: "distilbart-cnn  summarization", color: "#f59e0b" },
  { label: "distilbert-sst2  sentiment",    color: "#10b981" },
  { label: "bart-large-mnli  zero-shot",    color: "#8b5cf6" },
  { label: "spaCy NER",                      color: "#3b82f6" },
  { label: "MiniLM  embeddings",            color: "#ec4899" },
  { label: "KMeans  clustering",            color: "#f97316" },
];

export default function Dashboard() {
  const [page, setPage]               = useState(1);
  const [search, setSearch]           = useState("");
  const [sentiment, setSentiment]     = useState("all");
  const [activeTopic, setActiveTopic] = useState(null);
  const [activeCluster, setActiveCluster] = useState(null);
  const [pipelining, setPipelining]   = useState(false);

  const filters = {
    page, page_size: PAGE_SIZE,
    ...(search            ? { search }                  : {}),
    ...(sentiment !== "all" ? { sentiment }             : {}),
    ...(activeTopic       ? { topic: activeTopic }      : {}),
    ...(activeCluster !== null ? { cluster_id: activeCluster } : {}),
  };

  const { articles, total, loading, error, refetch } = useArticles(filters);
  const stats = useStats();

  const handleSearch = useCallback((v) => { setSearch(v); setPage(1); }, []);
  const handleSentiment = useCallback((v) => { setSentiment(v); setPage(1); }, []);
  const handleTopicClick = useCallback((label) => { setActiveTopic(label); setActiveCluster(null); setPage(1); }, []);
  const handleClusterClick = useCallback((id) => { setActiveCluster(id); setActiveTopic(null); setPage(1); }, []);
  const handleClear = useCallback((type) => {
    if (!type || type === "topic") setActiveTopic(null);
    if (!type || type === "cluster") setActiveCluster(null);
    setPage(1);
  }, []);

  const handleRefresh = async () => {
    setPipelining(true);
    try { await triggerPipeline(); await refetch(); }
    catch (e) { console.error(e); }
    finally { setPipelining(false); }
  };

  return (
    <div style={s.root}>
      <header style={s.header}>
        <div style={s.headerInner}>
          <div style={s.logo}>
            <span style={s.logoAccent}>⬡</span> News<span style={s.logoAccent}>Intel</span>
            <span style={s.badge}>ML PIPELINE</span>
          </div>
          <div style={s.live}><div style={s.dot} /><span style={s.liveLabel}>LIVE</span></div>
        </div>
      </header>

      <main style={s.main}>
        <div style={s.heroRow}>
          <div>
            <h1 style={s.title}>AI News Intelligence</h1>
            <p style={s.sub}>End-to-end ML pipeline · NER · Zero-shot classification · Semantic clustering</p>
          </div>
          <div style={s.modelStack}>
            {MODEL_CHIPS.map((m, i) => <span key={i} style={s.modelChip(m.color)}>{m.label}</span>)}
          </div>
        </div>

        <MLInsightsPanel
          stats={stats}
          onTopicClick={handleTopicClick}
          onClusterClick={handleClusterClick}
        />

        <FilterBar
          search={search} setSearch={handleSearch}
          sentiment={sentiment} setSentiment={handleSentiment}
          activeTopic={activeTopic} activeCluster={activeCluster}
          onClear={handleClear} onRefresh={handleRefresh}
          loading={loading || pipelining}
        />

        {!loading && !error && (
          <p style={{ fontSize: 12.5, color: "var(--text-muted)", marginBottom: 14 }}>
            {total.toLocaleString()} articles
            {activeTopic   && <> · topic "<strong style={{ color: "var(--amber)" }}>{activeTopic}</strong>"</>}
            {activeCluster !== null && <> · cluster <strong style={{ color: "var(--amber)" }}>#{activeCluster}</strong></>}
            {search        && <> · matching "<strong style={{ color: "var(--text)" }}>{search}</strong>"</>}
          </p>
        )}

        <div style={s.grid}>
          {loading && Array.from({ length: PAGE_SIZE }).map((_, i) => <div key={i} style={s.skeleton(i)} />)}
          {!loading && error && (
            <div style={{ gridColumn: "1/-1", textAlign: "center", padding: "40px 0", color: "var(--red)", fontSize: 13 }}>
              ⚠ {error} — Is the backend running?
            </div>
          )}
          {!loading && !error && articles.length === 0 && (
            <div style={s.empty}>No articles found. Try adjusting your filters.</div>
          )}
          {!loading && !error && articles.map((a) => (
            <ArticleCard key={a.id || a.article_id} article={a} />
          ))}
        </div>

        <Pagination page={page} total={total} pageSize={PAGE_SIZE} onChange={setPage} />
      </main>

      <footer style={s.footer}>
        NewsIntel · FastAPI · MongoDB · HuggingFace Transformers · sentence-transformers · spaCy · scikit-learn · React
      </footer>
    </div>
  );
}
