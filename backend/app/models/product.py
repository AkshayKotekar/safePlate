import enum
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.common import uid, utcnow


class ProductSource(str, enum.Enum):
    BARCODE_LOOKUP = "barcode_lookup"   # matched via external/mock barcode DB
    OCR = "ocr"                          # created/updated from OCR label extraction
    MANUAL = "manual"                    # manually entered/edited by a user


class ScanStatus(str, enum.Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    ERROR = "error"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    barcode: Mapped[str] = mapped_column(String, nullable=True, index=True)
    product_name: Mapped[str] = mapped_column(String, nullable=True)
    brand: Mapped[str] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=True)
    ingredients: Mapped[str] = mapped_column(Text, nullable=True)
    allergens: Mapped[str] = mapped_column(Text, nullable=True)
    manufacturer: Mapped[str] = mapped_column(String, nullable=True)
    manufacturing_date: Mapped[str] = mapped_column(String, nullable=True)  # free-text; OCR dates are unreliable
    expiry_date: Mapped[str] = mapped_column(String, nullable=True)
    batch_number: Mapped[str] = mapped_column(String, nullable=True)
    lot_number: Mapped[str] = mapped_column(String, nullable=True)
    nutrition_information: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    source: Mapped[ProductSource] = mapped_column(Enum(ProductSource), default=ProductSource.MANUAL)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    barcode_scans: Mapped[list["BarcodeScan"]] = relationship(back_populates="product")
    ocr_scans: Mapped[list["OCRScan"]] = relationship(back_populates="product")


class BarcodeScan(Base):
    __tablename__ = "barcode_scans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    barcode: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, default="mock")  # e.g. "mock", "openfoodfacts"
    status: Mapped[ScanStatus] = mapped_column(Enum(ScanStatus), default=ScanStatus.NOT_FOUND)
    product_id: Mapped[str] = mapped_column(String, ForeignKey("products.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    product: Mapped["Product"] = relationship(back_populates="barcode_scans")


class OCRScan(Base):
    __tablename__ = "ocr_scans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    image_path: Mapped[str] = mapped_column(String, nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_fields_json: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    ocr_confidence: Mapped[float] = mapped_column(nullable=True)
    product_id: Mapped[str] = mapped_column(String, ForeignKey("products.id"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    product: Mapped["Product"] = relationship(back_populates="ocr_scans")
