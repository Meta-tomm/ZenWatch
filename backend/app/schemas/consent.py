"""GDPR consent and data export schemas"""

from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


ConsentType = Literal["terms", "privacy", "marketing", "analytics"]
ExportStatus = Literal["pending", "processing", "completed", "failed", "expired"]


class ConsentCreate(BaseModel):
    """Schema for recording user consent"""

    consent_type: ConsentType
    consented: bool
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None


class ConsentUpdate(BaseModel):
    """Schema for updating/withdrawing consent"""

    consented: bool
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None


class ConsentResponse(BaseModel):
    """Schema for consent API response"""

    id: int
    consent_type: ConsentType
    consented: bool
    consented_at: datetime
    withdrawn_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConsentStatusResponse(BaseModel):
    """Schema for all user consent statuses"""

    terms: bool = False
    privacy: bool = False
    marketing: bool = False
    analytics: bool = False
    last_updated: Optional[datetime] = None


class DataExportRequestCreate(BaseModel):
    """Schema for requesting data export (GDPR right to data portability)"""

    pass


class DataExportResponse(BaseModel):
    """Schema for data export request response"""

    id: int
    status: ExportStatus
    file_url: Optional[str] = None
    requested_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DataExportListResponse(BaseModel):
    """Schema for list of data export requests"""

    exports: List[DataExportResponse]
    total: int


class AccountDeletionRequest(BaseModel):
    """Schema for account deletion request (GDPR right to erasure)"""

    password: str = Field(..., min_length=1)
    confirmation: Literal["DELETE MY ACCOUNT"]


class AccountDeletionResponse(BaseModel):
    """Schema for account deletion confirmation"""

    message: str = "Account deletion initiated"
    deletion_scheduled_at: datetime
