# Catalog Listing

Catalog Listing is an AI-assisted product catalog extraction pipeline for product packaging and label images. The application accepts one to three product photos, normalizes them, extracts text via OCR, and uses an LLM-based extraction step to build structured product records.

This project is designed for use cases such as:

- cataloging packaged grocery or retail products
- extracting brand, product name, quantity, ingredients, and nutrition details
- validating extracted data against OCR evidence
- storing normalized product data in a database for downstream use

## Features

- Upload 1-3 product images through a FastAPI endpoint
- Preprocess and normalize uploaded images before OCR
- Extract label text from product images
- Parse product fields such as brand, category, product name, description, ingredients, and pack size
- Normalize numeric values and units (for example, `8,5 g`, `12%`, `0,19 mg`)
- Validate extracted content against OCR evidence and schema rules
- Persist structured product records to a PostgreSQL-compatible database using SQLAlchemy
- Includes a dataset helper for downloading reference product metadata from Open Food Facts

## Project structure

```text
catalog-listing/
├─ backend/
│  └─ app/
│     ├─ database.py
│     ├─ main.py
│     ├─ models.py
│     ├─ schemas/
│     │  ├─ product.py
│     │  └─ validation.py
│     └─ services/
│        ├─ evidence_validation_service.py
│        ├─ image_services.py
│        ├─ normalization_service.py
│        ├─ ocr_services.py
│        ├─ product_extraction_service.py
│        ├─ product_persisitence.py
│        └─ validation_service.py
├─ data/
│  ├─ datasets/
│  ├─ processed/
│  └─ raw/
├─ scripts/
│  └─ download_off_product.py
├─ tests/
│  └─ test_normalization.py
├─ .env.example (optional if you create one locally)
├─ create_tables.py
├─ requirements.txt
├─ check_db.py
├─ test_persistence.py
├─ README.md
└─ .gitignore
```

## Tech stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL / Postgres-compatible database
- OpenAI API for product extraction
- OCR/image-processing services via the existing pipeline
- pytest for validation tests

## Prerequisites

- Python 3.10 or newer
- A PostgreSQL database instance or compatible local database
- An OpenAI API key
- Access to the project dependencies in `requirements.txt`

## Setup

1. Clone the repository.
2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a local `.env` file in the project root and add the required environment variables:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/catalog_listing
OPENAI_API_KEY=your_openai_api_key
```

If your database uses a different driver or connection string, adjust it accordingly.

5. Create the database tables:

```bash
python create_tables.py
```

## Running the API

Start the FastAPI app with Uvicorn:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open the Swagger UI here:

```text
http://localhost:8000/docs
```

## API usage

The main ingestion endpoint is:

```http
POST /api/products/extract
```

It accepts multipart form data with a `photos` field containing one to three uploaded images.

Example using curl:

```bash
curl -X POST "http://localhost:8000/api/products/extract" \
  -F "photos=@data/raw/front.jpg" \
  -F "photos=@data/raw/ingredients.jpg"
```

The response includes:

- extracted product information
- validation results
- evidence validation results
- normalized attributes

## Data and scripts

- `data/raw/`: uploaded and raw product images
- `data/processed/`: processed outputs generated during image normalization
- `scripts/download_off_product.py`: downloads a sample product reference from Open Food Facts
- `tests/test_normalization.py`: validates normalization logic for values such as weight, percentages, and nutrition data

## Testing

Run the project tests with:

```bash
pytest
```

## Notes

This project is a prototype and an internal automation pipeline. It is useful as a foundation for product image intake, OCR-driven extraction, and structured catalog enrichment. You may need to adjust model prompts, environment variables, and database settings to match your deployment environment.

## License

No explicit license file is included in this repository. If you intend to share or distribute this project publicly, add a license that matches your usage requirements.
