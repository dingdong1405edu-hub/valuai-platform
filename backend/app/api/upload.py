"""
File upload endpoint — Supabase-free version.
Files are parsed immediately during upload; extracted text is stored in DB.
"""

import asyncio
import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import get_settings
from app.database import get_db
from app.models.report import Document, Report
from app.models.user import User
from app.parsers import parse_document
from app.schemas.api import DocumentType, JobStatus, UploadResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])
settings = get_settings()

ALLOWED_EXTENSIONS = {
    ".pdf", ".xlsx", ".xls", ".docx", ".doc",
    ".txt", ".csv",
}


def _validate_extension(filename: str) -> None:
    import os
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type '{ext}' not supported. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload documents and start valuation pipeline",
)
async def upload_documents(
    company_name: Annotated[str, Form(min_length=1, max_length=500)],
    files: Annotated[list[UploadFile], File()],
    doc_types: Annotated[list[str], Form()],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    if not files:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "At least one file required.")
    if len(files) > settings.MAX_FILES_PER_REPORT:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            f"Max {settings.MAX_FILES_PER_REPORT} files per report.")
    if len(doc_types) != len(files):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Length of doc_types must match files.")

    valid_types = {dt.value for dt in DocumentType}
    for dt in doc_types:
        if dt not in valid_types:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                f"Invalid doc_type '{dt}'.")

    # Read and validate all files
    file_data: list[tuple[str, bytes, str]] = []
    for upload_file, doc_type in zip(files, doc_types):
        filename = upload_file.filename or "unnamed"
        _validate_extension(filename)
        content = await upload_file.read()
        if len(content) > settings.max_file_size_bytes:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                                f"File '{filename}' exceeds {settings.MAX_FILE_SIZE_MB}MB.")
        if len(content) == 0:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                f"File '{filename}' is empty.")
        file_data.append((filename, content, doc_type))

    # Parse all files concurrently (CPU-bound → run in thread pool)
    async def _parse(filename: str, content: bytes) -> str:
        try:
            return await asyncio.to_thread(
                lambda: asyncio.run(parse_document(filename, content))
            )
        except Exception as e:
            logger.warning("Parse failed for %s: %s", filename, e)
            return f"[Parse error for {filename}: {e}]"

    texts = await asyncio.gather(*[_parse(fn, c) for fn, c, _ in file_data])

    # Create Report
    job_id = str(uuid.uuid4())
    report = Report(
        user_id=str(current_user.id),
        company_name=company_name,
        status=JobStatus.PENDING.value,
        job_id=job_id,
    )
    db.add(report)
    await db.flush()
    await db.refresh(report)

    # Create Document records with extracted text
    for (filename, _content, doc_type), extracted_text in zip(file_data, texts):
        doc = Document(
            report_id=report.id,
            filename=filename,
            doc_type=doc_type,
            storage_path=f"local:{report.id}/{filename}",
            extracted_text=extracted_text,
        )
        db.add(doc)

    await db.flush()

    # Enqueue Celery task
    from app.tasks.valuation import run_valuation_pipeline  # noqa: PLC0415
    task = run_valuation_pipeline.apply_async(
        kwargs={"report_id": str(report.id)},
        task_id=job_id,
    )
    actual_task_id = task.id
    if actual_task_id != job_id:
        report.job_id = actual_task_id
        await db.flush()

    await db.commit()

    logger.info("Pipeline enqueued: report=%s job=%s user=%s",
                report.id, report.job_id, current_user.email)

    return UploadResponse(
        report_id=report.id,
        job_id=report.job_id,
        document_count=len(file_data),
    )
