from backend.app.models import ProductModel
from backend.app.schemas.product import Product
from sqlalchemy.orm import Session

class ProductPersistenceService:
    
    @staticmethod
    def save_product(
        db:Session,
        product:Product,
        status:str="PENDING_REVIEW",
    )->ProductModel:
        pack_size = product.pack_size
        db_product = ProductModel(
            brand = product.brand,
            product_name = product.product_name,
            category = product.category,
            pack_size_value = pack_size.value if pack_size else None,
            pack_size_unit = pack_size.unit if pack_size else None,
             mrp=product.mrp,
            ingredients=product.ingredients,
            description=product.description,
            attributes=product.attributes,
            identifiers=product.identifiers.model_dump(),
            status=status,
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product