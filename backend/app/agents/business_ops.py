from typing import Type

from app.agents.base import BaseAgent, T
from app.schemas.agents import BusinessOpsOutput


class BusinessOpsAgent(BaseAgent):
    """
    A4 – Phân tích hoạt động kinh doanh: cơ cấu doanh thu theo sản phẩm,
    kênh bán hàng, khu vực, drivers tăng trưởng và biên lợi nhuận.
    """

    AGENT_NAME = "business_ops"

    def get_system_prompt(self) -> str:
        return (
            "Bạn là chuyên gia phân tích hoạt động kinh doanh. "
            "Hãy phân tích cơ cấu doanh thu, kênh bán hàng, driver tăng trưởng và biên lợi nhuận. "
            "Phân tích cụ thể: (1) Doanh thu theo sản phẩm/dịch vụ, "
            "(2) Doanh thu theo kênh bán hàng (online, offline, B2B, B2C,...), "
            "(3) Doanh thu theo khu vực địa lý. "
            "Tổng % của mỗi nhóm phân tích phải bằng 100%. "
            "Volume driver: yếu tố tăng sản lượng. "
            "Price driver: yếu tố thay đổi giá bán. "
            "Mix driver: thay đổi cơ cấu sản phẩm/kênh. "
            "Biên lợi nhuận tính bằng % (gross_margin, ebitda_margin). "
            "Unit economics: nếu có dữ liệu (CAC, LTV, AOV,...). "
            "Trả về kết quả bằng cách gọi tool được chỉ định."
        )

    def get_output_schema(self) -> dict:
        revenue_segment_schema = {
            "type": "object",
            "required": ["name", "percentage", "description"],
            "properties": {
                "name": {"type": "string", "description": "Tên phân khúc"},
                "percentage": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Tỷ trọng (%)",
                },
                "description": {
                    "type": "string",
                    "description": "Mô tả chi tiết phân khúc",
                },
            },
        }

        return {
            "type": "object",
            "required": [
                "revenue_by_product",
                "revenue_by_channel",
                "revenue_by_region",
                "volume_driver",
                "price_driver",
                "mix_driver",
                "gross_margin",
                "ebitda_margin",
                "key_operational_metrics",
            ],
            "properties": {
                "revenue_by_product": {
                    "type": "array",
                    "description": "Cơ cấu doanh thu theo sản phẩm/dịch vụ (tổng = 100%)",
                    "items": revenue_segment_schema,
                    "minItems": 1,
                },
                "revenue_by_channel": {
                    "type": "array",
                    "description": "Cơ cấu doanh thu theo kênh bán hàng (tổng = 100%)",
                    "items": revenue_segment_schema,
                    "minItems": 1,
                },
                "revenue_by_region": {
                    "type": "array",
                    "description": "Cơ cấu doanh thu theo khu vực địa lý (tổng = 100%)",
                    "items": revenue_segment_schema,
                    "minItems": 1,
                },
                "volume_driver": {
                    "type": "string",
                    "description": "Yếu tố chính thúc đẩy tăng trưởng sản lượng",
                },
                "price_driver": {
                    "type": "string",
                    "description": "Yếu tố chính tác động đến giá bán",
                },
                "mix_driver": {
                    "type": "string",
                    "description": "Sự thay đổi cơ cấu sản phẩm/kênh ảnh hưởng đến doanh thu",
                },
                "gross_margin": {
                    "type": "number",
                    "description": "Biên lợi nhuận gộp (%)",
                },
                "ebitda_margin": {
                    "type": "number",
                    "description": "Biên EBITDA (%)",
                },
                "unit_economics": {
                    "type": ["object", "null"],
                    "description": "Chỉ số unit economics nếu có (CAC, LTV, AOV, churn rate,...)",
                    "additionalProperties": True,
                },
                "key_operational_metrics": {
                    "type": "array",
                    "description": "Các KPI vận hành quan trọng của doanh nghiệp",
                    "items": {"type": "string"},
                    "minItems": 3,
                },
            },
        }

    def get_output_model(self) -> Type[BusinessOpsOutput]:
        return BusinessOpsOutput
