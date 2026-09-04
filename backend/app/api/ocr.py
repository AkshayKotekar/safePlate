import base64
import json
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.db import get_db
from app.models.product import OCRScan, Product, ProductSource
from app.schemas.ocr import OCRConfirmRequest, OCRProcessRequest, OCRProcessResponse
from app.schemas.product import ProductOut
from app.services.ocr_service import extract_fields

router = APIRouter(prefix="/api/ocr", tags=["ocr"])

_OCR_IMAGES_DIR = os.path.join(settings.media_dir, "ocr")
os.makedirs(_OCR_IMAGES_DIR, exist_ok=True)


@router.post("/process", response_model=OCRProcessResponse)
def process_ocr(payload: OCRProcessRequest, db: Session = Depends(get_db)):
    if not payload.raw_text.strip():
        raise HTTPException(400, "No text detected. Try recapturing with better lighting/focus.")

    fields = extract_fields(payload.raw_text)

    image_path = None
    if payload.image_base64:
        try:
            data = base64.b64decode(payload.image_base64.split(",")[-1])
            filename = f"{uuid.uuid4()}.jpg"
            path = os.path.join(_OCR_IMAGES_DIR, filename)
            with open(path, "wb") as f:
                f.write(data)
            image_path = f"ocr/{filename}"
        except Exception:
            image_path = None

    scan = OCRScan(
        image_path=image_path,
        raw_text=payload.raw_text,
        extracted_fields_json=json.dumps(fields.model_dump()),
        ocr_confidence=payload.ocr_confidence,
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return OCRProcessResponse(ocr_scan_id=scan.id, raw_text=scan.raw_text, extracted_fields=fields)


@router.post("/confirm", response_model=ProductOut)
def confirm_ocr(payload: OCRConfirmRequest, db: Session = Depends(get_db)):
    """User has reviewed/edited the extracted fields — only now do we write a
    Product record. Verified product data is never silently overwritten by
    raw OCR guesses (spec §11)."""
    scan = db.get(OCRScan, payload.ocr_scan_id)
    if scan is None:
        raise HTTPException(404, "OCR scan not found")

    field_data = {k: v for k, v in payload.fields.model_dump().items() if v is not None}

    if payload.product_id:
        product = db.get(Product, payload.product_id)
        if product is None:
            raise HTTPException(404, "Product not found")
        for k, v in field_data.items():
            setattr(product, k, v)
    else:
        product = Product(source=ProductSource.OCR, **field_data)
        db.add(product)

    db.flush()
    scan.product_id = product.id
    db.commit()
    db.refresh(product)
    return product
