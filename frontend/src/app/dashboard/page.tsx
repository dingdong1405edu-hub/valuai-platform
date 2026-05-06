import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import Link from "next/link";
import { Plus, FileText, BarChart3 } from "lucide-react";
import type { Report } from "@/lib/types";
import { DashboardActions } from "./DashboardActions";
import { ReportCardClient } from "./ReportCard";

export const dynamic = "force-dynamic";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchReports(token: string): Promise<Report[]> {
  try {
    const res = await fetch(`${API_BASE}/api/reports`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!res.ok) return [];
    return (await res.json()) as Report[];
  } catch {
    return [];
  }
}

export default async function DashboardPage() {
  const cookieStore = await cookies();
  const token = cookieStore.get("valuai_token")?.value;

  if (!token) redirect("/login");

  // Verify token is valid
  const meResp = await fetch(`${API_BASE}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!meResp.ok) redirect("/login");

  const user = await meResp.json() as { id: string; email: string; full_name: string };
  const reports = await fetchReports(token);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top nav */}
      <nav className="sticky top-0 z-40 border-b border-navy-100 bg-white shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-navy-800">
              <BarChart3 className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold text-navy-800">ValuAI</span>
          </Link>
          <div className="flex items-center gap-3">
            <span className="hidden text-sm text-navy-500 sm:block">
              {user.email}
            </span>
            <DashboardActions />
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-navy-800">Báo cáo của tôi</h1>
            <p className="mt-1 text-sm text-navy-500">
              {reports.length > 0 ? `${reports.length} báo cáo` : "Chưa có báo cáo nào"}
            </p>
          </div>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 rounded-xl bg-navy-800 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-navy-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Tạo báo cáo mới
          </Link>
        </div>

        {reports.length === 0 ? (
          <div className="card flex flex-col items-center justify-center gap-5 py-20 text-center">
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-navy-100">
              <FileText className="h-10 w-10 text-navy-400" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-navy-700">Chưa có báo cáo nào</h2>
              <p className="mt-1 text-sm text-navy-400 max-w-sm">
                Bắt đầu bằng cách tải lên tài liệu doanh nghiệp để nhận báo cáo định giá AI.
              </p>
            </div>
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 rounded-xl bg-navy-800 px-5 py-2.5 text-sm font-semibold text-white hover:bg-navy-700 transition-colors"
            >
              <Plus className="h-4 w-4" />
              Tạo báo cáo đầu tiên
            </Link>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {reports.map((report) => (
              <ReportCardClient key={report.id} report={report} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
