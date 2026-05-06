"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Download,
  RefreshCw,
  BarChart3,
  AlertCircle,
} from "lucide-react";
import { api } from "@/lib/api";
import { StatusTracker } from "@/components/report/StatusTracker";
import { Button } from "@/components/ui/Button";
import { JobStatusBadge } from "@/components/ui/Badge";
import type { JobStatus, JobStatusResponse, Report } from "@/lib/types";

const POLL_INTERVAL_MS = 3000;
const TERMINAL_STATUSES: JobStatus[] = ["DONE", "FAILED"];

export default function ReportPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const reportId = params.id;

  const [report, setReport] = useState<Report | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loadingInitial, setLoadingInitial] = useState(true);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const pollStatus = useCallback(
    async (jobId: string) => {
      try {
        const status = await api.getJobStatus(jobId);
        setJobStatus(status);

        if (TERMINAL_STATUSES.includes(status.status)) {
          stopPolling();
          // Refresh report for latest pdf_url / error_message
          const updatedReport = await api.getReport(reportId);
          setReport(updatedReport);
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    },
    [reportId, stopPolling]
  );

  // Initial load
  useEffect(() => {
    let cancelled = false;

    const initialize = async () => {
      try {
        const r = await api.getReport(reportId);
        if (cancelled) return;
        setReport(r);

        // Seed initial job status from report
        setJobStatus({
          job_id: r.job_id,
          status: r.status,
          progress_pct:
            r.status === "DONE" ? 100 : r.status === "FAILED" ? 0 : 0,
          message: "",
          pdf_url: r.pdf_url,
          error_message: r.error_message,
        });

        // If not terminal, begin polling
        if (!TERMINAL_STATUSES.includes(r.status)) {
          // Immediate first poll
          await pollStatus(r.job_id);
          if (cancelled) return;

          intervalRef.current = setInterval(() => {
            void pollStatus(r.job_id);
          }, POLL_INTERVAL_MS);
        }
      } catch (err) {
        if (!cancelled) {
          setLoadError(
            err instanceof Error ? err.message : "Không thể tải báo cáo."
          );
        }
      } finally {
        if (!cancelled) setLoadingInitial(false);
      }
    };

    void initialize();

    return () => {
      cancelled = true;
      stopPolling();
    };
  }, [reportId, pollStatus, stopPolling]);

  const handleRetry = () => {
    router.push("/upload");
  };

  const currentStatus = jobStatus?.status ?? report?.status ?? "PENDING";
  const progressPct = jobStatus?.progress_pct ?? 0;
  const message = jobStatus?.message ?? "";
  const pdfUrl = report?.pdf_url ?? jobStatus?.pdf_url ?? null;
  const errorMessage = report?.error_message ?? null;

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Nav */}
      <nav className="sticky top-0 z-40 border-b border-navy-100 bg-white shadow-sm">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-navy-800">
              <BarChart3 className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold text-navy-800">ValuAI</span>
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 text-sm text-navy-500 hover:text-navy-700"
          >
            <ArrowLeft className="h-4 w-4" />
            Dashboard
          </Link>
        </div>
      </nav>

      <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        {loadingInitial ? (
          <div className="card p-12 flex flex-col items-center gap-4">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-navy-200 border-t-navy-800" />
            <p className="text-navy-500">Đang tải thông tin báo cáo...</p>
          </div>
        ) : loadError ? (
          <div className="card p-8 text-center space-y-4">
            <AlertCircle className="mx-auto h-12 w-12 text-red-400" />
            <h1 className="text-lg font-semibold text-navy-800">
              Không thể tải báo cáo
            </h1>
            <p className="text-sm text-navy-500">{loadError}</p>
            <div className="flex justify-center gap-3">
              <Button variant="secondary" onClick={() => router.back()}>
                <ArrowLeft className="h-4 w-4" />
                Quay lại
              </Button>
              <Button
                variant="primary"
                onClick={() => window.location.reload()}
              >
                <RefreshCw className="h-4 w-4" />
                Thử lại
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Report header */}
            <div className="card p-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs text-navy-400 mb-1">Báo cáo định giá</p>
                  <h1 className="text-xl font-bold text-navy-800">
                    {report?.company_name ?? "..."}
                  </h1>
                </div>
                <JobStatusBadge status={currentStatus} />
              </div>
            </div>

            {/* Progress card */}
            <div className="card p-6 sm:p-8">
              <h2 className="text-base font-semibold text-navy-800 mb-6">
                Tiến trình xử lý
              </h2>
              <StatusTracker
                status={currentStatus}
                progress_pct={progressPct}
                message={message}
              />
            </div>

            {/* Done state */}
            {currentStatus === "DONE" && (
              <div className="card p-6 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                <div className="flex flex-col items-center text-center gap-4">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-green-500 shadow-md">
                    <Download className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-green-800">
                      Báo cáo đã hoàn thành!
                    </h2>
                    <p className="mt-1.5 text-sm text-green-700">
                      Báo cáo định giá doanh nghiệp đã sẵn sàng để tải xuống.
                    </p>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
                    {pdfUrl ? (
                      <a
                        href={pdfUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center justify-center gap-2 rounded-xl bg-green-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-green-700 transition-colors"
                      >
                        <Download className="h-4 w-4" />
                        Tải báo cáo PDF
                      </a>
                    ) : (
                      <p className="text-sm text-green-600 italic">
                        Link PDF đang được tạo...
                      </p>
                    )}
                    <Link
                      href="/dashboard"
                      className="inline-flex items-center justify-center gap-2 rounded-xl border border-green-300 bg-white px-6 py-3 text-sm font-medium text-green-700 hover:bg-green-50 transition-colors"
                    >
                      <ArrowLeft className="h-4 w-4" />
                      Về dashboard
                    </Link>
                  </div>
                </div>
              </div>
            )}

            {/* Failed state */}
            {currentStatus === "FAILED" && (
              <div className="card p-6 bg-red-50 border-red-200">
                <div className="flex flex-col items-center text-center gap-4">
                  <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-red-100">
                    <AlertCircle className="h-8 w-8 text-red-500" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-red-800">
                      Xử lý thất bại
                    </h2>
                    {errorMessage && (
                      <p className="mt-2 text-sm text-red-600 max-w-md">
                        {errorMessage}
                      </p>
                    )}
                  </div>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <Button variant="danger" onClick={handleRetry}>
                      <RefreshCw className="h-4 w-4" />
                      Thử lại
                    </Button>
                    <Link
                      href="/dashboard"
                      className="inline-flex items-center justify-center gap-2 rounded-xl border border-red-300 bg-white px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50 transition-colors"
                    >
                      <ArrowLeft className="h-4 w-4" />
                      Về dashboard
                    </Link>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
