from dotenv import load_dotenv
from openai import OpenAI
import os

from backend.app.schemas.product import Product

load_dotenv()

class ProductExtractionService:
    
    def __init__(self):
        
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                " OPENAI_API_KEY isnt configured"
            )
        self.client = OpenAI(api_key=api_key)
    def extract_product(self,ocr_text:str)->Product:
        prompt = f"""
        You are an AI product catalog extraction system.

Your task is to extract structured product information
from supplier OCR text.

IMPORTANT RULES:

1. Extract ONLY information supported by the OCR text.
2. Never invent or guess missing information.
3. If information is unavailable, return null.
4. Do not infer a brand or product name unless supported.
5. Keep category information as specific as the evidence allows.
6. Put category-specific properties inside "attributes".
7. Return only the requested JSON structure.

OCR TEXT:
----------------
{ocr_text}
----------------

Return this structure:

{{
    "brand": null,
    "product_name": null,
    "category": null,

    "pack_size": {{
        "value": null,
        "unit": null
    }},

    "mrp": null,

    "description": null,

    "ingredients": [],

    "attributes": {{}},

    "identifiers": {{
        "barcode": null,
        "sku": null
    }}
}}
        """
        response = self.client.responses.create(
            model = "gpt-5.5",input = prompt
    )
        return Product.model_validate_json(response.output_text)
    
        


