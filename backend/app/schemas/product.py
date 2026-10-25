
from pydantic import BaseModel, Field, ConfigDict


class Identifiers(BaseModel):
    barcode: str | None = None
    sku: str | None = None


class PackSize(BaseModel):
    value: float | None = None
    unit: str | None = None


class Product(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
    )

    brand: str | None = None
    product_name: str | None = None
    category: str | None = None

    pack_size: PackSize = Field(default_factory=PackSize)
    mrp: float | None = None

    ingredients: list[str] = Field(default_factory=list)
    description: str | None = None

    # Keep flexible while product extraction is evolving.
    attributes: dict[str, object] = Field(default_factory=dict)

    identifiers: Identifiers = Field(default_factory=Identifiers)
