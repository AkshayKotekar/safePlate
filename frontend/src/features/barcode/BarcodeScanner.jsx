import React, { useEffect, useRef, useState } from "react";
import { BrowserMultiFormatReader } from "@zxing/browser";
import { api } from "../../services/api.js";

export default function BarcodeScanner() {
  const videoRef = useRef(null);
  const readerRef = useRef(null);
  const controlsRef = useRef(null);
  const [scanning, setScanning] = useState(false);
  const [lastBarcode, setLastBarcode] = useState(null);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("Idle");
  const [error, setError] = useState(null);

  useEffect(() => {
    readerRef.current = new BrowserMultiFormatReader();
    return () => controlsRef.current?.stop();
  }, []);

  async function startScanning() {
    setError(null);
    setResult(null);
    setStatus("Starting camera…");
    try {
      const controls = await readerRef.current.decodeFromVideoDevice(
        undefined, // let the browser pick; prefers back camera on most phones
        videoRef.current,
        async (decodeResult) => {
          if (!decodeResult) return;
          const barcode = decodeResult.getText();
          if (barcode === lastBarcode) return; // debounce repeat reads of the same code
          setLastBarcode(barcode);
          setStatus(`Detected: ${barcode} — looking up…`);
          try {
            const lookup = await api.scanBarcode(barcode);
            setResult(lookup);
            setStatus(lookup.status === "found" ? "Product found" : "Product not found in database");
          } catch (err) {
            setError(err.message);
          }
        }
      );
      controlsRef.current = controls;
      setScanning(true);
      setStatus("Scanning — point camera at a barcode");
    } catch (err) {
      setError(
        err.name === "NotAllowedError"
          ? "Camera permission denied."
          : `Camera error: ${err.message}`
      );
    }
  }

  function stopScanning() {
    controlsRef.current?.stop();
    setScanning(false);
    setStatus("Idle");
  }

  return (
    <div>
      <div className="camera-video-wrap" style={{ aspectRatio: "4/3", maxWidth: 480 }}>
        <video ref={videoRef} style={{ width: "100%", height: "100%", objectFit: "cover" }} muted />
      </div>

      <div style={{ margin: "12px 0", display: "flex", gap: 10 }}>
        {!scanning ? (
          <button className="btn" onClick={startScanning}>Start Barcode Scan</button>
        ) : (
          <button className="btn btn-secondary" onClick={stopScanning}>Stop</button>
        )}
      </div>

      {error && <div style={{ color: "var(--red)" }}>{error}</div>}
      <div className="camera-meta">{status}</div>

      {result && (
        <div className="card" style={{ marginTop: 12, maxWidth: 480 }}>
          <div className="camera-meta">Barcode: {result.barcode} · source: {result.source}</div>
          {result.product ? (
            <div style={{ marginTop: 8 }}>
              <div style={{ fontWeight: 700 }}>{result.product.product_name}</div>
              <div className="camera-meta">{result.product.brand} · {result.product.category}</div>
              <div style={{ fontSize: 13, marginTop: 6 }}>{result.product.ingredients}</div>
            </div>
          ) : (
            <div style={{ marginTop: 8, color: "var(--muted)" }}>
              No product found for this barcode. Add it manually from the Products page.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
