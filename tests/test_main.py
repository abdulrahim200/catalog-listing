from io import BytesIO
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import app
from pathlib import Path
from backend.app.schemas.product import Product

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json()== {
        "message":"Catalog-lister is running"
    }

def test_upload_rejects_more_than_three_images():
    files = [
        ("photos", (f"image{i}.jpg", BytesIO(b"fake image"), "image/jpeg"))
        for i in range(4)
    ]

    response = client.post("/api/products/extract", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Upload a maximum of three images per product."
    )


def test_upload_rejects_empty_file():
    files = [
        ("photos", ("empty.jpg", BytesIO(b""), "image/jpeg"))
    ]

    response = client.post("/api/products/extract", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "File uploaded is Empty"


def test_upload_rejects_missing_photos():
    response = client.post("/api/products/extract")

    assert response.status_code == 422

def test_upload_return_500_when_image_normalization_fails():
    files = [
        ("photos",("fornt.jpg",BytesIO(b"fake image"),"image/jpeg"))
    ]
    
    with patch(
        "backend.app.main.run_in_threadpool",side_effect=RuntimeError("Simulated normalization failure"),
    ):
        response = client.post("/api/products/extract",files=files)
    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Product extraction failed.Check Server Logs."
    )
def test_upload_successfully_extracts_product():
    # Create a sample product that simulates the LLM output.
    sample_product = Product(
        brand="Acme",
        product_name="Orange Juice",
        category="Beverages",
        pack_size={"value": 1.0, "unit": "L"},
        mrp=120.0,
        ingredients=["Orange juice"],
        attributes={},
        identifiers={},
    )

    # Fake validation responses.
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "decision": "AUTO_APPROVE",
    }

    evidence_result = {
        "supported_fields": [],
        "unsupported_fields": [],
    }

    # The normalizer must create a file because the endpoint
    # subsequently opens/checks the normalized image path.
    def fake_normalize_image(input_path, output_path):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_bytes(b"fake normalized image")

    with (
        patch(
            "backend.app.main.ImageService.normalize_image",
            side_effect=fake_normalize_image,
        ),
        patch(
            "backend.app.main.ocr_services.extract_text",
            return_value=[{"text": "Acme Orange Juice 1 L MRP 120"}],
        ),
        patch(
            "backend.app.main.product_extraction_service.extract_product",
            return_value=sample_product,
        ),
        patch(
            "backend.app.main.normalize_product_attributes",
            side_effect=lambda attributes: attributes,
        ),
        patch(
            "backend.app.main.validation_service.validate",
        ) as mock_validate,
        patch(
            "backend.app.main.evidence_validation_services.validate",
        ) as mock_evidence_validate,
    ):
        mock_validate.return_value.model_dump.return_value = validation_result
        mock_evidence_validate.return_value.model_dump.return_value = (
            evidence_result
        )

        files = [
            (
                "photos",
                ("front.jpg", b"fake image bytes", "image/jpeg"),
            )
        ]

        response = client.post("/api/products/extract", files=files)

    assert response.status_code == 200

    data = response.json()

    assert data["image_count"] == 1
    assert data["product_info"]["brand"] == "Acme"
    assert data["product_info"]["product_name"] == "Orange Juice"
    assert data["product_info"]["category"] == "Beverages"
    assert data["product_info"]["pack_size"]["value"] == 1.0
    assert data["product_info"]["mrp"] == 120.0

    assert data["validation"] == validation_result
    assert data["evidence_Validation"] == evidence_result

    mock_validate.assert_called_once()
    mock_evidence_validate.assert_called_once()