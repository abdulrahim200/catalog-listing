from fastapi import FastAPI,UploadFile,File

app = FastAPI(title="catalog-lister",description="AI-powered product catalog automation system",version="0.1.0")

@app.get("/")
def root():
    return {
        "message":"Catalog-lister is running"
    }

try:
    @app.post("/api/products/upload")
    def upload_photo(photo:UploadFile = File(...)):
        return {
            "filename":photo.filename,
            "contenttype":photo.content_type,
            "message":"Product image received"
        
            }
except: