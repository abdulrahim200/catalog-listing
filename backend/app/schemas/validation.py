from typing import Literal
from pydantic import BaseModel,Field

class ValidationIssue(BaseModel):
    field:str
    code:str
    message:str
    severity:Literal["error","warning"]

class ValidationResult(BaseModel):
    valid:bool
    error:list[ValidationIssue]=Field(default_factory = list)
    warning:list[ValidationIssue]=Field(default_factory = list)
    decision:Literal["AUTO_APPROVE","REVIEW","REJECT"]="REVIEW"

