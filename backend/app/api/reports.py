"""Report management endpoints."""

import logging
import math

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.report import Document, Report
from app.models.user import User
from app.schemas.api import (
    DocumentOut,
    PaginatedReports,
    ReportDetail,
    ReportListItem,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


# ── GET /api/reports/ ─────────────────────────────────────────────────────────

@router.get("/", response_model=PaginatedReports)
async def list_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedReports:
    base_where = Report.user_id == str(current_user.id)

    total_result = await db.execute(
        select(func.count()).select_from(Report).where(base_where)
    )
    total = total_result.scalar_one()

    result = await db.execute(
        select(Report)
        .where(base_where)
        .order_by(Report.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    reports = list(result.scalars().all())

    return PaginatedReports(
        items=[ReportListItem.model_validate(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, math.ceil(total / page_size)),
    )


# ── GET /api/reports/{report_id} ─────────────────────────────────────────────

@router.get("/{report_id}", response_model=ReportDetail)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReportDetail:
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == str(current_user.id))
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found.")

    doc_result = await db.execute(
        select(Document).where(Document.report_id == report_id)
    )
    documents = list(doc_result.scalars().all())

    detail = ReportDetail.model_validate(report)
    detail.documents = [DocumentOut.model_validate(d) for d in documents]
    detail.pdf_download_url = report.pdf_url
    return detail


# ── GET /api/reports/{report_id}/pdf ─────────────────────────────────────────

@router.get("/{report_id}/pdf", include_in_schema=False)
async def download_pdf(
    report_id: str,
    token: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Public download endpoint — authenticated via download_token in URL."""
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()

    if report is None or report.download_token != token or report.pdf_bytes is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "PDF not found or token invalid.")

    company_safe = "".join(
        c if c.isalnum() or c in "-_ " else "_"
        for c in (report.company_name or "report")
    ).strip()[:50]

    return Response(
        content=report.pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="ValuAI_{company_safe}.pdf"',
            "Content-Length": str(len(report.pdf_bytes)),
        },
    )


# ── DELETE /api/reports/{report_id} ──────────────────────────────────────────

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(Report).where(Report.id == report_id, Report.user_id == str(current_user.id))
    )
    report = result.scalar_one_or_none()
    if report is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Report not found.")

    await db.delete(report)
    await db.commit()
    logger.info("Deleted report %s by user %s", report_id, current_user.id)
