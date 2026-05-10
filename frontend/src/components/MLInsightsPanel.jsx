import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";

const PIE_COLORS = ["#f59e0b","#10b981","#ef4444","#3b82f6","#8b5cf6","#ec4899","#14b8a6","#f97316"];

const s = {
  panel: {
    background: "var(--bg-2)", border: "1px solid var(--border)",
    borderRadius: "var(--radius)", padding: 24, marginBottom: 28,
  },
  title: {
    fontFamily: "var(--font-display)", fontSize: 18, fontWeight: 700,
    marginBottom: 20, color: "var(--text)",
  },
  grid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 20 },
  chartBox: {
    background: "var(--bg-3)", borderRadius: 8, padding: "16px 12px",
    border: "1px solid var(--border)",
  },
  chartTitle: { fontSize: 12, color: "var(--text-muted)", fontFamily: "var(--font-mono)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 14 },
  clusterWrap: { display: "flex", flexWrap: "wrap", gap: 8, marginTop: 4 },
  clusterChip: (i) => ({
    padding: "5px 12px", borderRadius: 20, fontSize: 12, fontWeight: 500,
    background: `${PIE_COLORS[i % PIE_COLORS.length]}18`,
    border: `1px solid ${PIE_COLORS[i % PIE_COLORS.length]}55`,
    color: PIE_COLORS[i % PIE_COLORS.length],
    cursor: "pointer",
  }),
  entityRow: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 },
  entityName: { fontSize: 13, color: "var(--text)" },
  entityBar: (w) => ({
    height: 4, borderRadius: 2, background: "var(--amber)",
    width: `${w}%`, minWidth: 4, marginTop: 3,
  }),
};

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: "var(--bg-3)", border: "1px solid var(--border)", padding: "8px 12px", borderRadius: 6, fontSize: 12 }}>
      <p style={{ color: "var(--text)", marginBottom: 2 }}>{label}</p>
      <p style={{ color: "var(--amber)" }}>{payload[0].value} articles</p>
    </div>
  );
};

export default function MLInsightsPanel({ stats, onClusterClick, onTopicClick }) {
  if (!stats) return null;

  const sentimentData = [
    { name: "Positive", value: stats.positive,  fill: "#10b981" },
    { name: "Negative", value: stats.negative,  fill: "#ef4444" },
    { name: "Neutral",  value: stats.neutral,   fill: "#3b82f6" },
  ];

  const maxEntityCount = Math.max(...(stats.top_entities?.map(e => e.count) || [1]));

  return (
    <div style={s.panel}>
      <div style={s.title}>🧠 ML Analytics</div>
      <div style={s.grid}>

        {/* Sentiment Pie */}
        <div style={s.chartBox}>
          <div style={s.chartTitle}>Sentiment Distribution</div>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={sentimentData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={65} label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`} labelLine={false} fontSize={11}>
                {sentimentData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Pie>
              <Tooltip contentStyle={{ background: "var(--bg-3)", border: "1px solid var(--border)", fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Topics Bar */}
        {stats.top_topics?.length > 0 && (
          <div style={s.chartBox}>
            <div style={s.chartTitle}>Zero-Shot Topics (click to filter)</div>
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={stats.top_topics} layout="vertical" onClick={(d) => d?.activePayload && onTopicClick(d.activePayload[0].payload.label)}>
                <XAxis type="number" tick={{ fontSize: 10, fill: "var(--text-muted)" }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="label" tick={{ fontSize: 10, fill: "var(--text-dim)" }} width={80} axisLine={false} tickLine={false} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="count" radius={[0, 4, 4, 0]} cursor="pointer">
                  {stats.top_topics.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* NER Entities */}
        {stats.top_entities?.length > 0 && (
          <div style={s.chartBox}>
            <div style={s.chartTitle}>Top Organizations (NER)</div>
            {stats.top_entities.slice(0, 7).map((e, i) => (
              <div key={i}>
                <div style={s.entityRow}>
                  <span style={s.entityName}>{e.name}</span>
                  <span style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>{e.count}</span>
                </div>
                <div style={s.entityBar((e.count / maxEntityCount) * 100)} />
              </div>
            ))}
          </div>
        )}

        {/* Cluster Explorer */}
        {stats.clusters?.length > 0 && (
          <div style={{ ...s.chartBox, gridColumn: "1 / -1" }}>
            <div style={s.chartTitle}>Semantic Clusters (KMeans · click to explore)</div>
            <div style={s.clusterWrap}>
              {stats.clusters.map((c, i) => (
                <button key={c.id} style={s.clusterChip(i)} onClick={() => onClusterClick(c.id)}>
                  {c.label} <span style={{ opacity: 0.6 }}>({c.count})</span>
                </button>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
