import React from "react";

const SENTIMENTS = ["all","positive","negative","neutral"];
const SENT_COLORS = { all: "var(--text-dim)", positive: "var(--green)", negative: "var(--red)", neutral: "var(--amber)" };

const s = {
  bar: { display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 20 },
  searchWrap: { flex: 1, minWidth: 200, position: "relative" },
  searchIcon: { position: "absolute", left: 11, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)", fontSize: 14, pointerEvents: "none" },
  input: { width: "100%", background: "var(--bg-2)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text)", fontFamily: "var(--font-body)", fontSize: 13, padding: "8px 10px 8px 32px", outline: "none" },
  group: { display: "flex", gap: 5 },
  sentBtn: (active, color) => ({ padding: "6px 12px", borderRadius: 20, fontSize: 12, fontWeight: 500, background: active ? "rgba(255,255,255,0.06)" : "transparent", border: `1px solid ${active ? color : "var(--border)"}`, color: active ? color : "var(--text-muted)", transition: "all 0.15s" }),
  clearBtn: { padding: "6px 12px", borderRadius: 8, fontSize: 12, fontWeight: 500, background: "var(--bg-3)", border: "1px solid var(--border)", color: "var(--text-muted)" },
  refreshBtn: { padding: "7px 14px", borderRadius: 8, fontSize: 12, fontWeight: 500, background: "var(--amber-glow)", border: "1px solid var(--amber-dim)", color: "var(--amber)" },
  activeFilter: { fontSize: 11, color: "var(--amber)", background: "var(--amber-glow)", border: "1px solid var(--amber-dim)", borderRadius: 20, padding: "3px 10px", display: "flex", alignItems: "center", gap: 5 },
};

export default function FilterBar({ search, setSearch, sentiment, setSentiment, activeTopic, activeCluster, onClear, onRefresh, loading }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <div style={s.bar}>
        <div style={s.searchWrap}>
          <span style={s.searchIcon}>⌕</span>
          <input style={s.input} placeholder="Search articles, sources, topics…" value={search} onChange={e => { setSearch(e.target.value); }} />
        </div>
        <div style={s.group}>
          {SENTIMENTS.map(snt => (
            <button key={snt} style={s.sentBtn(sentiment === snt, SENT_COLORS[snt])} onClick={() => setSentiment(snt)}>
              {snt.charAt(0).toUpperCase() + snt.slice(1)}
            </button>
          ))}
        </div>
        {(activeTopic || activeCluster !== null) && (
          <button style={s.clearBtn} onClick={onClear}>✕ Clear filters</button>
        )}
        <button style={s.refreshBtn} onClick={onRefresh} disabled={loading}>
          {loading ? "…" : "↻ Refresh"}
        </button>
      </div>

      {/* Active ML filters */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {activeTopic && (
          <span style={s.activeFilter}>
            🏷 Topic: <strong>{activeTopic}</strong>
            <button style={{ background: "none", border: "none", color: "var(--amber)", cursor: "pointer", padding: 0, fontSize: 12 }} onClick={() => onClear("topic")}>✕</button>
          </span>
        )}
        {activeCluster !== null && (
          <span style={s.activeFilter}>
            🗂 Cluster #{activeCluster}
            <button style={{ background: "none", border: "none", color: "var(--amber)", cursor: "pointer", padding: 0, fontSize: 12 }} onClick={() => onClear("cluster")}>✕</button>
          </span>
        )}
      </div>
    </div>
  );
}
