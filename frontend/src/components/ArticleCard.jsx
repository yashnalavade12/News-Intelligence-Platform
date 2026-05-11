import React, { useState } from "react";

const BADGE = {
  positive: { bg: "var(--green-light)", color: "var(--green)", label: "Positive" },
  negative: { bg: "var(--red-light)",   color: "var(--red)",   label: "Negative" },
  neutral:  { bg: "var(--yellow-light)",  color: "#f59e0b",  label: "Neutral"  },
};

function timeAgo(d) {
  if (!d) return "";
  const h = Math.floor((Date.now() - new Date(d)) / 3_600_000);
  return h < 1 ? "Just now" : h < 24 ? `${h}h ago` : `${Math.floor(h/24)}d ago`;
}

const s = {
  card: (hov) => ({
    background: "var(--bg-2)", border: `1px solid var(--border)`,
    borderRadius: "var(--radius)", display: "flex", flexDirection: "column",
    transition: "all 0.25s ease", transform: hov ? "translateY(-4px)" : "translateY(0)",
    boxShadow: hov ? "0 12px 24px rgba(0,0,0,0.08)" : "0 2px 8px rgba(0,0,0,0.04)",
    animation: "fadeUp 0.35s ease both", overflow: "hidden",
  }),
  img:  { width: "100%", height: 180, objectFit: "cover", background: "var(--bg-3)", display: "block" },
  imgFallback: { width: "100%", height: 180, background: "linear-gradient(135deg,var(--bg-3),var(--bg-2))", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--border-2)", fontSize: 40 },
  body: { padding: 18, flex: 1, display: "flex", flexDirection: "column", gap: 12 },
  row:  { display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 },
  src:  { fontSize: 12, color: "var(--text-muted)", fontWeight: 600, textTransform: "capitalize" },
  time: { fontSize: 12, color: "var(--text-dim)" },
  badge: (b) => ({ display: "inline-block", padding: "4px 10px", borderRadius: 4, fontSize: 11, fontWeight: 600, background: b.bg, color: b.color, width: "fit-content" }),
  title: { fontSize: 16, fontWeight: 700, lineHeight: 1.4, color: "var(--text)" },
  summary: { fontSize: 13, color: "var(--text-muted)", lineHeight: 1.6, flex: 1 },
  footer: { display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, borderTop: "1px solid var(--border)", paddingTop: 12 },
  topicChip: {
    fontSize: 11, padding: "3px 8px", borderRadius: 4, fontWeight: 500,
    background: "var(--primary-light)",
    color: "var(--primary)", display: "inline-block", marginRight: 4
  },
  readMore: { fontSize: 12, fontWeight: 600, color: "var(--primary)", cursor: "pointer", textDecoration: "none" },
};

export default function ArticleCard({ article }) {
  const [hov, setHov]         = useState(false);
  const badge = BADGE[article.sentiment] || BADGE.neutral;

  return (
    <div style={s.card(hov)} onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}>
      {article.image_url
        ? <img src={article.image_url} alt="" style={s.img} onError={e => { e.target.style.display="none"; }} />
        : <div style={s.imgFallback}>📰</div>
      }

      <div style={s.body}>
        <div style={s.row}>
          <span style={s.src}>{article.source_name || "News Source"}</span>
          <span style={s.time}>{timeAgo(article.published_at)}</span>
        </div>

        <h3 style={s.title}>{article.title}</h3>

        {article.summary && <p style={s.summary}>{article.summary}</p>}

        <div style={s.footer}>
          <span style={s.badge(badge)}>{badge.label}</span>
          {article.url && (
            <a href={article.url} target="_blank" rel="noopener noreferrer" style={s.readMore}>
              Read more →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
          <a href={article.url} target="_blank" rel="noopener noreferrer" style={s.readMore}>
            Read full article →
          </a>
        )}
      </div>
    </div>
  );
}
