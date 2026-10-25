
from backend.app.services.normalization_service import (
    parse_value_and_unit,
)

from backend.app.services.normalization_service import (
    normalize_product_attributes,
)

def test_decimal_comma():
    assert parse_value_and_unit("8,5 g") == {
        "value": 8.5,
        "unit": "g",
    }


def test_integer_value():
    assert parse_value_and_unit("19g") == {
        "value": 19.0,
        "unit": "g",
    }


def test_milligrams():
    assert parse_value_and_unit("0,19 mg") == {
        "value": 0.19,
        "unit": "mg",
    }


def test_percentage():
    assert parse_value_and_unit("12%") == {
        "value": 12.0,
        "unit": "%",
    }


def test_invalid_value():
    assert parse_value_and_unit("unknown") == {
        "value": None,
        "unit": None,
    }
def test_normalize_nested_nutrition():
    data = {
        "nutrition": {
            "per_100g": {
                "fat": "19g",
                "protein": "8,5g",
                "energy": {
                    "kj": 1913,
                    "kcal": 462,
                },
            }
        }
    }

    result = normalize_product_attributes(data)

    assert result["nutrition"]["per_100g"]["fat"] == {
        "value": 19.0,
        "unit": "g",
    }
    assert result["nutrition"]["per_100g"]["protein"] == {
        "value": 8.5,
        "unit": "g",
    }
    assert result["nutrition"]["per_100g"]["energy"] == {
        "kj": 1913,
        "kcal": 462,
    }


def test_normalize_list_values():
    from backend.app.services.normalization_service import (
        normalize_nutrition_values,
    )

    result = normalize_nutrition_values(["8,5 g", "unknown"])

    assert result == [
        {"value": 8.5, "unit": "g"},
        "unknown",
    ]

def test_preserve_percentages():
    assert parse_value_and_unit("12%") == {
        "value": 12.0,
        "unit": "%",
    }
def test_normalize_nutrition_only():
    attributes = {
        "claims": ["Riche en fibres"],
        "serving_size": {"value": 45, "unit": "g"},
        "nutrition": {
            "per_100g": {
                "fat": "19g",
                "protein": "8,5g",
                "energy": {"kj": 1913, "kcal": 462},
            }
        },
    }

    result = normalize_product_attributes(attributes)

    assert result["nutrition"]["per_100g"]["fat"] == {
        "value": 19.0,
        "unit": "g",
    }
    assert result["nutrition"]["per_100g"]["protein"] == {
        "value": 8.5,
        "unit": "g",
    }
    assert result["nutrition"]["per_100g"]["energy"] == {
        "kj": 1913,
        "kcal": 462,
    }
    assert result["claims"] == ["Riche en fibres"]
    assert result["serving_size"] == {"value": 45, "unit": "g"}


def test_normalize_separate_nutrition_keys():
    attributes = {
        "nutrition_per_100g": {"fat": "19g"},
        "description": "Contains 19g of fat",
    }

    result = normalize_product_attributes(attributes)

    assert result["nutrition_per_100g"]["fat"] == {
        "value": 19.0,
        "unit": "g",
    }
    assert result["description"] == "Contains 19g of fat"
