from starlette.concurrency import run_in_threadpool
from fastapi import FastAPI,UploadFile,File,HTTPException
import os
from backend.app.services.ocr_services import OCRService
from backend.app.services.image_services import ImageService
from backend.app.services.product_extraction_service import ProductExtractionService
from backend.app.services.validation_service import ValidationService
from pathlib import Path
import traceback

app = FastAPI(title="catalog-lister",description="AI-powered product catalog automation system",version="0.1.0")
ocr_services = OCRService()
product_extraction_service  = ProductExtractionService()
validation_service = ValidationService()
@app.get("/")
def root():
    return {
        "message":"Catalog-lister is running"
    }
@app.post("/api/products/extract")
async def upload_photo(photo:UploadFile = File(...)):
    upload_dir = Path("data/raw")
    upload_dir.mkdir(parents=True,exist_ok=True)
    
    filename = Path(photo.filename or "upload").name
    original_path = upload_dir / filename
    try:
        contents = await photo.read()
    
        if not contents:
            raise HTTPException(
                status_code=400,
                detail="File uploaded is Empty"   
            )
        
    
        with open(original_path,"wb") as file:
            file.write(contents)
    
        normalized_path = upload_dir / f"normalized_{filename}.jpg"
        if not original_path.exists():
            return {
                "error":"Image not saved"
            }

        ImageService.normalize_image(str(original_path), str(normalized_path))
        
        absolute_path = normalized_path.resolve()
    
        print(f"File size: {absolute_path.stat().st_size} bytes")
        
        extracted_text = ocr_services.extract_text(str(absolute_path))
    
        ocr_text = "\n".join(item["text"] for item in extracted_text)
        try:
            product = product_extraction_service.extract_product(ocr_text=ocr_text)
        except Exception:
            traceback.print_exc()
            raise
        validation = validation_service.validate(product=product)
        return {
            "filename":photo.filename,
            "contenttype":photo.content_type,
            "product_info":product.model_dump(),
            "validation":validation.model_dump()
            }
    except HTTPException:
        raise
    except Exception as e:
        print("product extraction failed.")
        raise HTTPException(
        status_code=500,
        detail="Product extraction failed.Check Server Logs."
        )from e
    finally:
        await photo.close()
