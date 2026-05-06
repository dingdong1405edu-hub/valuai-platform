import json
import logging
from typing import TypeVar, Type

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from app.config import get_settings

T = TypeVar("T", bound=BaseModel)


class BaseAgent:
    """
    Base class cho tất cả valuation agents.
    Dùng Claude tool_use để force structured JSON output.
    Bật prompt caching cho system prompt (cache_control).
    """

    AGENT_NAME: str = "base"

    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.CLAUDE_MODEL
        self.logger = logging.getLogger(f"agent.{self.AGENT_NAME}")

    def get_system_prompt(self) -> str:
        raise NotImplementedError

    def get_output_schema(self) -> dict:
        """Trả về JSON Schema cho tool definition."""
        raise NotImplementedError

    def get_output_model(self) -> Type[T]:
        raise NotImplementedError

    async def run(
        self,
        doc_context: dict[str, str],
        extra_context: dict | None = None,
    ) -> T:
        """
        Gọi Claude với tool_use để lấy structured output.

        Args:
            doc_context: Mapping doc_type → extracted_text.
            extra_context: Dữ liệu bổ sung (ví dụ projections cho valuation agent).

        Returns:
            Pydantic model đã validate theo get_output_model().
        """
        docs_text = self._format_documents(doc_context)
        if extra_context:
            docs_text += (
                "\n\n## DỮ LIỆU BỔ SUNG\n"
                + json.dumps(extra_context, ensure_ascii=False, indent=2)
            )

        tool_name = f"output_{self.AGENT_NAME}"

        self.logger.info("Calling Claude model=%s tool=%s", self.model, tool_name)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=[
                {
                    "type": "text",
                    "text": self.get_system_prompt(),
                    "cache_control": {"type": "ephemeral"},  # prompt caching
                }
            ],
            tools=[
                {
                    "name": tool_name,
                    "description": f"Output structured data từ {self.AGENT_NAME} agent",
                    "input_schema": self.get_output_schema(),
                }
            ],
            tool_choice={"type": "tool", "name": tool_name},
            messages=[{"role": "user", "content": docs_text}],
        )

        for block in response.content:
            if block.type == "tool_use":
                try:
                    result = self.get_output_model().model_validate(block.input)
                    self.logger.info(
                        "Agent %s completed successfully. Input tokens=%s, Output tokens=%s",
                        self.AGENT_NAME,
                        response.usage.input_tokens,
                        response.usage.output_tokens,
                    )
                    return result
                except Exception as exc:
                    self.logger.error(
                        "Validation error in agent %s: %s\nRaw input: %s",
                        self.AGENT_NAME,
                        exc,
                        json.dumps(block.input, ensure_ascii=False, indent=2),
                    )
                    raise

        raise ValueError(
            f"Agent {self.AGENT_NAME} did not receive a tool_use block in the response."
        )

    def _format_documents(self, doc_context: dict[str, str]) -> str:
        doc_type_labels: dict[str, str] = {
            "financial_report": "Báo cáo tài chính",
            "website_fanpage": "Website / Fanpage",
            "catalogue_brochure": "Catalogue / Brochure",
            "company_profile": "Hồ sơ năng lực",
            "business_plan": "Kế hoạch kinh doanh",
            "ceo_cv": "CV Chủ doanh nghiệp",
            "crm_export": "Dữ liệu CRM",
            "accounting_export": "Phần mềm kế toán",
            "erp_export": "Hệ thống ERP",
            "other": "Tài liệu khác",
        }
        parts = ["# TÀI LIỆU DOANH NGHIỆP\n"]
        for doc_type, text in doc_context.items():
            label = doc_type_labels.get(doc_type, doc_type)
            # Cap each document at 15 000 chars to stay within context limits
            parts.append(f"## {label}\n{text[:15000]}\n")
        return "\n".join(parts)
