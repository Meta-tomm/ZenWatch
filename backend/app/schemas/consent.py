from typing import Optional, Literal, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


ConsentType = Literal['terms', 'privacy', 'marketing', 'analytics']
ExportStatus = Literal['pending', 'processing', 'completed', 'expired']


class ConsentCreate(BaseModel):
    """Schema for recording a consent decision"""
    consent_type: ConsentType
    consented: bool


class ConsentUpdate(BaseModel):
    """Schema for updating/withdrawing consent"""
    consented: bool


class ConsentResponse(BaseModel):
    """Consent record response"""
    id: int
    consent_type: ConsentType
    consented: bool
    consented_at: datetime
    withdrawn_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConsentStatusResponse(BaseModel):
    """Current consent status for all types"""
    terms: Optional[ConsentResponse] = None
    privacy: Optional[ConsentResponse] = None
    marketing: Optional[ConsentResponse] = None
    analytics: Optional[ConsentResponse] = None


class DataExportRequestCreate(BaseModel):
    """Request for GDPR data export"""
    pass


class DataExportRequestResponse(BaseModel):
    """Data export request response"""
    id: int
    status: ExportStatus
    file_url: Optional[str] = None
    requested_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DataDeletionRequest(BaseModel):
    """Request for GDPR data deletion (right to be forgotten)"""
    confirm_deletion: bool
    password: Optional[str] = None


class UserDataExport(BaseModel):
    """Exported user data structure"""
    user: dict
    articles_read: List[dict]
    videos_watched: List[dict]
    comments: List[dict]
    keywords: List[dict]
    consents: List[dict]
    export_date: datetime
