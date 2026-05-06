import enum
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARSING = "PARSING"
    RUNNING_AGENTS = "RUNNING_AGENTS"
    AGGREGATING = "AGGREGATING"
    BUILDING_PDF = "BUILDING_PDF"
    DONE = "DONE"
    FAILED = "FAILED"


class DocumentType(str, enum.Enum):
    FINANCIAL_REPORT = "financial_report"
    WEBSITE_FANPAGE = "website_fanpage"
    CATALOGUE_BROCHURE = "catalogue_brochure"
    COMPANY_PROFILE = "company_profile"
    BUSINESS_PLAN = "business_plan"
    CEO_CV = "ceo_cv"
    CRM_EXPORT = "crm_export"
    ACCOUNTING_EXPORT = "accounting_export"
    ERP_EXPORT = "erp_export"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------


class UploadResponse(BaseModel):
    report_id: UUID
    job_id: str
    message: str = "Valuation pipeline enqueued successfully"
    document_count: int


# ---------------------------------------------------------------------------
# Job status
# ---------------------------------------------------------------------------


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress_pct: int = Field(ge=0, le=100)
    message: str
    pdf_url: Optional[str] = None
    error_message: Optional[str] = None


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


class DocumentOut(BaseModel):
    id: UUID
    filename: str
    doc_type: DocumentType
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportListItem(BaseModel):
    id: UUID
    company_name: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    pdf_url: Optional[str] = None

    model_config = {"from_attributes": True}


class ReportDetail(BaseModel):
    id: UUID
    company_name: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    pdf_url: Optional[str] = None
    pdf_download_url: Optional[str] = None  # signed URL
    error_message: Optional[str] = None
    job_id: str
    documents: list[DocumentOut] = []

    model_config = {"from_attributes": True}


class PaginatedReports(BaseModel):
    items: list[ReportListItem]
    total: int
    page: int
    page_size: int
    pages: int


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: datetime

    model_config = {"from_attributes": True}
