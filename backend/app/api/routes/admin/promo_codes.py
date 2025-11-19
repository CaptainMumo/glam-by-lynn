"""Admin promo code management routes."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.promo_code import (
    PromoCodeCreate,
    PromoCodeListResponse,
    PromoCodeResponse,
    PromoCodeUpdate,
    PromoCodeValidationRequest,
    PromoCodeValidationResponse,
)
from app.services import promo_code_service

router = APIRouter(tags=["Admin Promo Codes"])


@router.get(
    "/admin/promo-codes",
    response_model=PromoCodeListResponse,
    summary="List all promo codes (admin only)",
)
def list_promo_codes(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of records to return"),
    is_active: Optional[bool] = Query(None, alias="isActive", description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search by code or description"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get all promo codes.

    Admin only. Supports pagination and filtering by active status and search term.
    """
    promo_codes, total = promo_code_service.get_all_promo_codes(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        search=search,
    )

    # Add computed fields
    items = []
    for pc in promo_codes:
        pc_dict = {
            "id": pc.id,
            "code": pc.code,
            "description": pc.description,
            "discountType": pc.discount_type,
            "discountValue": pc.discount_value,
            "minOrderAmount": pc.min_order_amount,
            "maxDiscountAmount": pc.max_discount_amount,
            "usageLimit": pc.usage_limit,
            "usageCount": pc.usage_count,
            "validFrom": pc.valid_from,
            "validUntil": pc.valid_until,
            "isActive": pc.is_active,
            "isExpired": promo_code_service.is_expired(pc),
            "isUsageExhausted": promo_code_service.is_usage_exhausted(pc),
            "createdAt": pc.created_at,
            "updatedAt": pc.updated_at,
        }
        items.append(PromoCodeResponse(**pc_dict))

    return PromoCodeListResponse(items=items, total=total)


@router.get(
    "/admin/promo-codes/{promo_code_id}",
    response_model=PromoCodeResponse,
    summary="Get promo code by ID (admin only)",
)
def get_promo_code(
    promo_code_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get a single promo code by ID.

    Admin only.
    """
    promo_code = promo_code_service.get_promo_code_by_id(db=db, promo_code_id=promo_code_id)
    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Promo code with ID {promo_code_id} not found",
        )

    # Add computed fields
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

    return PromoCodeResponse(**pc_dict)


@router.post(
    "/admin/promo-codes",
    response_model=PromoCodeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create promo code (admin only)",
)
def create_promo_code(
    promo_code_data: PromoCodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Create a new promo code.

    Admin only. Requires code, discount type, and discount value.
    """
    # Check if code already exists
    existing = promo_code_service.get_promo_code_by_code(db=db, code=promo_code_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Promo code '{promo_code_data.code}' already exists",
        )

    promo_code = promo_code_service.create_promo_code(
        db=db,
        code=promo_code_data.code,
        description=promo_code_data.description,
        discount_type=promo_code_data.discount_type,
        discount_value=promo_code_data.discount_value,
        min_order_amount=promo_code_data.min_order_amount,
        max_discount_amount=promo_code_data.max_discount_amount,
        usage_limit=promo_code_data.usage_limit,
        valid_from=promo_code_data.valid_from,
        valid_until=promo_code_data.valid_until,
        is_active=promo_code_data.is_active,
    )

    # Add computed fields
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

    return PromoCodeResponse(**pc_dict)


@router.put(
    "/admin/promo-codes/{promo_code_id}",
    response_model=PromoCodeResponse,
    summary="Update promo code (admin only)",
)
def update_promo_code(
    promo_code_id: UUID,
    promo_code_data: PromoCodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Update a promo code.

    Admin only. All fields are optional for partial updates.
    """
    # If updating code, check it doesn't conflict
    if promo_code_data.code:
        existing = promo_code_service.get_promo_code_by_code(db=db, code=promo_code_data.code)
        if existing and existing.id != promo_code_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Promo code '{promo_code_data.code}' already exists",
            )

    promo_code = promo_code_service.update_promo_code(
        db=db,
        promo_code_id=promo_code_id,
        code=promo_code_data.code,
        description=promo_code_data.description,
        discount_type=promo_code_data.discount_type,
        discount_value=promo_code_data.discount_value,
        min_order_amount=promo_code_data.min_order_amount,
        max_discount_amount=promo_code_data.max_discount_amount,
        usage_limit=promo_code_data.usage_limit,
        valid_from=promo_code_data.valid_from,
        valid_until=promo_code_data.valid_until,
        is_active=promo_code_data.is_active,
    )

    if not promo_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Promo code with ID {promo_code_id} not found",
        )

    # Add computed fields
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

    return PromoCodeResponse(**pc_dict)


@router.delete(
    "/admin/promo-codes/{promo_code_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete promo code (admin only)",
)
def delete_promo_code(
    promo_code_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Delete a promo code.

    Admin only.
    """
    success = promo_code_service.delete_promo_code(db=db, promo_code_id=promo_code_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Promo code with ID {promo_code_id} not found",
        )

    return None


@router.post(
    "/admin/promo-codes/validate",
    response_model=PromoCodeValidationResponse,
    summary="Validate promo code (admin only)",
)
def validate_promo_code(
    validation_data: PromoCodeValidationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Validate a promo code and calculate discount.

    Admin only. Used for testing promo codes.
    """
    is_valid, message, discount_amount, promo_code = promo_code_service.validate_promo_code(
        db=db,
        code=validation_data.code,
        order_amount=validation_data.order_amount,
    )

    promo_code_response = None
    if promo_code:
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
