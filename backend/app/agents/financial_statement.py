from typing import Type

from app.agents.base import BaseAgent, T
from app.schemas.agents import FinancialStatementOutput


class FinancialStatementAgent(BaseAgent):
    """
    A2 – Trích xuất và phân tích báo cáo tài chính lịch sử.
    Đơn vị: tỷ đồng VND.
    """

    AGENT_NAME = "financial_statement"

    def get_system_prompt(self) -> str:
        return (
            "Bạn là chuyên gia phân tích tài chính CFA. "
            "Hãy đọc báo cáo tài chính và trích xuất số liệu chính xác. "
            "Đơn vị: tỷ đồng VND. "
            "Nếu số liệu chưa đủ, hãy ước tính dựa trên thông tin có sẵn và ghi rõ trong key_observations. "
            "Tính toán các chỉ số tài chính: gross_margin = gross_profit/revenue, "
            "ebitda_margin = ebitda/revenue, net_margin = net_income/revenue (tất cả dạng phần trăm 0-100). "
            "FCF = CFO - CapEx. ROE = net_income/equity, ROA = net_income/total_assets (phần trăm). "
            "Revenue CAGR và Profit CAGR tính theo phần trăm trên toàn bộ kỳ dữ liệu. "
            "Trả về kết quả bằng cách gọi tool được chỉ định."
        )

    def get_output_schema(self) -> dict:
        financial_year_schema = {
            "type": "object",
            "required": [
                "year", "revenue", "cogs", "gross_profit", "ebitda", "ebit",
                "net_income", "total_assets", "total_debt", "equity",
                "cfo", "capex", "fcf", "gross_margin", "ebitda_margin", "net_margin",
            ],
            "properties": {
                "year": {"type": "integer", "description": "Năm tài chính"},
                "revenue": {"type": "number", "description": "Doanh thu thuần (tỷ đồng)"},
                "cogs": {"type": "number", "description": "Giá vốn hàng bán (tỷ đồng)"},
                "gross_profit": {"type": "number", "description": "Lợi nhuận gộp (tỷ đồng)"},
                "ebitda": {"type": "number", "description": "EBITDA (tỷ đồng)"},
                "ebit": {"type": "number", "description": "EBIT (tỷ đồng)"},
                "net_income": {"type": "number", "description": "Lợi nhuận sau thuế (tỷ đồng)"},
                "total_assets": {"type": "number", "description": "Tổng tài sản (tỷ đồng)"},
                "total_debt": {"type": "number", "description": "Tổng nợ vay (tỷ đồng)"},
                "equity": {"type": "number", "description": "Vốn chủ sở hữu (tỷ đồng)"},
                "cfo": {"type": "number", "description": "Dòng tiền từ hoạt động kinh doanh (tỷ đồng)"},
                "capex": {"type": "number", "description": "Chi tiêu vốn (tỷ đồng, giá trị dương)"},
                "fcf": {"type": "number", "description": "Free Cash Flow = CFO - CapEx (tỷ đồng)"},
                "gross_margin": {"type": "number", "description": "Biên lợi nhuận gộp (%)"},
                "ebitda_margin": {"type": "number", "description": "Biên EBITDA (%)"},
                "net_margin": {"type": "number", "description": "Biên lợi nhuận ròng (%)"},
            },
        }

        return {
            "type": "object",
            "required": [
                "years", "roe", "roa", "debt_to_ebitda",
                "revenue_cagr", "profit_cagr", "key_observations",
            ],
            "properties": {
                "currency": {"type": "string", "default": "VND"},
                "unit": {"type": "string", "default": "tỷ đồng"},
                "years": {
                    "type": "array",
                    "description": "Số liệu tài chính theo từng năm (thứ tự tăng dần)",
                    "items": financial_year_schema,
                    "minItems": 1,
                },
                "roe": {
                    "type": "number",
                    "description": "Return on Equity trung bình kỳ phân tích (%)",
                },
                "roa": {
                    "type": "number",
                    "description": "Return on Assets trung bình kỳ phân tích (%)",
                },
                "debt_to_ebitda": {
                    "type": "number",
                    "description": "Tỷ lệ Debt/EBITDA (năm gần nhất)",
                },
                "revenue_cagr": {
                    "type": "number",
                    "description": "Tăng trưởng doanh thu kép hàng năm (CAGR) toàn kỳ (%)",
                },
                "profit_cagr": {
                    "type": "number",
                    "description": "Tăng trưởng lợi nhuận kép hàng năm (CAGR) toàn kỳ (%)",
                },
                "key_observations": {
                    "type": "array",
                    "description": "Nhận xét quan trọng về tình hình tài chính",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
            },
        }

    def get_output_model(self) -> Type[FinancialStatementOutput]:
        return FinancialStatementOutput
