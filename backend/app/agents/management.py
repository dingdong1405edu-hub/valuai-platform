from typing import Type

from app.agents.base import BaseAgent, T
from app.schemas.agents import ManagementOutput


class ManagementAgent(BaseAgent):
    """
    A5 – Đánh giá đội ngũ lãnh đạo: năng lực CEO, sức mạnh team,
    rủi ro quản lý và điểm số tổng hợp.
    """

    AGENT_NAME = "management"

    def get_system_prompt(self) -> str:
        return (
            "Bạn là chuyên gia đánh giá team lãnh đạo. "
            "Hãy phân tích năng lực và kinh nghiệm của đội ngũ quản lý. "
            "Đánh giá dựa trên: (1) Kinh nghiệm và thành tích của CEO, "
            "(2) Năng lực của team lãnh đạo cấp cao, "
            "(3) Văn hóa doanh nghiệp và khả năng thực thi, "
            "(4) Rủi ro phụ thuộc vào cá nhân, quản trị nội bộ. "
            "management_score từ 1 đến 10 (1 = rất yếu, 10 = xuất sắc). "
            "Tiêu chí chấm điểm: kinh nghiệm ngành (30%), track record (30%), "
            "team depth (20%), governance (20%). "
            "key_risks_management: các rủi ro liên quan đến con người và quản trị. "
            "Trả về kết quả bằng cách gọi tool được chỉ định."
        )

    def get_output_schema(self) -> dict:
        return {
            "type": "object",
            "required": [
                "ceo_name",
                "ceo_background",
                "ceo_achievements",
                "team_strength",
                "management_score",
                "key_risks_management",
            ],
            "properties": {
                "ceo_name": {
                    "type": "string",
                    "description": "Họ tên CEO / Người đứng đầu doanh nghiệp",
                },
                "ceo_background": {
                    "type": "string",
                    "description": "Tiểu sử, học vấn và kinh nghiệm của CEO",
                },
                "ceo_achievements": {
                    "type": "array",
                    "description": "Các thành tích nổi bật của CEO",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
                "team_strength": {
                    "type": "string",
                    "description": "Đánh giá tổng thể về sức mạnh của team lãnh đạo",
                },
                "management_score": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Điểm đánh giá đội ngũ lãnh đạo (1-10)",
                },
                "key_risks_management": {
                    "type": "array",
                    "description": "Rủi ro chính liên quan đến đội ngũ và quản trị",
                    "items": {"type": "string"},
                    "minItems": 1,
                },
            },
        }

    def get_output_model(self) -> Type[ManagementOutput]:
        return ManagementOutput
