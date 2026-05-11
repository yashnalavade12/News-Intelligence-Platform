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
  header: { borderBottom: "1px solid var(--border)", padding: "0 40px", background: "var(--bg)", position: "sticky", top: 0, zIndex: 50 },
  headerInner: { maxWidth: 1400, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", height: 64 },
  logo: { fontSize: 20, fontWeight: 700, display: "flex", alignItems: "center", gap: 10, color: "var(--primary)" },
  logoIcon: { width: 32, height: 32, borderRadius: 6, background: "var(--primary-light)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18, fontWeight: 700 },
  headerRight: { display: "flex", alignItems: "center", gap: 12 },
  badge: { fontSize: 11, fontWeight: 600, background: "var(--green-light)", color: "var(--green)", padding: "4px 10px", borderRadius: 20 },
  main: { flex: 1, maxWidth: 1400, margin: "0 auto", width: "100%", padding: "32px 40px" },
  heroRow: { marginBottom: 28 },
  title: { fontSize: 28, fontWeight: 700, color: "var(--text)", marginBottom: 6, letterSpacing: "-0.5px" },
  sub: { fontSize: 14, color: "var(--text-muted)" },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(320px,1fr))", gap: 20, marginBottom: 24 },
  empty: { gridColumn: "1/-1", textAlign: "center", padding: "80px 40px", color: "var(--text-muted)", fontSize: 15 },
  skeleton: (i) => ({ background: "var(--bg-2)", border: "1px solid var(--border)", borderRadius: "var(--radius)", height: 360, backgroundImage: "linear-gradient(90deg,var(--bg-2) 0%,var(--bg-3) 50%,var(--bg-2) 100%)", backgroundSize: "800px 100%", animation: `shimmer 1.4s ${i*0.05}s infinite linear` }),
  footer: { borderTop: "1px solid var(--border)", padding: "20px 40px", textAlign: "center", fontSize: 12, color: "var(--text-muted)" },
  statsContainer: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 28 },
  statCard: { background: "var(--bg-2)", border: "1px solid var(--border)", borderRadius: "var(--radius)", padding: 16 },
  statLabel: { fontSize: 12, color: "var(--text-muted)", fontWeight: 500, marginBottom: 8 },
  statValue: { fontSize: 24, fontWeight: 700, color: "var(--text)" },
};

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
            <div style={s.logoIcon}>📰</div>
            NewsDaily
          </div>
          <div style={s.headerRight}>
            <span style={s.badge}>● Live</span>
          </div>
        </div>
      </header>

      <main style={s.main}>
        <div style={s.heroRow}>
          <h1 style={s.title}>News Feed</h1>
          <p style={s.sub}>Stay informed with the latest articles and insights</p>
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
          <p style={{ fontSize: 13, color: "var(--text-muted)", marginBottom: 20, fontWeight: 500 }}>
            {total.toLocaleString()} articles
            {activeTopic   && <> • <strong>{activeTopic}</strong></>}
            {activeCluster !== null && <> • Cluster #{activeCluster}</>}
            {search        && <> • Matching "<strong>{search}</strong>"</>}
          </p>
        )}

        <div style={s.grid}>
          {loading && Array.from({ length: PAGE_SIZE }).map((_, i) => <div key={i} style={s.skeleton(i)} />)}
          {!loading && error && (
            <div style={{ gridColumn: "1/-1", textAlign: "center", padding: "60px 0", color: "var(--red)" }}>
              <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>⚠ Unable to load articles</div>
              <div style={{ fontSize: 13 }}>Make sure the backend is running on localhost:8000</div>
            </div>
          )}
          {!loading && !error && articles.length === 0 && (
            <div style={s.empty}>
              <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>No articles found</div>
              <div style={{ fontSize: 13 }}>Try adjusting your search filters</div>
            </div>
          )}
          {!loading && !error && articles.map((a) => (
            <ArticleCard key={a.id || a.article_id} article={a} />
          ))}
        </div>

        <Pagination page={page} total={total} pageSize={PAGE_SIZE} onChange={setPage} />
      </main>

      <footer style={s.footer}>
        NewsDaily • Powered by FastAPI & React
      </footer>
    </div>
  );
}
