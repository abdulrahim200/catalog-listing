import uuid
from sqlalchemy import Float,String,Text
from sqlalchemy.dialects.postgresql import JSONB,UUID
from sqlalchemy.orm import Mapped,mapped_column
from backend.app.database import Base

class ProductModel(Base):
    __tablename__ = "products"
    
    id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,)
    brand:Mapped[str|None] = mapped_column(String(500),nullable=True)
    product_name: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)

    pack_size_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    pack_size_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mrp: Mapped[float | None] = mapped_column(Float, nullable=True)

    ingredients: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    attributes: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    identifiers: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING_REVIEW",
    )

    