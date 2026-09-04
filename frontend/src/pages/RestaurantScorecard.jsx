import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../services/api.js";
import ScoreGauge from "../components/ScoreGauge.jsx";

const STATUS_COLOR = {
  EXCELLENT: "var(--green)",
  SAFE: "var(--accent)",
  WARNING: "var(--orange)",
  UNHYGIENIC: "var(--red)",
};

export default function RestaurantScorecard() {
  const { id } = useParams();
  const [scorecard, setScorecard] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getScorecard(id).then(setScorecard).catch((e) => setError(e.message));
  }, [id]);

  if (error) return <div className="empty-state">{error}</div>;
  if (!scorecard) return <div className="empty-state">Loading…</div>;

  const color = STATUS_COLOR[scorecard.status] || "var(--muted)";
  const totalIssues = scorecard.categories.reduce((sum, c) => sum + c.issues.length, 0);
  const totalEvidence = scorecard.categories.reduce((sum, c) => sum + c.evidence.length, 0);

  return (
    <div>
      <Link to="/restaurants" style={{ fontSize: 13 }}>&larr; Back to Restaurants</Link>
      <h1 style={{ marginTop: 10 }}>{scorecard.restaurant_name}</h1>
      <p className="subtitle">SafePlate Hygiene Scorecard — computed {new Date(scorecard.computed_at).toLocaleString()}</p>

      <div className="card" style={{ maxWidth: 520, textAlign: "center", padding: 32, marginBottom: 20 }}>
        <ScoreGauge score={scorecard.score} size={140} strokeWidth={12} />
        <div style={{ marginTop: 14 }}>
          <span className="pill" style={{ background: `${color}22`, color, fontSize: 13, padding: "4px 14px" }}>
            {scorecard.status}
          </span>
        </div>
        <div style={{ color: "var(--muted)", fontSize: 12, marginTop: 10 }}>
          Passing Threshold: {scorecard.passing_threshold} / {scorecard.max_score}
        </div>
      </div>

      <h2>Category Breakdown</h2>
      <div style={{ maxWidth: 640 }}>
        {scorecard.categories.map((c) => {
          const pct = (c.score / c.max_score) * 100;
          return (
            <div key={c.key} style={{ marginBottom: 14 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14, marginBottom: 4 }}>
                <span>{c.name}</span>
                <span style={{ fontWeight: 700 }}>{c.score} / {c.max_score}</span>
              </div>
              <div style={{ background: "var(--panel2)", borderRadius: 6, height: 8, overflow: "hidden" }}>
                <div style={{
                  width: `${pct}%`, height: "100%",
                  background: pct === 100 ? "var(--green)" : pct >= 60 ? "var(--orange)" : "var(--red)",
                }} />
              </div>
            </div>
          );
        })}
      </div>

      <h2 style={{ marginTop: 24 }}>Issues & Evidence</h2>
      {totalIssues === 0 ? (
        <div className="empty-state">No issues detected — all categories at full marks.</div>
      ) : (
        <div style={{ maxWidth: 640 }}>
          {scorecard.categories.filter((c) => c.issues.length > 0).map((c) => (
            <div className="alert-item sev-medium" key={c.key}>
              <div className="alert-title">{c.name}</div>
              {c.issues.map((issue, i) => (
                <div className="alert-meta" key={i}>{issue}</div>
              ))}
            </div>
          ))}
          <div className="camera-meta" style={{ marginTop: 8 }}>
            {totalEvidence} evidence item{totalEvidence !== 1 ? "s" : ""} across {scorecard.categories.filter(c => c.issues.length).length} categor{scorecard.categories.filter(c => c.issues.length).length !== 1 ? "ies" : "y"}
          </div>
        </div>
      )}

      <div className="instructions-box" style={{ maxWidth: 640, marginTop: 24 }}>
        <strong>{scorecard.disclaimer}</strong>
      </div>
    </div>
  );
}
