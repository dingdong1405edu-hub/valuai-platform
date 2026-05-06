from typing import Type

from app.agents.base import BaseAgent, T
from app.schemas.agents import ProjectionOutput


class ProjectionAgent(BaseAgent):
    """
    A6 – Lập mô hình tài chính dự phóng 5 năm (base case).
    Chạy sau khi A1-A5 và A8 hoàn thành để có đủ ngữ cảnh.
    """

    AGENT_NAME = "projection"

    def get_system_prompt(self) -> str:
        return (
            "Bạn là chuyên gia lập mô hình tài chính. "
            "Hãy dự phóng tài chính 5 năm tới dựa trên lịch sử tài chính và kế hoạch kinh doanh. "
            "Đơn vị tỷ đồng. Assumptions phải thực tế và có căn cứ. "
            "Nguyên tắc lập mô hình: "
            "(1) Doanh thu: dựa trên tăng trưởng lịch sử, kế hoạch mở rộng, tình hình thị trường. "
            "(2) EBITDA margin: dựa trên quy mô kinh tế (operating leverage), cải thiện vận hành. "
            "(3) CapEx: tùy theo kế hoạch đầu tư và ngành. "
            "(4) Working capital: thay đổi vốn lưu động (dương = tiêu tiền). "
            "(5) FCF = EBITDA × (1 - tax_rate) + D&A - CapEx - working_capital_change. "
            "Đơn giản hóa: FCF ≈ EBITDA × 0.75 - CapEx - working_capital_change. "
            "revenue_growth tính bằng % so với năm trước. "
            "ebitda_margin tính bằng % của doanh thu. "
            "Phải có đúng 5 ProjectionYear. "
            "revenue_cagr và ebitda_cagr tính cho toàn bộ giai đoạn 5 năm. "
            "terminal_year_ebitda là EBITDA của năm cuối (năm 5). "
            "Trả về kết quả bằng cách gọi tool được chỉ định."
        )

    def get_output_schema(self) -> dict:
        projection_year_schema = {
            "type": "object",
            "required": [
                "year", "revenue", "revenue_growth", "ebitda",
                "ebitda_margin", "capex", "working_capital_change", "fcf",
            ],
            "properties": {
                "year": {
                    "type": "integer",
                    "description": "Năm dự phóng (ví dụ: 2025, 2026,...)",
                },
                "revenue": {
                    "type": "number",
                    "description": "Doanh thu dự phóng (tỷ đồng)",
                },
                "revenue_growth": {
                    "type": "number",
                    "description": "Tăng trưởng doanh thu so với năm trước (%)",
                },
                "ebitda": {
                    "type": "number",
                    "description": "EBITDA dự phóng (tỷ đồng)",
                },
                "ebitda_margin": {
                    "type": "number",
                    "description": "Biên EBITDA (%)",
                },
                "capex": {
                    "type": "number",
                    "description": "Chi tiêu vốn (tỷ đồng, giá trị dương)",
                },
                "working_capital_change": {
                    "type": "number",
                    "description": "Thay đổi vốn lưu động (tỷ đồng, dương = sử dụng tiền)",
                },
                "fcf": {
                    "type": "number",
                    "description": "Free Cash Flow (tỷ đồng)",
                },
            },
        }

        return {
            "type": "object",
            "required": [
                "base_case",
                "key_assumptions",
                "revenue_cagr",
                "ebitda_cagr",
                "terminal_year_ebitda",
            ],
            "properties": {
                "base_case": {
                    "type": "array",
                    "description": "Dự phóng base case 5 năm",
                    "items": projection_year_schema,
                    "minItems": 5,
                    "maxItems": 5,
                },
                "key_assumptions": {
                    "type": "array",
                    "description": "Các giả định chính của mô hình dự phóng",
                    "items": {"type": "string"},
                    "minItems": 5,
                },
                "revenue_cagr": {
                    "type": "number",
                    "description": "Tăng trưởng doanh thu kép hàng năm 5 năm (%)",
                },
                "ebitda_cagr": {
                    "type": "number",
                    "description": "Tăng trưởng EBITDA kép hàng năm 5 năm (%)",
                },
                "terminal_year_ebitda": {
                    "type": "number",
                    "description": "EBITDA năm cuối dự phóng (năm 5, tỷ đồng)",
                },
            },
        }

    def get_output_model(self) -> Type[ProjectionOutput]:
        return ProjectionOutput
