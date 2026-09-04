"""Raw OCR text -> structured field extraction.

This is intentionally simple regex/heuristic parsing, not NLP — it exists to
turn messy label text into candidate fields for the user to review and correct
(see spec §9: OCR results are never treated as verified until a human confirms
them). OCR itself happens client-side in the browser (Tesseract.js); this
module never touches image pixels.
"""
import re

from app.schemas.ocr import ExtractedFields

_DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{2,4}|\d{4}[\/\-.]\d{1,2}[\/\-.]\d{1,2}|"
    r"\d{1,2}[\/\-.]\d{4}|"  # MM/YYYY — common short form for expiry/mfg on food labels
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s?\d{2,4})\b",
    re.IGNORECASE,
)
_BATCH_PATTERN = re.compile(r"\b(?:batch|b\.?no\.?)\s*[:\-]?\s*([A-Za-z0-9\-]+)", re.IGNORECASE)
_LOT_PATTERN = re.compile(r"\b(?:lot)\s*[:\-]?\s*([A-Za-z0-9\-]+)", re.IGNORECASE)
_EXPIRY_LABEL_PATTERN = re.compile(r"(?:exp(?:iry)?|use by|best before)\D{0,10}", re.IGNORECASE)
_MFG_LABEL_PATTERN = re.compile(r"(?:mfg|mfd|manufactured|packed on)\D{0,10}", re.IGNORECASE)
_INGREDIENTS_PATTERN = re.compile(r"ingredients\s*[:\-]?\s*(.+)", re.IGNORECASE)


def _find_date_near(text: str, label_pattern: re.Pattern) -> str | None:
    for label_match in label_pattern.finditer(text):
        window = text[label_match.end(): label_match.end() + 20]
        date_match = _DATE_PATTERN.search(window)
        if date_match:
            return date_match.group(0)
    return None


def extract_fields(raw_text: str) -> ExtractedFields:
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    product_name = lines[0] if lines else None

    expiry_date = _find_date_near(raw_text, _EXPIRY_LABEL_PATTERN)
    manufacturing_date = _find_date_near(raw_text, _MFG_LABEL_PATTERN)

    batch_match = _BATCH_PATTERN.search(raw_text)
    lot_match = _LOT_PATTERN.search(raw_text)
    ingredients_match = _INGREDIENTS_PATTERN.search(raw_text)

    return ExtractedFields(
        product_name=product_name,
        brand=None,  # left for manual entry — brand is not reliably inferable from raw text alone
        expiry_date=expiry_date,
        manufacturing_date=manufacturing_date,
        batch_number=batch_match.group(1) if batch_match else None,
        lot_number=lot_match.group(1) if lot_match else None,
        ingredients=ingredients_match.group(1).strip() if ingredients_match else None,
    )
