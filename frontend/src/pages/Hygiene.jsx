import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api.js";

export default function Hygiene() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.getHygieneCategories().then(setData);
  }, []);

  if (!data) return <div className="empty-state">Loading…</div>;

  return (
    <div>
      <h1>SafePlate Hygiene Score</h1>
      <p className="subtitle">
        A 100-point scorecard whose categories are <strong>informed by FDA Food Code food-safety risk factors</strong>.
        Scores are computed per-restaurant from actual evidence (camera/CV detections, sensor readings, OCR, manual
        inspection) — see a live example on the <Link to="/restaurants">Restaurants</Link> page.
      </p>

      <div className="card" style={{ maxWidth: 640, marginBottom: 20, borderColor: "var(--orange)" }}>
        <strong>{data.disclaimer}</strong>
        <p style={{ color: "var(--muted)", fontSize: 13, marginTop: 8, marginBottom: 0 }}>
          SafePlate's {data.passing_threshold}/100 passing threshold is a prototype rule — the FDA does not define a
          universal numeric passing score.
        </p>
      </div>

      <h2>Category Breakdown (100 points total)</h2>
      <div className="grid">
        {data.categories.map((c) => (
          <div className="card" key={c.key}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <div style={{ fontWeight: 600 }}>{c.name}</div>
              <div style={{ fontWeight: 700, color: "var(--accent)" }}>{c.max_score} pts</div>
            </div>
          </div>
        ))}
      </div>

      <h2 style={{ marginTop: 24 }}>Status Thresholds</h2>
      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        <span className="pill" style={{ background: "rgba(51,209,122,0.2)", color: "var(--green)" }}>90-100 Excellent</span>
        <span className="pill" style={{ background: "rgba(62,166,255,0.2)", color: "var(--accent)" }}>70-89 Safe / Pass</span>
        <span className="pill sev-medium">50-69 Warning</span>
        <span className="pill sev-high">0-49 Unhygienic / High Risk</span>
      </div>
    </div>
  );
}
