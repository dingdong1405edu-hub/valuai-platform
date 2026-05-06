# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Mục tiêu hệ thống

Nền tảng định giá doanh nghiệp tự động (Business Valuation Platform). User upload các tài liệu doanh nghiệp → pipeline multi-agent phân tích độc lập → tổng hợp thành báo cáo định giá chuyên nghiệp (PDF 12 chương).

---

## Tech Stack

| Layer | Công nghệ |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Backend API | FastAPI (Python 3.11+) |
| Agent Orchestration | LangGraph (multi-agent graph) + Claude API (claude-sonnet-4-6) |
| Job Queue | Celery + Redis |
| Database | PostgreSQL (Supabase hoặc self-hosted) |
| File Storage | Supabase Storage hoặc S3-compatible |
| PDF Generation | WeasyPrint hoặc Puppeteer (HTML → PDF) |
| Auth | Supabase Auth (JWT) |

---

## Development Commands

### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev          # localhost:3000
npm run build
npm run lint
npm run type-check   # tsc --noEmit
```

### Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Agent Worker (Celery)
```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

### Database Migrations (Alembic)
```bash
cd backend
alembic upgrade head
alembic revision --autogenerate -m "description"
```

### Run single test
```bash
cd backend
pytest tests/agents/test_financial_agent.py -v
pytest tests/ -k "test_dcf" -v

cd frontend
npx jest src/components/ReportViewer.test.tsx
```

### Docker (full stack)
```bash
docker compose up --build
docker compose up db redis -d   # chỉ chạy infra
```

---

## Kiến trúc Tổng quan

```
User Upload Documents
        │
        ▼
[ FastAPI Ingestion API ]
  - Parse PDF/Excel/DOCX
  - Extract text + tables
  - Store raw files → Supabase Storage
  - Enqueue Celery job
        │
        ▼
[ LangGraph Orchestrator ]  ← central controller
  Chạy các agent song song (fan-out), mỗi agent nhả JSON
        │
   ┌────┼────┬────┬────┬────┬────┬────┐
   ▼    ▼    ▼    ▼    ▼    ▼    ▼    ▼
 [A1] [A2] [A3] [A4] [A5] [A6] [A7] [A8]
        │
        ▼
[ Aggregator Agent ]  ← fan-in, ghép tất cả JSON
        │
        ▼
[ Report Builder ]
  - Render Jinja2 HTML templates
  - WeasyPrint → PDF
  - Upload PDF → Storage
        │
        ▼
[ Frontend ] ← polling job status, download PDF
```

---

## Agent Pipeline

Mỗi agent là một LangGraph node độc lập. Chúng nhận `DocumentContext` (text đã extract) và trả về JSON theo schema riêng. Không agent nào phụ thuộc trực tiếp vào output của agent khác — tất cả chờ Aggregator.

| ID | Agent | Input chính | Output JSON key |
|---|---|---|---|
| A1 | `CompanyProfileAgent` | Website, hồ sơ năng lực, brochure | `company_profile` |
| A2 | `FinancialStatementAgent` | Báo cáo tài chính, phần mềm kế toán | `financials` |
| A3 | `MarketAnalysisAgent` | Ngành nghề, CRM, kế hoạch KD | `market_analysis` |
| A4 | `BusinessOpsAgent` | Catalogue, ERP, kế hoạch KD | `business_ops` |
| A5 | `ManagementAgent` | CV chủ DN, hồ sơ năng lực | `management` |
| A6 | `ProjectionAgent` | Tài chính lịch sử + kế hoạch KD | `projections` |
| A7 | `ValuationAgent` | Output của ProjectionAgent + multiples ngành | `valuation` |
| A8 | `RiskAgent` | Tất cả tài liệu | `risks` |

**Lưu ý quan trọng:** `ValuationAgent` (A7) và `ProjectionAgent` (A6) phải chạy **tuần tự** (A6 → A7). Tất cả agent khác chạy song song.

---

## Cấu trúc thư mục

```
valuai/
├── frontend/               # Next.js app
│   ├── app/
│   │   ├── (auth)/        # login, register
│   │   ├── dashboard/     # danh sách reports
│   │   ├── upload/        # wizard upload tài liệu
│   │   └── report/[id]/   # xem + download PDF
│   ├── components/
│   │   ├── upload/        # DropZone, FileList, ProgressBar
│   │   └── report/        # ReportViewer, SectionNav
│   └── lib/
│       └── api.ts         # typed fetch client → backend
│
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI app + routers
│   │   ├── celery_app.py  # Celery config
│   │   ├── api/
│   │   │   ├── upload.py  # POST /api/upload
│   │   │   ├── reports.py # GET /api/reports/{id}
│   │   │   └── jobs.py    # GET /api/jobs/{id}/status
│   │   ├── agents/
│   │   │   ├── base.py           # BaseAgent abstract class
│   │   │   ├── company_profile.py
│   │   │   ├── financial_statement.py
│   │   │   ├── market_analysis.py
│   │   │   ├── business_ops.py
│   │   │   ├── management.py
│   │   │   ├── projection.py
│   │   │   ├── valuation.py
│   │   │   └── risk.py
│   │   ├── orchestrator/
│   │   │   ├── graph.py   # LangGraph definition
│   │   │   └── runner.py  # Celery task gọi graph
│   │   ├── parsers/
│   │   │   ├── pdf_parser.py
│   │   │   ├── excel_parser.py
│   │   │   └── docx_parser.py
│   │   ├── report/
│   │   │   ├── aggregator.py     # ghép JSONs
│   │   │   ├── builder.py        # Jinja2 + WeasyPrint
│   │   │   └── templates/        # HTML templates từng section
│   │   ├── models/        # SQLAlchemy ORM models
│   │   └── schemas/       # Pydantic schemas (agent outputs)
│   ├── tests/
│   └── alembic/
│
└── docker-compose.yml
```

---

## Agent Output Schemas (Pydantic)

Tất cả agent output phải match schema trong `backend/app/schemas/`. Aggregator validate toàn bộ trước khi build PDF.

```python
# Ví dụ schemas/valuation.py
class DCFResult(BaseModel):
    fcf_projections: list[float]       # 5 năm
    wacc: float
    terminal_growth_rate: float
    enterprise_value: float
    equity_value: float

class MultiplesResult(BaseModel):
    ev_ebitda: float
    pe_ratio: float
    pb_ratio: float
    comparable_companies: list[str]

class ValuationOutput(BaseModel):
    dcf: DCFResult
    multiples: MultiplesResult
    final_value_range: tuple[float, float]
    sensitivity_matrix: dict            # WACC × growth grid
```

---

## Cấu trúc Báo cáo (12 Section → PDF)

Report builder map từng JSON key sang HTML template tương ứng:

| Section | Template | JSON keys dùng |
|---|---|---|
| 1. Executive Summary | `executive_summary.html` | tất cả (summary) |
| 2. Investment Thesis | `investment_thesis.html` | `market_analysis`, `financials`, `risks` |
| 3. Business Overview | `business_overview.html` | `company_profile`, `management` |
| 4. Market Analysis | `market_analysis.html` | `market_analysis` |
| 5. Business Operations | `business_ops.html` | `business_ops` |
| 6. Financial Analysis | `financial_analysis.html` | `financials` |
| 7. Financial Ratios | `ratios.html` | `financials` |
| 8. Projections | `projections.html` | `projections` |
| 9. Valuation | `valuation.html` | `valuation` |
| 10. Sensitivity | `sensitivity.html` | `valuation.sensitivity_matrix` |
| 11. Conclusion | `conclusion.html` | `valuation`, `risks` |
| 12. Appendix | `appendix.html` | tất cả (raw assumptions) |

---

## Job Status Flow

```
PENDING → PARSING → RUNNING_AGENTS → AGGREGATING → BUILDING_PDF → DONE
                                                                  → FAILED
```

Frontend poll `GET /api/jobs/{id}/status` mỗi 3 giây. Khi `DONE`, hiển thị download link.

---

## Biến môi trường quan trọng

```env
# backend/.env
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379/0
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
ANTHROPIC_API_KEY=...
CLAUDE_MODEL=claude-sonnet-4-6

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=...
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
```

---

## Nguyên tắc thiết kế Agent

- Mỗi agent **không gọi agent khác** — chỉ nhận `DocumentContext`, gọi Claude API, trả JSON.
- Dùng **structured output** (`response_format` với Pydantic schema) để đảm bảo JSON hợp lệ.
- Prompt của mỗi agent nằm trong file `agents/<name>.py`, không hardcode ở orchestrator.
- Nếu agent thất bại, orchestrator log lỗi và điền `null` cho key đó — report vẫn build được với section thiếu được đánh dấu rõ.
- Tất cả Claude API calls phải bật **prompt caching** (`cache_control`) cho system prompt vì các document context dài.

---

## PDF Generation

- HTML templates dùng **Jinja2**, render với aggregated JSON.
- CSS dùng print media queries cho pagination, page breaks giữa các section.
- Chart/biểu đồ: render server-side bằng **Matplotlib → SVG** nhúng inline vào HTML (không dùng JS chart).
- WeasyPrint build PDF từ HTML đã render.
- Sensitivity table (Section 10) là HTML table, không phải chart.
