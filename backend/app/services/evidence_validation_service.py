import re 
from pydantic import BaseModel,Field
from typing import Literal
from backend.app.schemas.product import Product
import unicodedata
from typing import LiteralString  
  
class FieldEvidence(BaseModel):
    field:str
    value:str|None = None
    status :Literal[
        "SUPPORTED",
        "NOT_FOUND",
        "CONFLICT",
    ]
    matched_text:list[str]=Field(default_factory=list)

class EvidenceValidationResult(BaseModel):
    supported_fields: list[FieldEvidence] = Field(
        default_factory=list
    )
    unsupported_fields: list[FieldEvidence] = Field(
        default_factory=list
    )
def normalize_text(text:str)->str:
    text = unicodedata.normalize("NFKD",text)
    text = " ".join(char for char in text 
                    if not unicodedata.combining(char))
    text = text.casefold()
    return re.sub(r"\s+"," ", text).strip()
def product_name_is_supported(product_name:str,normalized_ocr:str)->bool:
    normalized_name = normalize_text(product_name)
    normalized_words = normalized_name.split()
    if not normalized_words:
        return False
    if normalized_name in normalized_ocr:
        return True
    return all(
          re.search(r"\b" + re.escape(word) + r"\b", normalized_ocr)
        for word in normalized_words
    )
    
class EvidenceValidationService:
        
    def validate(self,product:Product,ocr_text:str,)->EvidenceValidationResult:
        
        supported = [] 
        unsupported = [] 
        
        normalized_ocr = normalize_text(ocr_text)
        print("\n--- RAW OCR TEXT ---")
        print(ocr_text)

        print("\n--- NORMALIZED OCR TEXT ---")
        print(normalized_ocr.strip())
        
        fields_to_check = {
            "brand":product.brand,
            "product_name":product.product_name,
            "mrp":(
                str(product.mrp)
                if product.mrp is not None
                else None
            ),
        }
        
        for field,value in fields_to_check.items():
            print(f"checking field:{field},value:{value}")
            if value is None or not str(value).strip():
                continue
            value_text = str(value).strip()
            normalized_text = normalize_text(value_text)
            print(normalized_text)
            if field=="product_name":
                is_supported = product_name_is_supported(value_text,normalized_ocr)
            else:
                is_supported= normalized_text in normalized_ocr
            if is_supported:
                supported.append(
                    FieldEvidence(
                    field = field,
                    value=value_text,
                    status="SUPPORTED",
                    matched_text=[value_text],
                )
                )
            else:
                 unsupported.append(
                    FieldEvidence(
                        field=field,
                        value=value_text,
                        status="NOT_FOUND",
                    )
                )
        return EvidenceValidationResult(
            supported_fields=supported,unsupported_fields=unsupported,
            )