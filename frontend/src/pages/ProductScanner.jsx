import React, { useState } from "react";
import BarcodeScanner from "../features/barcode/BarcodeScanner.jsx";
import OcrScanner from "../features/ocr/OcrScanner.jsx";

export default function ProductScanner() {
  const [mode, setMode] = useState("barcode");

  return (
    <div>
      <h1>Product Scanner</h1>
      <p className="subtitle">Works on phone or desktop — the browser's own camera is used directly (no pairing needed).</p>

      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        <button className={`btn ${mode === "barcode" ? "" : "btn-secondary"}`} onClick={() => setMode("barcode")}>
          Barcode Scan
        </button>
        <button className={`btn ${mode === "ocr" ? "" : "btn-secondary"}`} onClick={() => setMode("ocr")}>
          OCR Label Scan
        </button>
      </div>

      {mode === "barcode" ? <BarcodeScanner /> : <OcrScanner />}
    </div>
  );
}
