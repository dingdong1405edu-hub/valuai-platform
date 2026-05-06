# ValuAI — Business Valuation Platform

Hệ thống định giá doanh nghiệp tự động dùng AI. Upload tài liệu → 8 AI agents phân tích song song → Xuất báo cáo PDF định giá chuyên nghiệp (12 chương).

---

## Cấu trúc hệ thống

```
valuai/
├── backend/          FastAPI + Celery + 8 AI agents
│   ├── app/
│   │   ├── agents/   8 Claude agents (company, financial, market, ops, mgmt, projection, valuation, risk)
│   │   ├── api/      REST endpoints (upload, reports, jobs, auth)
│   │   ├── models/   SQLAlchemy ORM (users, reports, documents)
│   │   ├── orchestrator/ Celery pipeline runner
│   │   ├── parsers/  PDF, Excel, DOCX extractors
│   │   ├── report/   Aggregator + WeasyPrint PDF builder + Jinja2 templates
│   │   └── schemas/  Pydantic (agent outputs + API I/O)
│   └── alembic/      DB migrations
└── frontend/         Next.js 14 App Router
    └── src/
        ├── app/      Pages (landing, auth, dashboard, upload, report/[id])
        ├── components/ DropZone, FileList, StatusTracker, UI primitives
        └── lib/      api.ts, supabase.ts, types.ts
```

---

## Yêu cầu trước khi chạy

| Dịch vụ | Mục đích |
|---|---|
| **Anthropic API Key** | AI agents gọi Claude |
| **Supabase project** | Auth + Storage (file upload + PDF) |
| **PostgreSQL** | Lưu reports, jobs, users |
| **Redis** | Celery task queue |

---

## Chạy local (Docker Compose)

### 1. Clone và cài đặt env

```bash
git clone <repo>
cd valuai
cp .env.example .env
# Mở .env và điền:
#   ANTHROPIC_API_KEY=sk-ant-...
#   SUPABASE_URL=https://xxxx.supabase.co
#   SUPABASE_SERVICE_KEY=eyJ...
#   SUPABASE_ANON_KEY=eyJ...
#   SECRET_KEY=<random-32-chars>
```

### 2. Cài đặt Supabase Storage bucket

Vào Supabase Dashboard → Storage → New bucket:
- Name: `valuai-documents`
- Public: **tắt** (private)

### 3. Khởi động services

```bash
# Build + start tất cả (db, redis, backend, worker, frontend)
docker compose up --build

# Hoặc chỉ infra (DB + Redis) rồi chạy app tay
docker compose up db redis -d
```

### 4. Chạy DB migrations

```bash
docker compose exec backend alembic upgrade head
```

### 5. Truy cập

- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Chạy local (không Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows
# hoặc: source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Cần PostgreSQL và Redis đang chạy local
# Tạo .env từ .env.example, điền đủ thông tin

# Start API server
uvicorn app.main:app --reload --port 8000

# Start Celery worker (terminal riêng)
celery -A app.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Điền NEXT_PUBLIC_API_URL, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY

npm run dev   # http://localhost:3000
```

---

## Deploy lên Railway

### Chuẩn bị

1. Tạo tài khoản [Railway](https://railway.app)
2. Install Railway CLI: `npm i -g @railway/cli`
3. Login: `railway login`

### Deploy

```bash
# Link project
railway init

# Add databases (Railway plugins)
railway add postgresql
railway add redis

# Set environment variables (Railway Dashboard → Variables)
# Cần set cho mỗi service:
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_ANON_KEY=eyJ...
SECRET_KEY=<random-32-chars>
CLAUDE_MODEL=claude-sonnet-4-6

# Deploy
railway up
```

### Services trên Railway

| Service | Source folder | Start command |
|---|---|---|
| `backend` | `./backend` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| `worker` | `./backend` | `celery -A app.celery_app worker --loglevel=info` |
| `frontend` | `./frontend` | `node server.js` |

Railway tự inject `DATABASE_URL` và `REDIS_URL` từ plugins → không cần set tay.

### Sau khi deploy backend lần đầu

```bash
# Chạy migrations
railway run --service backend alembic upgrade head
```

---

## Quy trình xử lý báo cáo

```
User upload files
    ↓
POST /api/upload  →  Lưu files vào Supabase Storage
    ↓
Celery enqueue task run_valuation_pipeline(report_id)
    ↓
PARSING  →  Extract text từ PDF/Excel/DOCX
    ↓
RUNNING_AGENTS  →  asyncio.gather chạy 6 agents song song:
    A1 CompanyProfileAgent
    A2 FinancialStatementAgent
    A3 MarketAnalysisAgent
    A4 BusinessOpsAgent
    A5 ManagementAgent
    A8 RiskAgent
    Sau đó sequential:
    A6 ProjectionAgent
    A7 ValuationAgent (nhận output A6)
    ↓
AGGREGATING  →  Gộp tất cả JSON
    ↓
BUILDING_PDF  →  Jinja2 → HTML → WeasyPrint → PDF
    ↓
Upload PDF → Supabase Storage
    ↓
DONE  →  Frontend polling nhận pdf_url, hiện nút download
```

---

## API Endpoints

| Method | Path | Mô tả |
|---|---|---|
| `POST` | `/api/auth/register` | Đăng ký |
| `POST` | `/api/auth/login` | Đăng nhập → JWT |
| `GET` | `/api/auth/me` | Thông tin user |
| `POST` | `/api/upload/` | Upload files → enqueue pipeline |
| `GET` | `/api/reports/` | Danh sách reports |
| `GET` | `/api/reports/{id}` | Chi tiết + signed PDF URL |
| `DELETE` | `/api/reports/{id}` | Xóa report |
| `GET` | `/api/jobs/{job_id}/status` | Poll trạng thái job |
| `GET` | `/health` | Health check |

---

## Biến môi trường

### Backend (bắt buộc)

| Biến | Ví dụ | Ghi chú |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db` | Phải dùng driver `asyncpg` |
| `REDIS_URL` | `redis://localhost:6379/0` | |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | |
| `SUPABASE_URL` | `https://xxxx.supabase.co` | |
| `SUPABASE_SERVICE_KEY` | `eyJ...` | Service role key |
| `SECRET_KEY` | 32+ ký tự random | Ký JWT tokens |

### Frontend (bắt buộc)

| Biến | Ví dụ |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://backend.railway.app` |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://xxxx.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJ...` anon/public key |

---

## Troubleshooting

**WeasyPrint lỗi font trên Linux:**
```bash
apt-get install -y fonts-liberation fonts-noto
```

**Celery không nhận task:**
- Kiểm tra `REDIS_URL` đúng format
- Đảm bảo worker import đúng: `celery -A app.celery_app worker`

**Agent timeout:**
- Tăng `max_tokens` trong `base.py` nếu document quá dài
- Mỗi doc bị cap ở 15,000 chars trong `_format_documents()`

**PDF trắng / thiếu section:**
- Agent trả `None` → section đó hiện "Không đủ dữ liệu"
- Xem log Celery worker để biết agent nào fail
