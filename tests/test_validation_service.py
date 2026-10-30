
import pytest

from backend.app.schemas.product import Product
from backend.app.services.validation_service import ValidationService


@pytest.fixture
def service():
    return ValidationService()


@pytest.fixture
def valid_product():
    return Product(
        brand="Quaker",
        product_name="Cruesli Nut Mix",
        category="Cereal",
        pack_size={"value": 500, "unit": "g"},
        mrp=250.0,
        ingredients=["Oats", "Nuts"],
    )


def test_missing_product_name_is_rejected(service, valid_product):
    valid_product.product_name = "   "

    result = service.validate(valid_product)

    assert result.valid is False
    assert result.decision == "REJECT"
    assert any(
        issue.code == "MISSING_PRODUCT_NAME"
        for issue in result.errors
    )


def test_missing_brand_produces_warning(service, valid_product):
    valid_product.brand = None

    result = service.validate(valid_product)

    assert result.valid is True
    assert result.decision == "REVIEW"
    assert any(
        issue.code == "MISSING_BRAND"
        for issue in result.warnings
    )


def test_missing_pack_size_and_mrp_produce_warnings(
    service, valid_product
):
    valid_product.pack_size.value = None
    valid_product.mrp = None

    result = service.validate(valid_product)

    warning_codes = {issue.code for issue in result.warnings}

    assert "MISSING_PACK_SIZE" in warning_codes
    assert "MISSING_MRP" in warning_codes
    assert result.valid is True
    assert result.decision == "REVIEW"


def test_invalid_pack_size_is_rejected(service, valid_product):
    valid_product.pack_size.value = 0

    result = service.validate(valid_product)

    assert result.valid is False
    assert result.decision == "REJECT"
    assert any(
        issue.code == "INVALID_PACK_SIZE"
        for issue in result.errors
    )


def test_negative_mrp_is_rejected(service, valid_product):
    valid_product.mrp = -10

    result = service.validate(valid_product)

    assert result.valid is False
    assert result.decision == "REJECT"
    assert any(
        issue.code == "INVALID_MRP"
        for issue in result.errors
    )


def test_complete_product_is_auto_approved(service, valid_product):
    result = service.validate(valid_product)

    assert result.valid is True
    assert result.errors == []
    assert result.warnings == []
    assert result.decision == "AUTO_APPROVE"
