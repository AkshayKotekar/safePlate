import React, { useEffect, useRef, useState } from "react";
import { createWorker } from "tesseract.js";
import { api } from "../../services/api.js";

const FIELD_LABELS = {
  product_name: "Product Name",
  brand: "Brand",
  expiry_date: "Expiry Date",
  manufacturing_date: "Manufacturing Date",
  batch_number: "Batch Number",
  lot_number: "Lot Number",
  ingredients: "Ingredients",
};

export default function OcrScanner() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const workerRef = useRef(null);
  const [streamReady, setStreamReady] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [rawText, setRawText] = useState(null);
  const [ocrScanId, setOcrScanId] = useState(null);
  const [fields, setFields] = useState(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let stream;
    (async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 }, height: { ideal: 720 } },
        });
        videoRef.current.srcObject = stream;
        setStreamReady(true);
      } catch (err) {
        setError(`Camera error: ${err.message}`);
      }
    })();
    return () => stream?.getTracks().forEach((t) => t.stop());
  }, []);

  async function captureAndExtract() {
    setProcessing(true);
    setError(null);
    setSaved(false);
    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas.getContext("2d").drawImage(video, 0, 0);
      const dataUrl = canvas.toDataURL("image/jpeg", 0.85);

      if (!workerRef.current) {
        workerRef.current = await createWorker("eng");
      }
      const { data } = await workerRef.current.recognize(dataUrl);
      setRawText(data.text);

      const response = await api.processOcr({
        raw_text: data.text,
        image_base64: dataUrl,
        ocr_confidence: data.confidence / 100,
      });
      setOcrScanId(response.ocr_scan_id);
      setFields(response.extracted_fields);
    } catch (err) {
      setError(err.message);
    } finally {
      setProcessing(false);
    }
  }

  async function save() {
    try {
      await api.confirmOcr({ ocr_scan_id: ocrScanId, fields, product_id: null });
      setSaved(true);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <div className="camera-video-wrap" style={{ aspectRatio: "4/3", maxWidth: 480 }}>
        <video ref={videoRef} autoPlay playsInline muted style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </div>
      <canvas ref={canvasRef} style={{ display: "none" }} />

      <div style={{ margin: "12px 0" }}>
        <button className="btn" onClick={captureAndExtract} disabled={!streamReady || processing}>
          {processing ? "Extracting text…" : "Capture Label & Extract Text"}
        </button>
      </div>

      {error && <div style={{ color: "var(--red)" }}>{error}</div>}

      {rawText !== null && (
        <div className="card" style={{ maxWidth: 480 }}>
          <h2 style={{ marginTop: 0 }}>Review Extracted Fields</h2>
          <p className="camera-meta" style={{ marginBottom: 12 }}>
            OCR is not always accurate — check and correct before saving.
          </p>
          {Object.keys(FIELD_LABELS).map((key) => (
            <div className="form-group" key={key}>
              <label>{FIELD_LABELS[key]}</label>
              <input
                value={fields?.[key] || ""}
                onChange={(e) => setFields({ ...fields, [key]: e.target.value })}
              />
            </div>
          ))}
          <details style={{ marginBottom: 12 }}>
            <summary className="camera-meta" style={{ cursor: "pointer" }}>Raw OCR text</summary>
            <pre style={{ whiteSpace: "pre-wrap", fontSize: 12, color: "var(--muted)" }}>{rawText}</pre>
          </details>
          <button className="btn" onClick={save} disabled={saved}>
            {saved ? "Saved ✓" : "Save to Product Database"}
          </button>
        </div>
      )}
    </div>
  );
}
