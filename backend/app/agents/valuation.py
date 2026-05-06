from typing import Type

from app.agents.base import BaseAgent, T
from app.schemas.agents import ValuationOutput


class ValuationAgent(BaseAgent):
    """
    A7 – Định giá doanh nghiệp theo DCF và multiples.
    Nhận ProjectionOutput từ A6 qua extra_context.
    Sensitivity matrix: WACC ×3 levels × growth ×3 levels = 3×3 = 9 values.
    """

    AGENT_NAME = "valuation"

    def get_system_prompt(self) -> str:
        return (
            "Bạn là chuyên gia định giá doanh nghiệp CFA/CPA. "
            "Hãy thực hiện định giá theo DCF và phương pháp multiples. "
            "WACC điển hình cho SME Việt Nam: 12-18%. "
            "Multiple EV/EBITDA ngành: 5-12x tùy ngành. "
            "\n"
            "PHƯƠNG PHÁP DCF:\n"
            "- Chiết khấu FCF 5 năm theo WACC.\n"
            "- Terminal value = EBITDA_năm5 × exit_multiple (hoặc Gordon Growth Model: FCF_năm5 / (WACC - g)).\n"
            "- Enterprise Value = PV(FCF) + PV(Terminal Value).\n"
            "- Equity Value = Enterprise Value - Net Debt.\n"
            "\n"
            "PHƯƠNG PHÁP MULTIPLES:\n"
            "- So sánh EV/EBITDA với các công ty tương đương trong ngành.\n"
            "- implied_ev_from_ebitda = terminal_year_ebitda × ev_ebitda_multiple.\n"
            "\n"
            "SENSITIVITY MATRIX (3×3):\n"
            "- wacc_range: [base_wacc - 2%, base_wacc, base_wacc + 2%] (3 giá trị).\n"
            "- growth_range: [base_g - 1%, base_g, base_g + 1%] (3 giá trị).\n"
            "- values: ma trận 3×3 equity_value tương ứng (tỷ đồng).\n"
            "- Hàng i ứng với wacc_range[i], cột j ứng với growth_range[j].\n"
            "\n"
            "TỔNG HỢP:\n"
            "- final_value_low = min(DCF equity, multiples-based equity) × 0.9.\n"
            "- final_value_mid = trung bình có trọng số DCF (60%) và multiples (40%).\n"
            "- final_value_high = max × 1.1.\n"
            "- fair_value = final_value_mid.\n"
            "- upside_downside_pct = (fair_value / entry_price_suggestion - 1) × 100 nếu có, "
            "  còn không thì = (final_value_high / final_value_mid - 1) × 100.\n"
            "- recommendation: 'BUY' / 'HOLD' / 'SELL' / 'WATCH' kèm lý do ngắn gọn.\n"
            "Trả về kết quả bằng cách gọi tool được chỉ định."
        )

    def get_output_schema(self) -> dict:
        dcf_schema = {
            "type": "object",
            "required": [
                "wacc", "terminal_growth_rate",
                "enterprise_value", "equity_value", "net_debt",
            ],
            "properties": {
                "wacc": {
                    "type": "number",
                    "description": "WACC sử dụng trong DCF (%, ví dụ: 15.0)",
                },
                "terminal_growth_rate": {
                    "type": "number",
                    "description": "Tỷ lệ tăng trưởng terminal value (%, ví dụ: 3.0)",
                },
                "enterprise_value": {
                    "type": "number",
                    "description": "Enterprise Value từ DCF (tỷ đồng)",
                },
                "equity_value": {
                    "type": "number",
                    "description": "Equity Value = EV - Net Debt (tỷ đồng)",
                },
                "net_debt": {
                    "type": "number",
                    "description": "Nợ ròng = Total Debt - Cash (tỷ đồng)",
                },
            },
        }

        multiples_schema = {
            "type": "object",
            "required": [
                "ev_ebitda_multiple", "implied_ev_from_ebitda",
                "comparable_companies", "industry_median_multiple",
            ],
            "properties": {
                "ev_ebitda_multiple": {
                    "type": "number",
                    "description": "Multiple EV/EBITDA áp dụng (x)",
                },
                "pe_multiple": {
                    "type": ["number", "null"],
                    "description": "Multiple P/E áp dụng nếu có (x)",
                },
                "pb_multiple": {
                    "type": ["number", "null"],
                    "description": "Multiple P/B áp dụng nếu có (x)",
                },
                "implied_ev_from_ebitda": {
                    "type": "number",
                    "description": "Implied EV = terminal_year_ebitda × ev_ebitda_multiple (tỷ đồng)",
                },
                "comparable_companies": {
                    "type": "array",
                    "description": "Danh sách công ty tương đương dùng để so sánh",
                    "items": {"type": "string"},
                    "minItems": 2,
                },
                "industry_median_multiple": {
                    "type": "number",
                    "description": "Median EV/EBITDA của ngành (x)",
                },
            },
        }

        sensitivity_schema = {
            "type": "object",
            "required": ["wacc_range", "growth_range", "values"],
            "properties": {
                "wacc_range": {
                    "type": "array",
                    "description": "3 mức WACC [base-2%, base, base+2%] (%)",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                },
                "growth_range": {
                    "type": "array",
                    "description": "3 mức tăng trưởng terminal [base-1%, base, base+1%] (%)",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                },
                "values": {
                    "type": "array",
                    "description": "Ma trận 3×3 equity_value (tỷ đồng). values[i][j] = wacc_range[i] × growth_range[j]",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 3,
                    },
                    "minItems": 3,
                    "maxItems": 3,
                },
            },
        }

        return {
            "type": "object",
            "required": [
                "dcf", "multiples",
                "final_value_low", "final_value_mid", "final_value_high",
                "sensitivity", "fair_value", "upside_downside_pct", "recommendation",
            ],
            "properties": {
                "dcf": {
                    **dcf_schema,
                    "description": "Kết quả định giá DCF",
                },
                "multiples": {
                    **multiples_schema,
                    "description": "Kết quả định giá theo multiples",
                },
                "final_value_low": {
                    "type": "number",
                    "description": "Định giá thấp (tỷ đồng) – bear case",
                },
                "final_value_mid": {
                    "type": "number",
                    "description": "Định giá trung tâm (tỷ đồng) – base case",
                },
                "final_value_high": {
                    "type": "number",
                    "description": "Định giá cao (tỷ đồng) – bull case",
                },
                "sensitivity": {
                    **sensitivity_schema,
                    "description": "Ma trận sensitivity phân tích",
                },
                "fair_value": {
                    "type": "number",
                    "description": "Giá trị hợp lý (= final_value_mid, tỷ đồng)",
                },
                "upside_downside_pct": {
                    "type": "number",
                    "description": "Upside/downside so với giá nhập hoặc khoảng biến động (%)",
                },
                "recommendation": {
                    "type": "string",
                    "description": "Khuyến nghị đầu tư: BUY / HOLD / SELL / WATCH kèm lý do",
                },
                "deal_structure": {
                    "type": ["string", "null"],
                    "description": "Gợi ý cấu trúc giao dịch (equity, tranche, earn-out,...)",
                },
                "entry_price_suggestion": {
                    "type": ["number", "null"],
                    "description": "Giá nhập đề xuất (tỷ đồng)",
                },
            },
        }

    def get_output_model(self) -> Type[ValuationOutput]:
        return ValuationOutput
