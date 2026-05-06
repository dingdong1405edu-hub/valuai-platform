from typing import Type

from app.agents.base import BaseAgent, T
from app.schemas.agents import RiskOutput


class RiskAgent(BaseAgent):
    """
    A8 – Phân tích rủi ro toàn diện: tài chính, thị trường, pháp lý, vận hành.
    Chạy song song với A1-A5.
    """

    AGENT_NAME = "risk"

    def get_system_prompt(self) -> str:
        return (
            "Bạn là chuyên gia quản lý rủi ro. "
            "Hãy xác định và đánh giá các rủi ro tài chính, thị trường, pháp lý và vận hành của doanh nghiệp. "
            "Phân loại rủi ro theo category (chỉ dùng: 'financial', 'market', 'legal', 'operational'). "
            "Đánh giá mức độ nghiêm trọng theo severity (chỉ dùng: 'high', 'medium', 'low'). "
            "Với mỗi rủi ro phải đề xuất biện pháp giảm thiểu cụ thể và thực tế. "
            "overall_risk_level: đánh giá tổng thể mức độ rủi ro ('high', 'medium', 'low'). "
            "Ưu tiên liệt kê các rủi ro có severity 'high' trước. "
            "Tối thiểu phải có 1 rủi ro cho mỗi category. "
            "Trả về kết quả bằng cách gọi tool được chỉ định."
        )

    def get_output_schema(self) -> dict:
        risk_schema = {
            "type": "object",
            "required": ["category", "description", "severity", "mitigation"],
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["financial", "market", "legal", "operational"],
                    "description": "Loại rủi ro",
                },
                "description": {
                    "type": "string",
                    "description": "Mô tả chi tiết về rủi ro",
                },
                "severity": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Mức độ nghiêm trọng",
                },
                "mitigation": {
                    "type": "string",
                    "description": "Biện pháp giảm thiểu rủi ro",
                },
            },
        }

        return {
            "type": "object",
            "required": ["risks", "overall_risk_level", "key_risk_summary"],
            "properties": {
                "risks": {
                    "type": "array",
                    "description": "Danh sách rủi ro được xác định",
                    "items": risk_schema,
                    "minItems": 4,
                },
                "overall_risk_level": {
                    "type": "string",
                    "enum": ["high", "medium", "low"],
                    "description": "Mức độ rủi ro tổng thể của doanh nghiệp",
                },
                "key_risk_summary": {
                    "type": "string",
                    "description": "Tóm tắt các rủi ro trọng yếu nhất cần chú ý",
                },
            },
        }

    def get_output_model(self) -> Type[RiskOutput]:
        return RiskOutput
