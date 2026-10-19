import re 
from pydantic import BaseModel,Field
from typing import Literal
from backend.app.schemas.product import Product

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
class EvidenceValidationService:
    def validate(self,product:Product,ocr_text:str,)->EvidenceValidationResult:
        
        supported = [] 
        unsupported = [] 
        
        normalized_ocr = re.sub(r"\s+"," ",ocr_text).casefold()
        
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
            if value is None or not str(value).strip():
                continue
            value_text = str(value).strip()
            normalized_text = re.sub(r"\s+"," ",value_text).casefold()
            
            if normalized_text in normalized_ocr:
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