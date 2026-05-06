from typing import Type

from app.agents.base import BaseAgent, T
from app.schemas.agents import MarketAnalysisOutput


class MarketAnalysisAgent(BaseAgent):
    """
    A3 – Phân tích thị trường: TAM/SAM/SOM, tốc độ tăng trưởng ngành,
    xu hướng, đối thủ cạnh tranh và vị thế thị trường của doanh nghiệp.
    """

    AGENT_NAME = "market_analysis"

    def get_system_prompt(self) -> str:
        return (
            "Bạn là chuyên gia phân tích thị trường. "
            "Hãy phân tích quy mô thị trường (TAM/SAM/SOM), tốc độ tăng trưởng ngành, "
            "xu hướng và đối thủ cạnh tranh dựa trên tài liệu và kiến thức ngành của bạn. "
            "TAM = Tổng thị trường có thể tiếp cận (toàn quốc/toàn cầu tùy ngành). "
            "SAM = Thị trường có thể phục vụ (phân khúc phù hợp với doanh nghiệp). "
            "SOM = Thị phần doanh nghiệp có thể chiếm được thực tế. "
            "Tất cả giá trị tính bằng tỷ đồng VND. "
            "Đối thủ cạnh tranh phải liệt kê cả trong nước và quốc tế nếu có. "
            "Trả về kết quả bằng cách gọi tool được chỉ định."
        )

    def get_output_schema(self) -> dict:
        competitor_schema = {
            "type": "object",
            "required": ["name", "strengths", "weaknesses"],
            "properties": {
                "name": {"type": "string", "description": "Tên đối thủ cạnh tranh"},
                "market_share": {
                    "type": ["number", "null"],
                    "description": "Thị phần ước tính (%)",
                },
                "strengths": {
                    "type": "array",
                    "description": "Điểm mạnh của đối thủ",
                    "items": {"type": "string"},
                },
                "weaknesses": {
                    "type": "array",
                    "description": "Điểm yếu của đối thủ",
                    "items": {"type": "string"},
                },
            },
        }

        return {
            "type": "object",
            "required": [
                "tam_value", "sam_value", "som_value",
                "industry_cagr", "market_stage", "key_trends",
                "competitors", "market_position",
            ],
            "properties": {
                "tam_value": {
                    "type": "number",
                    "description": "Quy mô TAM (tỷ đồng)",
                },
                "sam_value": {
                    "type": "number",
                    "description": "Quy mô SAM (tỷ đồng)",
                },
                "som_value": {
                    "type": "number",
                    "description": "Quy mô SOM (tỷ đồng)",
                },
                "market_size_unit": {
                    "type": "string",
                    "default": "tỷ đồng",
                    "description": "Đơn vị quy mô thị trường",
                },
                "industry_cagr": {
                    "type": "number",
                    "description": "Tốc độ tăng trưởng kép hàng năm của ngành (%)",
                },
                "market_stage": {
                    "type": "string",
                    "description": "Giai đoạn thị trường: emerging / growing / mature / declining",
                },
                "key_trends": {
                    "type": "array",
                    "description": "Các xu hướng quan trọng của ngành",
                    "items": {"type": "string"},
                    "minItems": 3,
                },
                "competitors": {
                    "type": "array",
                    "description": "Danh sách đối thủ cạnh tranh chính",
                    "items": competitor_schema,
                    "minItems": 1,
                },
                "market_position": {
                    "type": "string",
                    "description": "Mô tả vị thế của doanh nghiệp trên thị trường",
                },
                "market_share_estimate": {
                    "type": ["number", "null"],
                    "description": "Ước tính thị phần hiện tại của doanh nghiệp (%)",
                },
            },
        }

    def get_output_model(self) -> Type[MarketAnalysisOutput]:
        return MarketAnalysisOutput
