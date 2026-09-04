from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.schemas.product import BarcodeScanRequest, BarcodeScanResult, ProductOut
from app.services.barcode_service import scan_barcode

router = APIRouter(prefix="/api/barcode", tags=["barcode"])


@router.post("/scan", response_model=BarcodeScanResult)
def scan(payload: BarcodeScanRequest, db: Session = Depends(get_db)):
    scan_record, product = scan_barcode(db, payload.barcode)
    return BarcodeScanResult(
        barcode=payload.barcode,
        status=scan_record.status,
        source=scan_record.source,
        product=ProductOut.model_validate(product) if product else None,
    )
