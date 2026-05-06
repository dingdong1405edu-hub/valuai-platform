"""
Valuation AI agents package.

Execution order:
  - Parallel (asyncio.gather): A1, A2, A3, A4, A5, A8
  - Sequential:                A6 (ProjectionAgent)
  - Sequential:                A7 (ValuationAgent) — receives A6 output via extra_context
"""

from app.agents.base import BaseAgent
from app.agents.business_ops import BusinessOpsAgent
from app.agents.company_profile import CompanyProfileAgent
from app.agents.financial_statement import FinancialStatementAgent
from app.agents.management import ManagementAgent
from app.agents.market_analysis import MarketAnalysisAgent
from app.agents.projection import ProjectionAgent
from app.agents.risk import RiskAgent
from app.agents.valuation import ValuationAgent

__all__ = [
    "BaseAgent",
    "CompanyProfileAgent",       # A1
    "FinancialStatementAgent",   # A2
    "MarketAnalysisAgent",       # A3
    "BusinessOpsAgent",          # A4
    "ManagementAgent",           # A5
    "ProjectionAgent",           # A6
    "ValuationAgent",            # A7
    "RiskAgent",                 # A8
]
