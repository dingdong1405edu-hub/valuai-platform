from typing import Optional, Any
from pydantic import BaseModel


class Shareholder(BaseModel):
    name: str
    percentage: float
    role: Optional[str] = None


class Executive(BaseModel):
    name: str
    title: str
    background: str


class CompanyProfileOutput(BaseModel):
    company_name: str
    founded_year: Optional[int] = None
    industry: str
    sub_industry: str
    headquarters: str
    description: str
    history: str
    shareholders: list[Shareholder]
    executives: list[Executive]
    products_services: list[str]
    revenue_model: str
    value_chain_input: str
    value_chain_production: str
    value_chain_distribution: str
    value_chain_customer: str


class FinancialYear(BaseModel):
    year: int
    revenue: float
    cogs: float
    gross_profit: float
    ebitda: float
    ebit: float
    net_income: float
    total_assets: float
    total_debt: float
    equity: float
    cfo: float
    capex: float
    fcf: float
    gross_margin: float
    ebitda_margin: float
    net_margin: float


class FinancialStatementOutput(BaseModel):
    currency: str = "VND"
    unit: str = "tỷ đồng"
    years: list[FinancialYear]
    roe: float
    roa: float
    debt_to_ebitda: float
    revenue_cagr: float
    profit_cagr: float
    key_observations: list[str]


class Competitor(BaseModel):
    name: str
    market_share: Optional[float] = None
    strengths: list[str]
    weaknesses: list[str]


class MarketAnalysisOutput(BaseModel):
    tam_value: float
    sam_value: float
    som_value: float
    market_size_unit: str = "tỷ đồng"
    industry_cagr: float
    market_stage: str
    key_trends: list[str]
    competitors: list[Competitor]
    market_position: str
    market_share_estimate: Optional[float] = None


class RevenueSegment(BaseModel):
    name: str
    percentage: float
    description: str


class BusinessOpsOutput(BaseModel):
    revenue_by_product: list[RevenueSegment]
    revenue_by_channel: list[RevenueSegment]
    revenue_by_region: list[RevenueSegment]
    volume_driver: str
    price_driver: str
    mix_driver: str
    gross_margin: float
    ebitda_margin: float
    unit_economics: Optional[dict] = None
    key_operational_metrics: list[str]


class ManagementOutput(BaseModel):
    ceo_name: str
    ceo_background: str
    ceo_achievements: list[str]
    team_strength: str
    management_score: int
    key_risks_management: list[str]


class ProjectionYear(BaseModel):
    year: int
    revenue: float
    revenue_growth: float
    ebitda: float
    ebitda_margin: float
    capex: float
    working_capital_change: float
    fcf: float


class ProjectionOutput(BaseModel):
    base_case: list[ProjectionYear]
    key_assumptions: list[str]
    revenue_cagr: float
    ebitda_cagr: float
    terminal_year_ebitda: float


class SensitivityMatrix(BaseModel):
    wacc_range: list[float]
    growth_range: list[float]
    values: list[list[float]]


class DCFResult(BaseModel):
    wacc: float
    terminal_growth_rate: float
    enterprise_value: float
    equity_value: float
    net_debt: float


class MultiplesResult(BaseModel):
    ev_ebitda_multiple: float
    pe_multiple: Optional[float] = None
    pb_multiple: Optional[float] = None
    implied_ev_from_ebitda: float
    comparable_companies: list[str]
    industry_median_multiple: float


class ValuationOutput(BaseModel):
    dcf: DCFResult
    multiples: MultiplesResult
    final_value_low: float
    final_value_mid: float
    final_value_high: float
    sensitivity: SensitivityMatrix
    fair_value: float
    upside_downside_pct: float
    recommendation: str
    deal_structure: Optional[str] = None
    entry_price_suggestion: Optional[float] = None


class Risk(BaseModel):
    category: str
    description: str
    severity: str
    mitigation: str


class RiskOutput(BaseModel):
    risks: list[Risk]
    overall_risk_level: str
    key_risk_summary: str


class AggregatedReport(BaseModel):
    company_profile: Optional[CompanyProfileOutput] = None
    financials: Optional[FinancialStatementOutput] = None
    market_analysis: Optional[MarketAnalysisOutput] = None
    business_ops: Optional[BusinessOpsOutput] = None
    management: Optional[ManagementOutput] = None
    projections: Optional[ProjectionOutput] = None
    valuation: Optional[ValuationOutput] = None
    risks: Optional[RiskOutput] = None
    generated_at: str
    job_id: str
