from datetime import datetime
from typing import Optional

from app.schemas.agents import (
    AggregatedReport,
    CompanyProfileOutput,
    FinancialStatementOutput,
    MarketAnalysisOutput,
    BusinessOpsOutput,
    ManagementOutput,
    ProjectionOutput,
    ValuationOutput,
    RiskOutput,
)


def aggregate_results(
    job_id: str,
    company_profile: Optional[CompanyProfileOutput] = None,
    financials: Optional[FinancialStatementOutput] = None,
    market_analysis: Optional[MarketAnalysisOutput] = None,
    business_ops: Optional[BusinessOpsOutput] = None,
    management: Optional[ManagementOutput] = None,
    projections: Optional[ProjectionOutput] = None,
    valuation: Optional[ValuationOutput] = None,
    risks: Optional[RiskOutput] = None,
) -> AggregatedReport:
    """
    Nhận output từ các agents (có thể None nếu agent thất bại),
    tổng hợp thành AggregatedReport.
    """
    return AggregatedReport(
        company_profile=company_profile,
        financials=financials,
        market_analysis=market_analysis,
        business_ops=business_ops,
        management=management,
        projections=projections,
        valuation=valuation,
        risks=risks,
        generated_at=datetime.now().isoformat(),
        job_id=job_id,
    )
