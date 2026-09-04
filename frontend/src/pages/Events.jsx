import React, { useEffect, useState } from "react";
import { api } from "../services/api.js";

export default function Events() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    api.listEvents().then(setEvents);
  }, []);

  async function verify(id, confirmed) {
    const updated = await api.verifyEvent(id, confirmed);
    setEvents((prev) => prev.map((e) => (e.id === id ? updated : e)));
  }

  return (
    <div>
      <h1>Events & Evidence</h1>
      <p className="subtitle">
        Generic event log (camera/CV, sensor, OCR, hygiene). Populated automatically once a trained YOLO model is
        connected to the live phone feed (Milestone 23+) — for now, use{" "}
        <code>POST /api/events</code> to create test events.
      </p>

      {events.length === 0 ? (
        <div className="empty-state">No events yet.</div>
      ) : (
        events.map((e) => (
          <div className={`alert-item sev-${e.severity}`} key={e.id}>
            <div className="alert-title">
              {e.type.replace(/_/g, " ").toUpperCase()}
              <span className={`pill sev-${e.severity}`}>{e.severity}</span>
              <span className="pill" style={{ background: "rgba(255,255,255,0.08)", color: "var(--muted)" }}>{e.status}</span>
            </div>
            <div className="alert-meta">
              {e.zone || "Unknown zone"} {e.confidence != null && `· confidence ${(e.confidence * 100).toFixed(0)}%`} ·{" "}
              {new Date(e.created_at).toLocaleString()}
            </div>
            {e.status === "open" && (
              <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
                <button className="btn" onClick={() => verify(e.id, true)}>Confirm</button>
                <button className="btn btn-secondary" onClick={() => verify(e.id, false)}>False Positive</button>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}
