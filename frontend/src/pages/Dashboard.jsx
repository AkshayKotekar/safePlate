import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api.js";

export default function Dashboard() {
  const [products, setProducts] = useState([]);
  const [events, setEvents] = useState([]);
  const [restaurants, setRestaurants] = useState([]);

  useEffect(() => {
    api.listProducts().then(setProducts).catch(() => {});
    api.listEvents().then(setEvents).catch(() => {});
    api.nearbyRestaurants().then(setRestaurants).catch(() => {});
  }, []);

  return (
    <div>
      <h1>SafePlate Dashboard</h1>
      <p className="subtitle">Food-safety intelligence overview — hospitality &amp; retail prototype.</p>

      <div style={{ display: "flex", gap: 16, marginBottom: 24, flexWrap: "wrap" }}>
        <div className="card" style={{ flex: 1, minWidth: 160 }}>
          <h2>Products Scanned</h2>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{products.length}</div>
        </div>
        <div className="card" style={{ flex: 1, minWidth: 160 }}>
          <h2>Open Events</h2>
          <div style={{ fontSize: 28, fontWeight: 700, color: "var(--red)" }}>
            {events.filter((e) => e.status === "open").length}
          </div>
        </div>
        <div className="card" style={{ flex: 1, minWidth: 160 }}>
          <h2>Monitored Localities</h2>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{new Set(restaurants.map((r) => r.locality)).size}</div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <div className="card">
          <h2 style={{ marginTop: 0 }}>Get Started</h2>
          <p style={{ fontSize: 14, color: "var(--muted)", marginBottom: 14 }}>
            Three primary workflows demonstrate SafePlate today:
          </p>
          <ol style={{ fontSize: 14, paddingLeft: 20 }}>
            <li><Link to="/live">Connect a phone camera</Link> over WebRTC and view it live.</li>
            <li><Link to="/scanner">Scan a product barcode</Link> to look it up and save it.</li>
            <li><Link to="/scanner">Scan a product label</Link> with OCR and review the extracted fields.</li>
          </ol>
        </div>
        <div className="card">
          <h2 style={{ marginTop: 0 }}>Recent Events</h2>
          {events.length === 0 ? (
            <div className="empty-state">No events yet.</div>
          ) : (
            events.slice(0, 5).map((e) => (
              <div key={e.id} className="alert-meta" style={{ marginBottom: 6 }}>
                {e.type.replace(/_/g, " ")} — {new Date(e.created_at).toLocaleTimeString()}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
