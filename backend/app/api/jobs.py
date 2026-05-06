"""
Job status polling endpoint.

GET /api/jobs/{job_id}/status — returns current pipeline status and progress.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models.report import Report
from app.models.user import User
from app.schemas.api import JobStatus, JobStatusResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# ---------------------------------------------------------------------------
# Progress mapping: status → estimated percentage complete
# ---------------------------------------------------------------------------

_STATUS_PROGRESS: dict[str, int] = {
    JobStatus.PENDING.value: 0,
    JobStatus.PARSING.value: 10,
    JobStatus.RUNNING_AGENTS.value: 40,
    JobStatus.AGGREGATING.value: 80,
    JobStatus.BUILDING_PDF.value: 90,
    JobStatus.DONE.value: 100,
    JobStatus.FAILED.value: 0,
}

_STATUS_MESSAGES: dict[str, str] = {
    JobStatus.PENDING.value: "Waiting in queue…",
    JobStatus.PARSING.value: "Extracting text from uploaded documents…",
    JobStatus.RUNNING_AGENTS.value: "Running AI analysis agents…",
    JobStatus.AGGREGATING.value: "Aggregating analysis results…",
    JobStatus.BUILDING_PDF.value: "Generating PDF report…",
    JobStatus.DONE.value: "Valuation report is ready.",
    JobStatus.FAILED.value: "Pipeline failed. See error details.",
}


# ---------------------------------------------------------------------------
# GET /api/jobs/{job_id}/status
# ---------------------------------------------------------------------------


@router.get(
    "/{job_id}/status",
    response_model=JobStatusResponse,
    summary="Poll the status of a valuation pipeline job",
)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobStatusResponse:
    # Lookup the report that owns this job_id — ensure it belongs to the caller
    result = await db.execute(
        select(Report).where(
            Report.job_id == job_id,
            Report.user_id == current_user.id,
        )
    )
    report = result.scalar_one_or_none()

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No job with id '{job_id}' found for the current user.",
        )

    current_status = report.status
    progress = _STATUS_PROGRESS.get(current_status, 0)
    message = _STATUS_MESSAGES.get(current_status, "Processing…")

    # Surface the error message in the status response when failed
    if current_status == JobStatus.FAILED.value and report.error_message:
        message = report.error_message

    return JobStatusResponse(
        job_id=job_id,
        status=current_status,  # type: ignore[arg-type]
        progress_pct=progress,
        message=message,
        pdf_url=report.pdf_url if current_status == JobStatus.DONE.value else None,
        error_message=report.error_message,
    )
