import React from "react";

const s = {
  bar: {
    display: "flex", gap: 16, flexWrap: "wrap",
    padding: "14px 0", borderBottom: "1px solid var(--border)",
    marginBottom: 28,
  },
  tile: {
    background: "var(--bg-2)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    padding: "10px 18px",
    display: "flex", flexDirection: "column", gap: 2,
    minWidth: 110,
  },
  label: { fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.06em" },
  value: { fontSize: 22, fontWeight: 700, fontFamily: "var(--font-display)", lineHeight: 1.1 },
  pos: { color: "var(--green)" },
  neg: { color: "var(--red)" },
  neu: { color: "var(--amber)" },
};

export default function StatsBar({ stats }) {
  if (!stats) return null;
  const pct = (n) => stats.processed_articles ? `${Math.round((n / stats.processed_articles) * 100)}%` : "—";

  return (
    <div style={s.bar}>
      <div style={s.tile}>
        <span style={s.label}>Total</span>
        <span style={s.value}>{stats.total_articles.toLocaleString()}</span>
      </div>
      <div style={s.tile}>
        <span style={s.label}>Processed</span>
        <span style={s.value}>{stats.processed_articles.toLocaleString()}</span>
      </div>
      <div style={s.tile}>
        <span style={s.label}>Positive</span>
        <span style={{ ...s.value, ...s.pos }}>{stats.positive} <span style={{ fontSize: 13, fontFamily: "var(--font-body)", fontWeight: 400 }}>({pct(stats.positive)})</span></span>
      </div>
      <div style={s.tile}>
        <span style={s.label}>Negative</span>
        <span style={{ ...s.value, ...s.neg }}>{stats.negative} <span style={{ fontSize: 13, fontFamily: "var(--font-body)", fontWeight: 400 }}>({pct(stats.negative)})</span></span>
      </div>
      <div style={s.tile}>
        <span style={s.label}>Neutral</span>
        <span style={{ ...s.value, ...s.neu }}>{stats.neutral} <span style={{ fontSize: 13, fontFamily: "var(--font-body)", fontWeight: 400 }}>({pct(stats.neutral)})</span></span>
      </div>
      <div style={{ ...s.tile, flex: 1 }}>
        <span style={s.label}>Sources</span>
        <span style={{ fontSize: 13, color: "var(--text-dim)", marginTop: 4 }}>
          {stats.sources.slice(0, 5).join(" · ")}
          {stats.sources.length > 5 && ` +${stats.sources.length - 5} more`}
        </span>
      </div>
    </div>
  );
}
