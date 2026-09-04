"""Mock product lookup — stands in for a real external product database
(e.g. Open Food Facts) so the barcode workflow works with zero paid/external
API dependency, per spec §51 (external APIs must never be mandatory for MVP).

Swap `lookup_barcode` for a real HTTP call later; callers only see the same
(status, data, source) shape either way.
"""

# A handful of real-looking EAN/UPC barcodes so testers can type/scan something
# concrete without needing an actual physical product on hand.
_MOCK_DB: dict[str, dict] = {
    "8901030895555": {
        "product_name": "Amul Butter",
        "brand": "Amul",
        "category": "Dairy",
        "ingredients": "Milk fat, salt",
        "allergens": "Milk",
        "manufacturer": "Gujarat Cooperative Milk Marketing Federation",
        "nutrition_information": "Energy 720kcal/100g, Fat 80g, Protein 0.5g",
        "image_url": None,
    },
    "8901063017277": {
        "product_name": "Maggi 2-Minute Noodles",
        "brand": "Nestle",
        "category": "Instant Food",
        "ingredients": "Wheat flour, palm oil, salt, spices",
        "allergens": "Wheat, Soy",
        "manufacturer": "Nestle India Ltd",
        "nutrition_information": "Energy 450kcal/100g, Fat 18g, Carbs 60g",
        "image_url": None,
    },
    "0012000161155": {
        "product_name": "Coca-Cola Classic 355ml",
        "brand": "Coca-Cola",
        "category": "Beverages",
        "ingredients": "Carbonated water, sugar, caramel color, phosphoric acid, caffeine",
        "allergens": None,
        "manufacturer": "The Coca-Cola Company",
        "nutrition_information": "Energy 140kcal/355ml, Sugar 39g",
        "image_url": None,
    },
}


def lookup_barcode(barcode: str) -> dict | None:
    """Returns product field dict if found in the mock DB, else None."""
    return _MOCK_DB.get(barcode.strip())
