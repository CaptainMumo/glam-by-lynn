"""
Service Package schemas for request/response validation
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator


class ServicePackageBase(BaseModel):
    """Base service package schema"""
    package_type: str = Field(
        ...,
        description="Package type: 'bridal_large', 'bridal_small', 'bride_only', 'regular', 'classes'"
    )
    name: str = Field(..., min_length=1, max_length=255, description="Package name")
    description: Optional[str] = Field(None, description="Package description")
    base_bride_price: Optional[Decimal] = Field(None, ge=0, description="Base price for bride")
    base_maid_price: Optional[Decimal] = Field(None, ge=0, description="Base price per maid/bridesmaid")
    base_mother_price: Optional[Decimal] = Field(None, ge=0, description="Base price for mother")
    base_other_price: Optional[Decimal] = Field(None, ge=0, description="Base price for other attendees")
    max_maids: Optional[int] = Field(None, gt=0, description="Maximum number of maids")
    min_maids: int = Field(0, ge=0, description="Minimum number of maids")
    includes_facial: bool = Field(False, description="Whether package includes facial")
    duration_minutes: Optional[int] = Field(None, gt=0, description="Service duration in minutes")
    is_active: bool = Field(True, description="Whether package is active")
    display_order: int = Field(0, ge=0, description="Display order (lower = earlier)")

    @field_validator('package_type')
    @classmethod
    def validate_package_type(cls, v: str) -> str:
        """Validate package type"""
        v = v.strip().lower()
        valid_types = ['bridal_large', 'bridal_small', 'bride_only', 'regular', 'classes']
        if v not in valid_types:
            raise ValueError(f"Package type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean package name"""
        v = v.strip()
        if not v:
            raise ValueError('Package name cannot be empty')
        return v

    @model_validator(mode='after')
    def validate_maid_range(self):
        """Validate max_maids >= min_maids"""
        if self.max_maids is not None and self.min_maids is not None:
            if self.max_maids < self.min_maids:
                raise ValueError('max_maids must be greater than or equal to min_maids')
        return self


class ServicePackageCreate(ServicePackageBase):
    """Schema for creating a service package"""
    pass


class ServicePackageUpdate(BaseModel):
    """Schema for updating a service package (all fields optional)"""
    package_type: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    base_bride_price: Optional[Decimal] = Field(None, ge=0)
    base_maid_price: Optional[Decimal] = Field(None, ge=0)
    base_mother_price: Optional[Decimal] = Field(None, ge=0)
    base_other_price: Optional[Decimal] = Field(None, ge=0)
    max_maids: Optional[int] = Field(None, gt=0)
    min_maids: Optional[int] = Field(None, ge=0)
    includes_facial: Optional[bool] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)

    @field_validator('package_type')
    @classmethod
    def validate_package_type(cls, v: Optional[str]) -> Optional[str]:
        """Validate package type if provided"""
        if v is not None:
            v = v.strip().lower()
            valid_types = ['bridal_large', 'bridal_small', 'bride_only', 'regular', 'classes']
            if v not in valid_types:
                raise ValueError(f"Package type must be one of: {', '.join(valid_types)}")
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate and clean package name if provided"""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError('Package name cannot be empty')
        return v


class ServicePackageResponse(ServicePackageBase):
    """Schema for service package response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ServicePackageListResponse(BaseModel):
    """Schema for paginated service package list response"""
    items: list[ServicePackageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
