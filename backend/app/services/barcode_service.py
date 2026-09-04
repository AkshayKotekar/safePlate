from sqlalchemy.orm import Session

from app.integrations.external_products.mock_lookup import lookup_barcode
from app.models.product import Product, BarcodeScan, ProductSource, ScanStatus


def scan_barcode(db: Session, barcode: str) -> tuple[BarcodeScan, Product | None]:
    existing = db.query(Product).filter(Product.barcode == barcode).first()
    if existing:
        scan = BarcodeScan(barcode=barcode, source="local_db", status=ScanStatus.FOUND, product_id=existing.id)
        db.add(scan)
        db.commit()
        db.refresh(scan)
        return scan, existing

    mock_data = lookup_barcode(barcode)
    if mock_data:
        product = Product(barcode=barcode, source=ProductSource.BARCODE_LOOKUP, **mock_data)
        db.add(product)
        db.flush()
        scan = BarcodeScan(barcode=barcode, source="mock_external_db", status=ScanStatus.FOUND, product_id=product.id)
        db.add(scan)
        db.commit()
        db.refresh(scan)
        db.refresh(product)
        return scan, product

    scan = BarcodeScan(barcode=barcode, source="none", status=ScanStatus.NOT_FOUND)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan, None
