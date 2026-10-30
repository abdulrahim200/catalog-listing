from uuid import uuid4
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import get_db
from backend.app.models import ProductModel


client = TestClient(app)


def override_get_db():
    db = MagicMock()
    try:
        yield db
    finally:
        pass


app.dependency_overrides[get_db] = override_get_db


def make_product():
    product = MagicMock(spec=ProductModel)

    product.id = uuid4()
    product.brand = "QUAKER"
    product.product_name = "Cruesli Mélange de Noix"
    product.category = "Breakfast Cereal"
    product.pack_size_value = 500.0
    product.pack_size_unit = "g"
    product.mrp = 250.0
    product.ingredients = ["Oats", "Nuts"]
    product.description = "Crispy cereal with nuts"
    product.attributes = {"claims": ["High in fibre"]}
    product.identifiers = {"barcode": None, "sku": None}
    product.status = "PENDING_REVIEW"

    return product


@patch("backend.app.main.ProductModel", ProductModel)
def test_get_products_returns_list():
    product = make_product()

    with patch("backend.app.main.get_db", return_value=None):
        app.dependency_overrides[get_db] = override_get_db
        db = next(override_get_db())

        query = MagicMock()
        query.order_by.return_value = query
        query.offset.return_value = query
        query.limit.return_value = query
        query.all.return_value = [product]
        db.query.return_value = query

        app.dependency_overrides[get_db] = lambda: db

        response = client.get("/api/products?limit=20&offset=0")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["brand"] == "QUAKER"
    assert data[0]["product_name"] == "Cruesli Mélange de Noix"


def test_get_product_by_id_returns_product():
    product = make_product()

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = product
    app.dependency_overrides[get_db] = lambda: db

    response = client.get(f"/api/products/{product.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(product.id)
    assert data["brand"] == "QUAKER"
    assert data["status"] == "PENDING_REVIEW"


def test_get_product_by_id_returns_404_when_missing():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    app.dependency_overrides[get_db] = lambda: db

    response = client.get(f"/api/products/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"