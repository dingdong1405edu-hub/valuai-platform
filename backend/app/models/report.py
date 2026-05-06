import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.schemas.api import DocumentType, JobStatus


class Report(Base):
    """Top-level valuation report job, one per company analysis request."""

    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=JobStatus.PENDING.value,
        index=True,
    )
    job_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Celery task ID returned when the pipeline is enqueued",
    )
    pdf_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    pdf_bytes: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    download_token: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable error description when status=FAILED",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="report",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Report id={self.id} company={self.company_name!r} status={self.status}>"


class Document(Base):
    """A single uploaded file attached to a Report."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    report_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Original filename as uploaded by the user",
    )
    doc_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=DocumentType.OTHER.value,
        comment="Semantic category of this document",
    )
    storage_path: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
        comment="Path / key within the Supabase Storage bucket",
    )
    extracted_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Full text extracted from the document by the parser",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    report: Mapped["Report"] = relationship("Report", back_populates="documents")

    def __repr__(self) -> str:
        return (
            f"<Document id={self.id} filename={self.filename!r} type={self.doc_type}>"
        )
