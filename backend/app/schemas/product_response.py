from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    brand: str | None = None
    product_name: str | None = None
    category: str | None = None
    pack_size_value: float | None = None
    pack_size_unit: str | None = None
    mrp: float | None = None
    ingredients: list = []
    description: str | None = None
    attributes: dict = {}
    identifiers: dict = {}
    status: str