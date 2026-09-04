from datetime import datetime
from pydantic import BaseModel

from app.models.product import ProductSource, ScanStatus


class ProductBase(BaseModel):
    barcode: str | None = None
    product_name: str | None = None
    brand: str | None = None
    category: str | None = None
    ingredients: str | None = None
    allergens: str | None = None
    manufacturer: str | None = None
    manufacturing_date: str | None = None
    expiry_date: str | None = None
    batch_number: str | None = None
    lot_number: str | None = None
    nutrition_information: str | None = None
    image_url: str | None = None


class ProductCreate(ProductBase):
    source: ProductSource = ProductSource.MANUAL


class ProductUpdate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: str
    source: ProductSource
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BarcodeScanRequest(BaseModel):
    barcode: str


class BarcodeScanResult(BaseModel):
    barcode: str
    status: ScanStatus
    source: str
    product: ProductOut | None = None
