import pathlib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS

from app.schemas.agents import AggregatedReport
from app.report.charts import (
    revenue_ebitda_chart,
    revenue_breakdown_pie,
    sensitivity_heatmap,
    valuation_waterfall,
    projection_chart,
)

TEMPLATE_DIR = pathlib.Path(__file__).parent / "templates"

# ── Custom Jinja2 filters ──────────────────────────────────────────────────────

def _fmt_currency(value, decimals: int = 1) -> str:
    """Format float as Vietnamese currency string."""
    try:
        v = float(value)
        if abs(v) >= 1_000:
            return f"{v / 1_000:,.{decimals}f} nghìn tỷ"
        return f"{v:,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def _fmt_pct(value, decimals: int = 1) -> str:
    try:
        return f"{float(value):.{decimals}f}%"
    except (TypeError, ValueError):
        return str(value)


def _severity_badge(severity: str) -> str:
    mapping = {
        "high":   ("badge-high",    "Cao"),
        "medium": ("badge-medium",  "Trung bình"),
        "low":    ("badge-low",     "Thấp"),
    }
    cls, label = mapping.get((severity or "").lower(), ("badge-medium", severity))
    return f'<span class="{cls}">{label}</span>'


# ── Builder ────────────────────────────────────────────────────────────────────

def build_pdf(report: AggregatedReport) -> bytes:
    """
    Render Jinja2 template → HTML → WeasyPrint → PDF bytes.
    Trả về bytes của PDF file.
    """
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["fmt_currency"] = _fmt_currency
    env.filters["fmt_pct"]      = _fmt_pct
    env.filters["severity_badge"] = _severity_badge

    template = env.get_template("report.html")

    # ── Build charts (SVG strings) ────────────────────────────────────────────
    charts: dict[str, str] = {}

    if report.financials and report.financials.years:
        charts["revenue_ebitda"] = revenue_ebitda_chart(
            [y.model_dump() for y in report.financials.years]
        )

    if report.projections and report.projections.base_case:
        charts["projection"] = projection_chart(
            [y.model_dump() for y in report.projections.base_case]
        )

    if report.valuation:
        v = report.valuation
        charts["valuation_compare"] = valuation_waterfall(
            dcf_value=v.dcf.equity_value,
            multiples_value=v.multiples.implied_ev_from_ebitda,
            final_low=v.final_value_low,
            final_high=v.final_value_high,
        )
        charts["sensitivity"] = sensitivity_heatmap(
            v.sensitivity.model_dump()
        )

    if report.business_ops and report.business_ops.revenue_by_product:
        charts["revenue_pie"] = revenue_breakdown_pie(
            [s.model_dump() for s in report.business_ops.revenue_by_product],
            "Cơ cấu doanh thu theo sản phẩm",
        )

    # ── Render ────────────────────────────────────────────────────────────────
    html_content = template.render(report=report, charts=charts)

    pdf_bytes = HTML(string=html_content).write_pdf(
        stylesheets=[
            CSS(string="@page { size: A4; margin: 2cm 1.8cm; }")
        ]
    )
    return pdf_bytes
