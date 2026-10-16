from pydantic import BaseModel,Field
from typing import Optional,Any

class Identifiers(BaseModel):
    barcode:Optional[str] = None
    sku:Optional[str] = None

class Packsize(BaseModel):
    value:Optional[int] = None
    unit:Optional[str] = None
    
class Product(BaseModel):
    brand:Optional[str]=None
    product_name:Optional[str]=None
    category:Optional[str]=None
    
    pack_size:Packsize = Field(default_factory = Packsize)
    mrp:Optional[float] = None
    
    ingredients:list[str] = Field(default_factory=list)
    description:Optional[str] = None
    
    attributes:dict[str,Any] = Field(default_factory=dict)
    
    identifiers:Identifiers = Field(default_factory=Identifiers)
