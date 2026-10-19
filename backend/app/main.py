from typing import Annotated
from starlette.concurrency import run_in_threadpool
from fastapi import FastAPI,UploadFile,File,HTTPException
from pathlib import Path
import os
import traceback
from uuid import uuid4
from backend.app.services.ocr_services import OCRService
from backend.app.services.image_services import ImageService
from backend.app.services.product_extraction_service import ProductExtractionService
from backend.app.services.validation_service import ValidationService
from backend.app.services.evidence_validation_service import EvidenceValidationService


app = FastAPI(title="catalog-lister",description="AI-powered product catalog automation system",version="0.1.0")

ocr_services = OCRService()
product_extraction_service  = ProductExtractionService()
validation_service = ValidationService()
evidence_validation_services = EvidenceValidationService()
@app.get("/")
def root():
    return {
        "message":"Catalog-lister is running"
    }
@app.post(
    "/api/products/extract",
    openapi_extra={
        "requestBody": {
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["photos"],
                        "properties": {
                            "photos": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "format": "binary",
                                },
                            }
                        },
                    }
                }
            }
        }
    },
)
async def upload_photo(photos:list[UploadFile] = File(...,description="Upload 2 to 3 images at once",),):
    
    if not photos:
        raise HTTPException(
            status_code=400,detail="Upload atleast one image"
        ) 
    if len(photos) > 3:
        raise HTTPException(
            status_code=400,
            detail="Upload a maximum of three images per product.",
        )
  
    upload_dir = Path("data/raw")
    upload_dir.mkdir(parents=True,exist_ok=True)
    
    submission_dir = upload_dir / str(uuid4())
    submission_dir.mkdir(parents=True,exist_ok=True)
    all_ocr_results = []
    evidence_sections = []
    try:
        for index,photo in enumerate(photos,start =1):
            filename = Path(photo.filename or f"image_{index}").name

            contents = await photo.read()
    
            if not contents:
                raise HTTPException(
                    status_code=400,
                    detail="File uploaded is Empty"   
                )
            original_path = submission_dir / f"{index}_{filename}"
            with open(original_path,"wb") as file:
                file.write(contents)
    
            normalized_path = (
                submission_dir / f"{index}_normalized.jpg"
            )
            if not original_path.exists():
                return {
                    "error":"Image not saved"
                }

            ImageService.normalize_image(str(original_path), str(normalized_path))
        
            absolute_path = normalized_path.resolve()
    
            print(f"File size: {absolute_path.stat().st_size} bytes")
        
            extracted_text = ocr_services.extract_text(str(absolute_path))
            
            all_ocr_results.append({
                "image_number":index,
                "ocr":extracted_text,
                "filename":filename
            })
    
            image_text = "\n".join(item["text"] for item in extracted_text)
            evidence_sections.append(f"IMAGE_{index}:{filename}\n{image_text}")
            
        combined_ocr_text = "\n\n".join(evidence_sections)
        if not combined_ocr_text.strip():
            raise HTTPException(
                status_code=422,
                detail = "No text could be extracted from the images"   
                )
        try:
            product = product_extraction_service.extract_product(ocr_text=combined_ocr_text)
        except Exception:
            traceback.print_exc()
            raise
        validation = validation_service.validate(product=product)
        evi_validation = evidence_validation_services.validate(product=product,ocr_text=combined_ocr_text)
        return {
            "image_count":len(photos),
            "product_info":product.model_dump(),
            "validation":validation.model_dump(),
            "evidence_Validation":evi_validation.model_dump(),
            }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
        status_code=500,
        detail="Product extraction failed.Check Server Logs."
        )from e
    finally:
        for photo in photos:
            await photo.close()
