import React, { useState } from "react";

const BADGE = {
  positive: { bg: "var(--green-dim)", color: "var(--green)", label: "↑ Positive" },
  negative: { bg: "var(--red-dim)",   color: "var(--red)",   label: "↓ Negative" },
  neutral:  { bg: "var(--blue-dim)",  color: "var(--blue)",  label: "● Neutral"  },
};

function timeAgo(d) {
  if (!d) return "";
  const h = Math.floor((Date.now() - new Date(d)) / 3_600_000);
  return h < 1 ? "Just now" : h < 24 ? `${h}h ago` : `${Math.floor(h/24)}d ago`;
}

const s = {
  card: (hov) => ({
    background: "var(--bg-2)", border: `1px solid ${hov ? "var(--border-2)" : "var(--border)"}`,
    borderRadius: "var(--radius)", display: "flex", flexDirection: "column",
    transition: "all 0.2s", transform: hov ? "translateY(-2px)" : "none",
    boxShadow: hov ? "0 8px 32px rgba(0,0,0,0.4)" : "none",
    animation: "fadeUp 0.4s ease both", overflow: "hidden",
  }),
  img:  { width: "100%", height: 148, objectFit: "cover", background: "var(--bg-3)", display: "block" },
  imgFallback: { width: "100%", height: 148, background: "linear-gradient(135deg,var(--bg-3),#0f1117)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--border-2)", fontSize: 28 },
  body: { padding: 16, flex: 1, display: "flex", flexDirection: "column", gap: 9 },
  row:  { display: "flex", alignItems: "center", justifyContent: "space-between", gap: 6 },
  src:  { fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.06em" },
  badge: (b) => ({ display: "inline-block", padding: "2px 8px", borderRadius: 20, fontSize: 11, fontWeight: 600, background: b.bg, color: b.color }),
  title: { fontFamily: "var(--font-display)", fontSize: 15, fontWeight: 700, lineHeight: 1.35 },
  summary: { fontSize: 12.5, color: "var(--text-dim)", lineHeight: 1.6, flex: 1 },
  topicRow: { display: "flex", flexWrap: "wrap", gap: 5 },
  topicChip: (score) => ({
    fontSize: 10, padding: "2px 7px", borderRadius: 10, fontWeight: 500,
    background: `rgba(245,158,11,${0.08 + score * 0.15})`,
    border: "1px solid var(--amber-dim)", color: "var(--amber)",
  }),
  entitySection: { background: "var(--bg-3)", borderRadius: 6, padding: "8px 10px", fontSize: 11 },
  entityLabel: { color: "var(--text-muted)", fontFamily: "var(--font-mono)", marginBottom: 4, fontSize: 10, textTransform: "uppercase", letterSpacing: "0.05em" },
  entityChip: { display: "inline-block", background: "var(--blue-dim)", color: "var(--blue)", padding: "1px 6px", borderRadius: 8, marginRight: 4, marginBottom: 3 },
  insightsToggle: { fontSize: 11, color: "var(--amber)", fontWeight: 500, background: "var(--amber-glow)", border: "1px solid var(--amber-dim)", borderRadius: 6, padding: "3px 9px", alignSelf: "flex-start" },
  insightsList: { background: "var(--bg-3)", borderRadius: 6, padding: "8px 12px", borderLeft: "3px solid var(--amber-dim)" },
  insightItem: { fontSize: 11.5, color: "var(--text-dim)", lineHeight: 1.55, marginBottom: 4 },
  readMore: { fontSize: 11.5, color: "var(--blue)", marginTop: 4, alignSelf: "flex-end" },
};

export default function ArticleCard({ article }) {
  const [hov, setHov]         = useState(false);
  const [showIns, setShowIns] = useState(false);
  const badge = BADGE[article.sentiment] || BADGE.neutral;

  const hasEntities = article.entities && Object.keys(article.entities).length > 0;

  return (
    <div style={s.card(hov)} onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}>
      {article.image_url
        ? <img src={article.image_url} alt="" style={s.img} onError={e => { e.target.style.display="none"; }} />
        : <div style={s.imgFallback}>📰</div>
      }

      <div style={s.body}>
        <div style={s.row}>
          <span style={s.src}>{article.source_name || "Unknown"}</span>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{timeAgo(article.published_at)}</span>
        </div>

        <div style={s.row}>
          <span style={s.badge(badge)}>{badge.label}</span>
          {article.sentiment_score != null && (
            <span style={{ fontSize: 10.5, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
              {(article.sentiment_score * 100).toFixed(0)}% conf
            </span>
          )}
        </div>

        <h3 style={s.title}>{article.title}</h3>

        {/* Zero-shot topic chips */}
        {article.topics?.length > 0 && (
          <div style={s.topicRow}>
            {article.topics.map((t, i) => (
              <span key={i} style={s.topicChip(t.score)}>{t.label} {(t.score*100).toFixed(0)}%</span>
            ))}
          </div>
        )}

        {article.summary && <p style={s.summary}>{article.summary}</p>}

        {/* NER entities */}
        {hasEntities && (
          <div style={s.entitySection}>
            <div style={s.entityLabel}>Named Entities</div>
            {Object.entries(article.entities).slice(0,3).map(([type, vals]) => (
              <div key={type} style={{ marginBottom: 3 }}>
                <span style={{ color: "var(--text-muted)", fontSize: 10 }}>{type}: </span>
                {vals.slice(0,3).map((v, i) => <span key={i} style={s.entityChip}>{v}</span>)}
              </div>
            ))}
          </div>
        )}

        {/* Cluster badge */}
        {article.cluster_label && (
          <span style={{ fontSize: 10.5, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
            🗂 Cluster: {article.cluster_label}
          </span>
        )}

        {article.insights?.length > 0 && (
          <button style={s.insightsToggle} onClick={() => setShowIns(p => !p)}>
            {showIns ? "▲ Hide" : "▼ Key Insights"} ({article.insights.length})
          </button>
        )}

        {showIns && (
          <div style={s.insightsList}>
            {article.insights.map((ins, i) => <p key={i} style={s.insightItem}>• {ins}</p>)}
          </div>
        )}

        {article.url && (
          <a href={article.url} target="_blank" rel="noopener noreferrer" style={s.readMore}>
            Read full article →
          </a>
        )}
      </div>
    </div>
  );
}
