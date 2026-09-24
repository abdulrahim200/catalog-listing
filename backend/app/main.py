from fastapi import FastAPI,UploadFile,File
import os
from backend.app.services.ocr_services import OCRService
from backend.app.services.image_services import ImageService
from pathlib import Path

app = FastAPI(title="catalog-lister",description="AI-powered product catalog automation system",version="0.1.0")
ocr_services = OCRService()
@app.get("/")
def root():
    return {
        "message":"Catalog-lister is running"
    }

try:
    @app.post("/api/products/upload")
    async def upload_photo(photo:UploadFile = File(...)):
        upload_dir = Path("data/raw")
        upload_dir.mkdir(parents=True,exist_ok=True)
        
        filename = Path(photo.filename or "upload").name
        original_path = upload_dir / filename
        
        contents = await photo.read()
        
        with open(original_path,"wb") as file:
            file.write(contents)
        
        normalized_path = upload_dir / "normalized.jpg"
        if not original_path.exists():
            return {
                "error":"Image not saved"
            }

        ImageService.normalize_image(str(original_path), str(normalized_path))
            
        absolute_path = normalized_path.resolve()
        
        print(f"File size: {absolute_path.stat().st_size} bytes")
        
        extracted_text = ocr_services.extract_text(str(absolute_path))
        return {
            "filename":photo.filename,
            "contenttype":photo.content_type,
            "normalized_file": str(absolute_path),
            "text":extracted_text
               }
except:
    print("upload the photo")
