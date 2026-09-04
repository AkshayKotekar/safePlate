import React, { useEffect, useState } from "react";
import { api } from "../services/api.js";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listProducts().then(setProducts).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="empty-state">Loading…</div>;

  return (
    <div>
      <h1>Products</h1>
      <p className="subtitle">Saved via barcode lookup or OCR label scan.</p>

      {products.length === 0 ? (
        <div className="empty-state">No products yet. Scan a barcode or product label from Product Scanner.</div>
      ) : (
        <div className="grid">
          {products.map((p) => (
            <div className="card" key={p.id}>
              <div style={{ fontWeight: 700 }}>{p.product_name || "(unnamed)"}</div>
              <div className="camera-meta">{p.brand} {p.category ? `· ${p.category}` : ""}</div>
              <div style={{ fontSize: 13, margin: "8px 0", color: "var(--muted)" }}>
                {p.barcode && <div>Barcode: {p.barcode}</div>}
                {p.expiry_date && <div>Expiry: {p.expiry_date}</div>}
                {p.batch_number && <div>Batch: {p.batch_number}</div>}
              </div>
              <span className="pill" style={{ background: "rgba(62,166,255,0.15)", color: "var(--accent)" }}>
                {p.source}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
