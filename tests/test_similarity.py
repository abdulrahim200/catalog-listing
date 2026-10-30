from backend.app.schemas.product import Product
from backend.app.services.product_similarity_service import (
    ProductSimilarityService,
)


service = ProductSimilarityService()

product_a = Product(
    brand="QUAKER",
    product_name="Cruesli Mélange de Noix",
    category="Breakfast Cereal",
    description="Crispy cereal with mixed nuts",
    ingredients=["Oats", "Wheat", "Hazelnuts", "Almonds"],
)

product_b = Product(
    brand="QUAKER",
    product_name="Cruesli Mélange de noix",
    category="Breakfast Cereal",
    description="Crispy cereal with mixed nuts",
    ingredients=["Oats", "Wheat", "Hazelnuts", "Almonds"],
)

product_c = Product(
    brand="Test Brand",
    product_name="Tomato Ketchup",
    category="Sauces",
    description="Tomato sauce",
    ingredients=["Tomatoes", "Sugar", "Vinegar"],
)

print(
    "Similar products:",
    service.calculate_score(product_a, product_b),
)

print(
    "Different products:",
    service.calculate_score(product_a, product_c),
)