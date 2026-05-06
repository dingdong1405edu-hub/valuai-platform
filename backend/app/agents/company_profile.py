from typing import Type

from app.agents.base import BaseAgent, T
from app.schemas.agents import CompanyProfileOutput


class CompanyProfileAgent(BaseAgent):
    """
    A1 – Trích xuất hồ sơ doanh nghiệp (tên, ngành, lịch sử, cổ đông,
    ban lãnh đạo, sản phẩm/dịch vụ, mô hình doanh thu, chuỗi giá trị).
    """

    AGENT_NAME = "company_profile"

    def get_system_prompt(self) -> str:
        return (
            "Bạn là chuyên gia phân tích doanh nghiệp. "
            "Hãy đọc các tài liệu được cung cấp và trích xuất thông tin hồ sơ doanh nghiệp "
            "đầy đủ và chính xác nhất có thể. "
            "Nếu thông tin không có trong tài liệu, hãy để giá trị mặc định hợp lý thay vì bịa đặt. "
            "Trả về kết quả bằng cách gọi tool được chỉ định."
        )

    def get_output_schema(self) -> dict:
        return {
            "type": "object",
            "required": [
                "company_name",
                "industry",
                "sub_industry",
                "headquarters",
                "description",
                "history",
                "shareholders",
                "executives",
                "products_services",
                "revenue_model",
                "value_chain_input",
                "value_chain_production",
                "value_chain_distribution",
                "value_chain_customer",
            ],
            "properties": {
                "company_name": {"type": "string", "description": "Tên đầy đủ của doanh nghiệp"},
                "founded_year": {"type": ["integer", "null"], "description": "Năm thành lập"},
                "industry": {"type": "string", "description": "Ngành kinh doanh chính"},
                "sub_industry": {"type": "string", "description": "Phân ngành cụ thể"},
                "headquarters": {"type": "string", "description": "Địa chỉ trụ sở chính"},
                "description": {"type": "string", "description": "Mô tả tổng quát về doanh nghiệp"},
                "history": {"type": "string", "description": "Lịch sử hình thành và phát triển"},
                "shareholders": {
                    "type": "array",
                    "description": "Danh sách cổ đông chính",
                    "items": {
                        "type": "object",
                        "required": ["name", "percentage"],
                        "properties": {
                            "name": {"type": "string"},
                            "percentage": {"type": "number", "minimum": 0, "maximum": 100},
                            "role": {"type": ["string", "null"]},
                        },
                    },
                },
                "executives": {
                    "type": "array",
                    "description": "Danh sách lãnh đạo chủ chốt",
                    "items": {
                        "type": "object",
                        "required": ["name", "title", "background"],
                        "properties": {
                            "name": {"type": "string"},
                            "title": {"type": "string"},
                            "background": {"type": "string"},
                        },
                    },
                },
                "products_services": {
                    "type": "array",
                    "description": "Danh sách sản phẩm/dịch vụ",
                    "items": {"type": "string"},
                },
                "revenue_model": {"type": "string", "description": "Mô hình tạo doanh thu"},
                "value_chain_input": {
                    "type": "string",
                    "description": "Chuỗi giá trị - Đầu vào (nguyên vật liệu, nhà cung cấp)",
                },
                "value_chain_production": {
                    "type": "string",
                    "description": "Chuỗi giá trị - Sản xuất/vận hành",
                },
                "value_chain_distribution": {
                    "type": "string",
                    "description": "Chuỗi giá trị - Phân phối/bán hàng",
                },
                "value_chain_customer": {
                    "type": "string",
                    "description": "Chuỗi giá trị - Khách hàng/dịch vụ sau bán",
                },
            },
        }

    def get_output_model(self) -> Type[CompanyProfileOutput]:
        return CompanyProfileOutput
