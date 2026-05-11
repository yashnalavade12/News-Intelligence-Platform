import React from "react";

const SENTIMENTS = ["all","positive","negative","neutral"];
const SENT_COLORS = { all: "var(--text-muted)", positive: "var(--green)", negative: "var(--red)", neutral: "#f59e0b" };

const s = {
  bar: { display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginBottom: 24 },
  searchWrap: { flex: 1, minWidth: 240, position: "relative" },
  searchIcon: { position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)", fontSize: 16, pointerEvents: "none" },
  input: { width: "100%", background: "var(--bg-2)", border: "1px solid var(--border)", borderRadius: 6, color: "var(--text)", fontFamily: "var(--font-body)", fontSize: 14, padding: "10px 12px 10px 40px", outline: "none", transition: "all 0.2s" },
  group: { display: "flex", gap: 6 },
  sentBtn: (active, color) => ({ padding: "8px 14px", borderRadius: 6, fontSize: 13, fontWeight: 500, background: active ? color + "15" : "transparent", border: `1px solid ${active ? color : "var(--border)"}`, color: active ? color : "var(--text-muted)", transition: "all 0.15s", cursor: "pointer" }),
  clearBtn: { padding: "8px 14px", borderRadius: 6, fontSize: 13, fontWeight: 500, background: "var(--bg-2)", border: "1px solid var(--border)", color: "var(--text-muted)", cursor: "pointer", transition: "all 0.15s" },
  refreshBtn: { padding: "8px 16px", borderRadius: 6, fontSize: 13, fontWeight: 600, background: "var(--primary)", color: "white", border: "none", cursor: "pointer", transition: "all 0.15s" },
  activeFilter: { fontSize: 12, color: "var(--primary)", background: "var(--primary-light)", border: "1px solid var(--primary-dim)", borderRadius: 6, padding: "6px 12px", display: "flex", alignItems: "center", gap: 6 },
};

export default function FilterBar({ search, setSearch, sentiment, setSentiment, activeTopic, activeCluster, onClear, onRefresh, loading }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <div style={s.bar}>
        <div style={s.searchWrap}>
          <span style={s.searchIcon}>🔍</span>
          <input style={s.input} placeholder="Search articles..." value={search} onChange={e => { setSearch(e.target.value); }} />
        </div>
        
        <div style={s.group}>
          {SENTIMENTS.map(snt => (
            <button key={snt} style={s.sentBtn(sentiment === snt, SENT_COLORS[snt])} onClick={() => setSentiment(snt)}>
              {snt === 'all' ? 'All' : snt.charAt(0).toUpperCase() + snt.slice(1)}
            </button>
          ))}
        </div>

        <button style={s.refreshBtn} onClick={onRefresh} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </button>

        {(activeTopic || activeCluster !== null) && (
          <button style={s.clearBtn} onClick={onClear}>Clear Filters</button>
        )}
      </div>

      {/* Active filters display */}
      {(activeTopic || activeCluster !== null) && (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {activeTopic && (
            <span style={s.activeFilter}>
              Topic: <strong>{activeTopic}</strong>
              <button style={{ background: "none", border: "none", color: "var(--primary)", cursor: "pointer", padding: 0, fontSize: 14, lineHeight: 1 }} onClick={() => onClear("topic")}>×</button>
            </span>
          )}
          {activeCluster !== null && (
            <span style={s.activeFilter}>
              Cluster #{activeCluster}
              <button style={{ background: "none", border: "none", color: "var(--primary)", cursor: "pointer", padding: 0, fontSize: 14, lineHeight: 1 }} onClick={() => onClear("cluster")}>×</button>
            </span>
          )}
        </div>
      )}
    </div>
  );
}
