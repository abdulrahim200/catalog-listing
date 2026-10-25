
import re


def parse_value_and_unit(text: str) -> dict:
    text = text.strip().replace(",", ".")

    match = re.fullmatch(
        r"([-+]?\d+(?:\.\d+)?)\s*([a-zA-Z%]+)?",
        text,
    )

    if not match:
        return {"value": None, "unit": None}

    value_text, unit = match.groups()

    return {
        "value": float(value_text),
        "unit": unit.strip() if unit else None,
    }


def normalize_nutrition_values(data):
    """Normalize simple measurement strings in nutrition data."""

    if isinstance(data, dict):
        # Preserve existing energy structures and other numeric objects.
        return {
            key: normalize_nutrition_values(value)
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [normalize_nutrition_values(item) for item in data]

    if isinstance(data, str):
        parsed = parse_value_and_unit(data)

        if parsed["value"] is not None and parsed["unit"] is not None:
            return parsed

    return data


def normalize_product_attributes(attributes: dict) -> dict:
    """Normalize nutrition fields while preserving other attributes."""

    result = attributes.copy()

    # Shape A: attributes["nutrition"]["per_100g"] / ["per_45g"]
    if isinstance(result.get("nutrition"), dict):
        result["nutrition"] = normalize_nutrition_values(
            result["nutrition"]
        )

    # Shape B: separate nutrition keys used by some extraction responses.
    for key in (
        "nutrition_per_100g",
        "nutrition_per_45g",
        "vitamins_minerals",
    ):
        if key in result:
            result[key] = normalize_nutrition_values(result[key])

    return result
