
import pytest

from backend.app.schemas.product import Product
from backend.app.services.evidence_validation_service import (
    EvidenceValidationService,
    normalize_text,
    product_name_is_supported,
)


@pytest.fixture
def service():
    return EvidenceValidationService()


@pytest.fixture
def product():
    return Product(
        brand="QUAKER",
        product_name="Cruesli Mélange de Noix",
        category="Cereal",
        pack_size={"value": 450, "unit": "g"},
        mrp=250.0,
        ingredients=["Oats", "Nuts"],
    )


def test_normalize_text_handles_case_accents_and_whitespace():
    result = normalize_text("  MÉLANGE   DE  NOIX ")

    assert result == "melange de noix"


def test_brand_and_product_name_supported_by_ocr(service, product):
    ocr_text = """
    QUAKER
    Cruesli
    MÉLANGE DE NOIX
    """

    result = service.validate(product, ocr_text)

    supported_fields = {
        item.field for item in result.supported_fields
    }

    assert "brand" in supported_fields
    assert "product_name" in supported_fields
    assert all(
    item.field not in {"brand", "product_name"}
    for item in result.unsupported_fields
    )


def test_product_name_supported_when_words_are_separated(
    service, product
):
    ocr_text = """
    Cruesli
    QUAKER
    MÉLANGE DE NOIX
    """

    result = service.validate(product, ocr_text)

    assert any(
        item.field == "product_name"
        and item.status == "SUPPORTED"
        for item in result.supported_fields
    )


def test_missing_brand_is_reported_as_not_found(service, product):
    ocr_text = """
    Cruesli
    MÉLANGE DE NOIX
    """

    result = service.validate(product, ocr_text)

    assert any(
        item.field == "brand"
        and item.status == "NOT_FOUND"
        for item in result.unsupported_fields
    )


def test_missing_product_name_words_are_not_supported(
    service, product
):
    product.product_name = "Chocolate Cookies"

    result = service.validate(product, "QUAKER Oats cereal")

    assert any(
        item.field == "product_name"
        and item.status == "NOT_FOUND"
        for item in result.unsupported_fields
    )


def test_mrp_not_found_in_ocr(service, product):
    result = service.validate(product, "QUAKER Cruesli Mélange de Noix")

    assert any(
        item.field == "mrp"
        and item.status == "NOT_FOUND"
        for item in result.unsupported_fields
    )


def test_empty_ocr_marks_nonempty_values_not_found(
    service, product
):
    result = service.validate(product, "")

    assert result.supported_fields == []
    assert {
        item.field for item in result.unsupported_fields
    } == {"brand", "product_name", "mrp"}


def test_empty_product_fields_are_skipped(service, product):
    product.brand = None
    product.product_name = None
    product.mrp = None

    result = service.validate(product, "")

    assert result.supported_fields == []
    assert result.unsupported_fields == []


def test_product_name_matching_is_case_insensitive():
    assert product_name_is_supported(
        "Cruesli Mélange de Noix",
        "QUAKER CRUESLI MÉLANGE DE NOIX",
    )


def test_product_name_does_not_match_partial_words():
    assert not product_name_is_supported(
        "Nut",
        "Nutrition facts",
    )
