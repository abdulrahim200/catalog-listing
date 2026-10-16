
import json
import re
from pathlib import Path

import requests


BARCODE = "3168930010883"

API_URL = (
    f"https://world.openfoodfacts.org/api/v2/product/"
    f"{BARCODE}.json"
)

IMAGE_BASE_URL = (
    "https://images.openfoodfacts.org/images/products"
)

OUTPUT_DIR = (
    Path("data")
    / "datasets"
    / "openfoodfacts"
    / BARCODE
)

HEADERS = {
    "User-Agent": (
        "AICatalogCopilot/0.1 "
        "(contact: zuhair111103@example.com)"
    )
}


def get_product_metadata() -> dict:
    """Fetch one product's metadata from Open Food Facts."""
    response = requests.get(
        API_URL,
        params={
            "fields": (
                "code,product_name,brands,categories,quantity,"
                "ingredients_text,nutriments,images"
            )
        },
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != 1:
        raise ValueError(
            f"Product not found for barcode: {BARCODE}"
        )

    return payload["product"]


def get_image_url(
    product: dict,
    image_name: str,
    resolution: str = "400",
) -> str | None:
    """Construct an image URL using official image metadata."""
    images = product.get("images", {})
    image_info = images.get(image_name)

    if not image_info:
        return None

    sizes = image_info.get("sizes", {})

    if resolution not in sizes:
        if "400" in sizes:
            resolution = "400"
        elif "full" in sizes:
            resolution = "full"
        else:
            return None

    barcode = str(product["code"]).zfill(13)

    if not barcode.isdigit():
        raise ValueError(f"Invalid barcode: {barcode}")

    # Example: 316/893/001/0883
    folder = (
        f"{barcode[:3]}/"
        f"{barcode[3:6]}/"
        f"{barcode[6:9]}/"
        f"{barcode[9:]}"
    )

    if image_name.isdigit():
        # Raw image: 1.400.jpg or 1.jpg
        if resolution == "full":
            filename = f"{image_name}.jpg"
        else:
            filename = f"{image_name}.{resolution}.jpg"

    else:
        # Selected image: front_fr.4.400.jpg
        revision = image_info.get("rev")

        if revision is None:
            return None

        filename = (
            f"{image_name}.{revision}.{resolution}.jpg"
        )

    return f"{IMAGE_BASE_URL}/{folder}/{filename}"


def download_image(
    url: str,
    destination: Path,
) -> bool:
    """Download an image from the Open Food Facts server."""
    try:
        with requests.get(
            url,
            headers=HEADERS,
            timeout=45,
            stream=True,
        ) as response:

            if response.status_code == 404:
                print(f"Image unavailable: {url}")
                return False

            response.raise_for_status()

            with destination.open("wb") as file:
                for chunk in response.iter_content(8192):
                    if chunk:
                        file.write(chunk)

        print(f"Downloaded: {destination}")
        return True

    except requests.RequestException as error:
        print(f"Download failed: {error}")
        return False


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Download product metadata.
    product = get_product_metadata()

    metadata_path = OUTPUT_DIR / "metadata.json"

    metadata_path.write_text(
        json.dumps(
            product,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Product: {product.get('product_name', 'Unknown')}")
    print(f"Metadata saved: {metadata_path}")

    # 2. Download available selected images.
    images = product.get("images", {})
    downloaded = 0

    for image_type in (
        "front",
        "ingredients",
        "nutrition",
        "packaging",
    ):
        candidates = [
            key
            for key in images
            if re.fullmatch(
                rf"{image_type}_[a-z]{{2}}",
                key,
            )
        ]

        if not candidates:
            print(f"No selected {image_type} image found.")
            continue

        # Prefer English, then Hindi, then another available language.
        preferred_key = next(
            (
                key
                for lang in ("en", "hi")
                for key in candidates
                if key == f"{image_type}_{lang}"
            ),
            candidates[0],
        )

        image_url = get_image_url(
            product,
            preferred_key,
            resolution="400",
        )

        if not image_url:
            print(f"Could not construct URL for {preferred_key}")
            continue

        destination = OUTPUT_DIR / f"{preferred_key}.jpg"

        if download_image(image_url, destination):
            downloaded += 1

    print(f"\nSelected images downloaded: {downloaded}")
    print(f"Dataset directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
