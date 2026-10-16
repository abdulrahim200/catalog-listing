from backend.app.schemas.validation import (ValidationIssue,ValidationResult)
from backend.app.schemas.product import Product

class ValidationService:
    
    def validate(self,product:Product)->ValidationResult:
        errors:list[ValidationIssue]=[]
        warnings:list[ValidationIssue]=[]
        
        if not product.product_name or product.product_name.strip():
            errors.append(
                ValidationIssue(
                    field="product_name",
                    code = "MISSING_PRODUCT_NAME",
                    message="Product name is required",
                    severity = "error"
                    
                )
            )
        if not product.brand or product.brand.strip():
            warnings.append(
                ValidationIssue(
                    field = "brand",
                    code = "MISSING_BRAND",
                    message="brand is not present",
                    severity="warning"
                )
            )
        if not product.category or not product.category.strip():
            warnings.append(
                ValidationIssue(
                    field="category",
                    code="MISSING_CATEGORY",
                    message="Product category was not identified.",
                    severity="warning",
                )
            )

        # 2. Pack-size checks
        if product.pack_size.value is None:
            warnings.append(
                ValidationIssue(
                    field="pack_size.value",
                    code="MISSING_PACK_SIZE",
                    message="Pack size was not identified.",
                    severity="warning",
                )
            )
        elif product.pack_size.value <= 0:
            errors.append(
                ValidationIssue(
                    field="pack_size.value",
                    code="INVALID_PACK_SIZE",
                    message="Pack size must be greater than zero.",
                    severity="error",
                )
            )

        if (
            product.pack_size.value is not None
            and not product.pack_size.unit
        ):
            warnings.append(
                ValidationIssue(
                    field="pack_size.unit",
                    code="MISSING_PACK_SIZE_UNIT",
                    message="Pack size unit is missing.",
                    severity="warning",
                )
            )

        # 3. MRP checks
        if product.mrp is None:
            warnings.append(
                ValidationIssue(
                    field="mrp",
                    code="MISSING_MRP",
                    message="MRP was not identified.",
                    severity="warning",
                )
            )
        elif product.mrp < 0:
            errors.append(
                ValidationIssue(
                    field="mrp",
                    code="INVALID_MRP",
                    message="MRP cannot be negative.",
                    severity="error",
                )
            )

        # 4. Initial decision policy
        if errors:
            decision = "REJECT"
        elif warnings:
            decision = "REVIEW"
        else:
            decision = "AUTO_APPROVE"

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            decision=decision,
        )
        