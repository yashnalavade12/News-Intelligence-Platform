import React from "react";

const s = {
  wrap: { display: "flex", alignItems: "center", justifyContent: "center", gap: 8, marginTop: 40 },
  btn: (active, disabled) => ({
    padding: "7px 14px", borderRadius: 8, fontSize: 13, fontWeight: 500,
    background: active ? "var(--amber)" : "var(--bg-2)",
    color: active ? "#000" : disabled ? "var(--text-muted)" : "var(--text)",
    border: `1px solid ${active ? "var(--amber)" : "var(--border)"}`,
    opacity: disabled ? 0.4 : 1,
    cursor: disabled ? "default" : "pointer",
    transition: "all 0.15s",
  }),
  info: { fontSize: 13, color: "var(--text-muted)", padding: "0 8px" },
};

export default function Pagination({ page, total, pageSize, onChange }) {
  const totalPages = Math.ceil(total / pageSize);
  if (totalPages <= 1) return null;

  const pages = [];
  for (let i = Math.max(1, page - 2); i <= Math.min(totalPages, page + 2); i++) pages.push(i);

  return (
    <div style={s.wrap}>
      <button style={s.btn(false, page === 1)} disabled={page === 1} onClick={() => onChange(page - 1)}>← Prev</button>
      {pages[0] > 1 && <span style={s.info}>…</span>}
      {pages.map((p) => (
        <button key={p} style={s.btn(p === page, false)} onClick={() => onChange(p)}>{p}</button>
      ))}
      {pages[pages.length - 1] < totalPages && <span style={s.info}>…</span>}
      <button style={s.btn(false, page === totalPages)} disabled={page === totalPages} onClick={() => onChange(page + 1)}>Next →</button>
      <span style={s.info}>Page {page} of {totalPages}</span>
    </div>
  );
}
