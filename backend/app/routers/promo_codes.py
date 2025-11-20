"""Public promo code routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.promo_code import (
    PromoCodeValidationRequest,
    PromoCodeValidationResponse,
)
from app.services import promo_code_service

router = APIRouter(prefix="/promo-codes", tags=["Promo Codes"])


@router.post("/validate", response_model=PromoCodeValidationResponse)
async def validate_promo_code(
    validation_data: PromoCodeValidationRequest,
    db: Session = Depends(get_db),
):
    """
    Validate a promo code and calculate discount (public).

    This endpoint is used during checkout to validate promo codes.

    **Request:**
    - code: Promo code string (case-insensitive)
    - order_amount: Order total amount before discount

    **Validation checks:**
    - Code exists
    - Code is active
    - Code is within valid date range
    - Usage limit not exceeded
    - Order amount meets minimum requirement

    **Response:**
    - valid: Whether the code is valid
    - message: Validation message or error description
    - discountAmount: Calculated discount (if valid)
    - promoCode: Full promo code details (if valid)
    """
    is_valid, message, discount_amount, promo_code = promo_code_service.validate_promo_code(
        db=db,
        code=validation_data.code,
        order_amount=validation_data.order_amount,
    )

    # For public endpoint, only return promo code details if valid
    # Don't expose internal details for invalid codes
    promo_code_response = None
    if is_valid and promo_code:
        from app.schemas.promo_code import PromoCodeResponse

        pc_dict = {
            "id": promo_code.id,
            "code": promo_code.code,
            "description": promo_code.description,
            "discountType": promo_code.discount_type,
            "discountValue": promo_code.discount_value,
            "minOrderAmount": promo_code.min_order_amount,
            "maxDiscountAmount": promo_code.max_discount_amount,
            "usageLimit": promo_code.usage_limit,
            "usageCount": promo_code.usage_count,
            "validFrom": promo_code.valid_from,
            "validUntil": promo_code.valid_until,
            "isActive": promo_code.is_active,
            "isExpired": promo_code_service.is_expired(promo_code),
            "isUsageExhausted": promo_code_service.is_usage_exhausted(promo_code),
            "createdAt": promo_code.created_at,
            "updatedAt": promo_code.updated_at,
        }
        promo_code_response = PromoCodeResponse(**pc_dict)

    return PromoCodeValidationResponse(
        valid=is_valid,
        message=message,
        discountAmount=discount_amount,
        promoCode=promo_code_response,
    )
