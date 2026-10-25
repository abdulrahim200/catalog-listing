from backend.app.database import SessionLocal
from backend.app.schemas.product import Product
from backend.app.services.product_persisitence import (
    ProductPersistenceService,
)

sample_product = Product(
    brand="Test Brand",
    product_name="Test Cereal",
    category="Breakfast Cereal",
    ingredients=["Oats", "Sugar"],
    description="Sample product for database persistence",
    attributes={
        "nutrition_per_100g": {
            "energy": {"kj": 1500, "kcal": 360},
            "protein": {"value": 10, "unit": "g"},
        }
    },
)

db = SessionLocal()

try:
    saved_product = ProductPersistenceService.save_product(db=db,product=sample_product,)    
    
    print("Product saved successfully!")
    print("Product ID:", saved_product.id)
    print("Product name:", saved_product.product_name)
    print("Status:", saved_product.status)
finally:
    db.close()