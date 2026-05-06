"""
Re-export shim for the valuation pipeline Celery task.

The real implementation lives in ``app.orchestrator.runner`` which has a
fully-async, agent-based pipeline.  This module simply re-exports
``run_valuation_pipeline`` so that the upload router can import it from
a stable path without creating a circular dependency with the orchestrator.

Usage (in upload router)::

    from app.tasks.valuation import run_valuation_pipeline

    task = run_valuation_pipeline.apply_async(kwargs={"report_id": report.id})
"""

from app.orchestrator.runner import run_valuation_pipeline  # noqa: F401

__all__ = ["run_valuation_pipeline"]
