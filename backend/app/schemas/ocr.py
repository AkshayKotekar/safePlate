from datetime import datetime
from pydantic import BaseModel


class ExtractedFields(BaseModel):
    product_name: str | None = None
    brand: str | None = None
    expiry_date: str | None = None
    manufacturing_date: str | None = None
    batch_number: str | None = None
    lot_number: str | None = None
    ingredients: str | None = None


class OCRProcessRequest(BaseModel):
    """Raw text already comes from the browser (Tesseract.js runs client-side —
    see spec §9, 'browser-compatible OCR'). The backend's job is text -> structured
    fields, kept separate so the OCR engine itself stays swappable."""
    raw_text: str
    image_base64: str | None = None
    ocr_confidence: float | None = None


class OCRProcessResponse(BaseModel):
    ocr_scan_id: str
    raw_text: str
    extracted_fields: ExtractedFields


class OCRConfirmRequest(BaseModel):
    ocr_scan_id: str
    fields: ExtractedFields
    product_id: str | None = None  # link to existing product, or None to create new


class OCRScanOut(BaseModel):
    id: str
    raw_text: str
    extracted_fields_json: str | None
    ocr_confidence: float | None
    product_id: str | None
    timestamp: datetime

    class Config:
        from_attributes = True
