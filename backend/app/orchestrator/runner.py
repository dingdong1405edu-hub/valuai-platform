"""
Valuation pipeline orchestrator.

Execution graph
---------------
  PARALLEL   → A1 CompanyProfileAgent
               A2 FinancialStatementAgent
               A3 MarketAnalysisAgent
               A4 BusinessOpsAgent
               A5 ManagementAgent
               A8 RiskAgent
  SEQUENTIAL → A6 ProjectionAgent  (needs financial + market context)
  SEQUENTIAL → A7 ValuationAgent   (needs A6 projection output)
  AGGREGATE  → combine all outputs into AggregatedReport
  BUILD_PDF  → render PDF via WeasyPrint, upload to Supabase Storage
"""

import asyncio
import logging
import traceback
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.business_ops import BusinessOpsAgent
from app.agents.company_profile import CompanyProfileAgent
from app.agents.financial_statement import FinancialStatementAgent
from app.agents.management import ManagementAgent
from app.agents.market_analysis import MarketAnalysisAgent
from app.agents.projection import ProjectionAgent
from app.agents.risk import RiskAgent
from app.agents.valuation import ValuationAgent
from app.celery_app import celery_app
from app.config import get_settings
from app.database import AsyncSessionLocal
from app.models.report import Document, Report
from app.parsers import parse_document
from app.report.aggregator import aggregate_results
from app.report.builder import build_pdf
from app.schemas.agents import (
    BusinessOpsOutput,
    CompanyProfileOutput,
    FinancialStatementOutput,
    ManagementOutput,
    MarketAnalysisOutput,
    ProjectionOutput,
    RiskOutput,
    ValuationOutput,
)
from app.schemas.api import JobStatus

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Progress milestones (approximate %)
# ---------------------------------------------------------------------------
_PROGRESS = {
    JobStatus.PARSING: 10,
    JobStatus.RUNNING_AGENTS: 20,
    JobStatus.AGGREGATING: 80,
    JobStatus.BUILDING_PDF: 88,
    JobStatus.DONE: 100,
    JobStatus.FAILED: 0,
}


# ---------------------------------------------------------------------------
# Celery entry point (sync wrapper required by Celery)
# ---------------------------------------------------------------------------


@celery_app.task(
    bind=True,
    name="run_valuation_pipeline",
    max_retries=0,           # retries managed explicitly if needed
    acks_late=True,
)
def run_valuation_pipeline(self, report_id: str) -> None:
    """Celery task: run the full valuation pipeline for *report_id*."""
    asyncio.run(_run_async(self, report_id))


# ---------------------------------------------------------------------------
# Async pipeline implementation
# ---------------------------------------------------------------------------


async def _run_async(task, report_id: str) -> None:  # noqa: C901 (complexity accepted)
    """Full async pipeline. Updates DB status at every major checkpoint."""

    async with AsyncSessionLocal() as db:
        try:
            # ── 1. Load report ──────────────────────────────────────────────
            report = await _get_report(db, report_id)
            if report is None:
                logger.error("Report %s not found — aborting pipeline", report_id)
                return

            # ── 2. Parse documents ──────────────────────────────────────────
            await _update_status(db, report_id, JobStatus.PARSING, "Đang đọc và phân tích tài liệu...")

            doc_context = await _parse_documents(db, report)
            if not doc_context:
                raise RuntimeError("Không có tài liệu nào được phân tích thành công.")

            logger.info(
                "Report %s: parsed %d document(s): %s",
                report_id,
                len(doc_context),
                list(doc_context.keys()),
            )

            # ── 3. Run parallel agents (A1-A5, A8) ─────────────────────────
            await _update_status(
                db, report_id, JobStatus.RUNNING_AGENTS,
                "Đang chạy AI agents phân tích (song song)...",
            )

            (
                company_profile,
                financials,
                market_analysis,
                business_ops,
                management,
                risks,
            ) = await _run_parallel_agents(doc_context)

            logger.info(
                "Report %s: parallel agents done — profile=%s, fin=%s, mkt=%s, "
                "ops=%s, mgmt=%s, risk=%s",
                report_id,
                company_profile is not None,
                financials is not None,
                market_analysis is not None,
                business_ops is not None,
                management is not None,
                risks is not None,
            )

            # ── 4. Run A6 ProjectionAgent ───────────────────────────────────
            projections = await _run_agent_safe(
                "ProjectionAgent",
                ProjectionAgent().run(doc_context),
            )
            logger.info("Report %s: A6 ProjectionAgent done=%s", report_id, projections is not None)

            # ── 5. Run A7 ValuationAgent ────────────────────────────────────
            valuation_extra: dict = {}
            if projections is not None:
                valuation_extra = projections.model_dump()

            valuation = await _run_agent_safe(
                "ValuationAgent",
                ValuationAgent().run(doc_context, extra_context=valuation_extra or None),
            )
            logger.info("Report %s: A7 ValuationAgent done=%s", report_id, valuation is not None)

            # ── 6. Aggregate results ────────────────────────────────────────
            await _update_status(db, report_id, JobStatus.AGGREGATING, "Đang tổng hợp kết quả...")

            aggregated = aggregate_results(
                job_id=report.job_id,
                company_profile=company_profile,
                financials=financials,
                market_analysis=market_analysis,
                business_ops=business_ops,
                management=management,
                projections=projections,
                valuation=valuation,
                risks=risks,
            )

            # Update company name from agent output if available
            if company_profile and company_profile.company_name:
                await _update_company_name(db, report_id, company_profile.company_name)

            # ── 7. Build PDF ────────────────────────────────────────────────
            await _update_status(db, report_id, JobStatus.BUILDING_PDF, "Đang tạo báo cáo PDF...")

            pdf_bytes = build_pdf(aggregated)
            pdf_url = await _save_pdf_to_db(db, report_id, pdf_bytes)

            # ── 8. Mark DONE ────────────────────────────────────────────────
            await _update_status(
                db, report_id, JobStatus.DONE,
                "Hoàn thành định giá doanh nghiệp.",
                pdf_url=pdf_url,
            )
            logger.info("Report %s: pipeline completed. pdf_url=%s", report_id, pdf_url)

        except Exception as exc:
            error_detail = traceback.format_exc()
            logger.error(
                "Report %s: pipeline FAILED — %s\n%s",
                report_id,
                exc,
                error_detail,
            )
            try:
                await _update_status(
                    db, report_id, JobStatus.FAILED,
                    f"Pipeline thất bại: {exc}",
                    error_message=str(exc),
                )
            except Exception as db_exc:
                logger.error("Report %s: cannot update FAILED status: %s", report_id, db_exc)


# ---------------------------------------------------------------------------
# Parallel agent runner
# ---------------------------------------------------------------------------


async def _run_parallel_agents(doc_context: dict[str, str]) -> tuple[
    Optional[CompanyProfileOutput],
    Optional[FinancialStatementOutput],
    Optional[MarketAnalysisOutput],
    Optional[BusinessOpsOutput],
    Optional[ManagementOutput],
    Optional[RiskOutput],
]:
    """Run A1-A5 and A8 concurrently via asyncio.gather."""

    results = await asyncio.gather(
        _run_agent_safe("CompanyProfileAgent", CompanyProfileAgent().run(doc_context)),
        _run_agent_safe("FinancialStatementAgent", FinancialStatementAgent().run(doc_context)),
        _run_agent_safe("MarketAnalysisAgent", MarketAnalysisAgent().run(doc_context)),
        _run_agent_safe("BusinessOpsAgent", BusinessOpsAgent().run(doc_context)),
        _run_agent_safe("ManagementAgent", ManagementAgent().run(doc_context)),
        _run_agent_safe("RiskAgent", RiskAgent().run(doc_context)),
        return_exceptions=False,  # exceptions already caught inside _run_agent_safe
    )
    return tuple(results)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Helper: safe agent execution
# ---------------------------------------------------------------------------


async def _run_agent_safe(agent_name: str, coro):
    """
    Await *coro* (an agent .run() call).
    On any exception: log the error and return None so the pipeline continues.
    """
    try:
        return await coro
    except Exception as exc:
        logger.error(
            "Agent %s failed (non-fatal): %s\n%s",
            agent_name,
            exc,
            traceback.format_exc(),
        )
        return None


# ---------------------------------------------------------------------------
# Helper: parse documents from DB
# ---------------------------------------------------------------------------


async def _parse_documents(db: AsyncSession, report: Report) -> dict[str, str]:
    """
    Fetch all documents belonging to *report*, parse each to text,
    and return a mapping {doc_type: extracted_text}.

    If multiple documents share the same doc_type, their texts are concatenated
    with a separator.
    """
    stmt = select(Document).where(Document.report_id == report.id)
    result = await db.execute(stmt)
    documents: list[Document] = list(result.scalars().all())

    doc_context: dict[str, str] = {}

    for doc in documents:
        try:
            # Use pre-extracted text if available (set during upload phase)
            if doc.extracted_text and doc.extracted_text.strip():
                text = doc.extracted_text.strip()
            else:
                # Fallback: re-parse from Supabase Storage
                text = await _fetch_and_parse_from_storage(doc)

            if not text:
                logger.warning("Document %s (%s) produced empty text — skipping", doc.id, doc.filename)
                continue

            doc_type = doc.doc_type
            if doc_type in doc_context:
                # Merge multiple documents of the same type
                doc_context[doc_type] = (
                    doc_context[doc_type]
                    + f"\n\n--- Tài liệu bổ sung: {doc.filename} ---\n\n"
                    + text
                )
            else:
                doc_context[doc_type] = text

        except Exception as exc:
            logger.error(
                "Failed to parse document %s (%s): %s",
                doc.id,
                doc.filename,
                exc,
            )

    return doc_context


async def _fetch_and_parse_from_storage(doc: Document) -> str:
    """
    Download a document from Supabase Storage and parse it to text.
    Used as fallback when extracted_text is not stored in the DB.
    """
    settings = get_settings()

    # Import supabase client lazily to avoid circular imports
    from supabase import create_client  # type: ignore[import-untyped]

    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

    try:
        response = client.storage.from_(settings.SUPABASE_BUCKET).download(doc.storage_path)
        file_bytes: bytes = response
        return await parse_document(doc.filename, file_bytes)
    except Exception as exc:
        logger.error(
            "Failed to download document %s from storage path %s: %s",
            doc.id,
            doc.storage_path,
            exc,
        )
        return ""


# ---------------------------------------------------------------------------
# Helper: upload PDF to Supabase Storage
# ---------------------------------------------------------------------------


async def _save_pdf_to_db(db: AsyncSession, report_id: str, pdf_bytes: bytes) -> Optional[str]:
    """
    Save generated PDF bytes directly into the reports table.
    Returns a download URL pointing to the backend's /api/reports/{id}/pdf endpoint.
    """
    import uuid as _uuid
    settings = get_settings()
    download_token = str(_uuid.uuid4())

    stmt = (
        update(Report)
        .where(Report.id == report_id)
        .values(pdf_bytes=pdf_bytes, download_token=download_token)
        .execution_options(synchronize_session=False)
    )
    await db.execute(stmt)
    await db.commit()

    pdf_url = f"{settings.BACKEND_URL}/api/reports/{report_id}/pdf?token={download_token}"
    logger.info("PDF saved to DB: report=%s size=%d bytes url=%s", report_id, len(pdf_bytes), pdf_url)
    return pdf_url


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


async def _get_report(db: AsyncSession, report_id: str) -> Optional[Report]:
    """Fetch a Report row by primary key."""
    stmt = select(Report).where(Report.id == report_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _update_status(
    db: AsyncSession,
    report_id: str,
    status: JobStatus,
    message: str,
    pdf_url: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    """Update report status and optional fields, then commit."""
    values: dict = {
        "status": status.value,
    }
    if pdf_url is not None:
        values["pdf_url"] = pdf_url
    if error_message is not None:
        values["error_message"] = error_message

    stmt = (
        update(Report)
        .where(Report.id == report_id)
        .values(**values)
        .execution_options(synchronize_session=False)
    )
    await db.execute(stmt)
    await db.commit()

    progress = _PROGRESS.get(status, 0)
    logger.info(
        "Report %s → status=%s (%d%%) — %s",
        report_id,
        status.value,
        progress,
        message,
    )


async def _update_company_name(db: AsyncSession, report_id: str, company_name: str) -> None:
    """Update the company_name field from CompanyProfileAgent output."""
    stmt = (
        update(Report)
        .where(Report.id == report_id)
        .values(company_name=company_name)
        .execution_options(synchronize_session=False)
    )
    await db.execute(stmt)
    await db.commit()
