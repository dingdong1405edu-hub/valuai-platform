"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Eye, Download, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import { JobStatusBadge } from "@/components/ui/Badge";
import { formatDate } from "@/lib/utils";
import type { Report } from "@/lib/types";

export function ReportCardClient({ report }: { report: Report }) {
  const router = useRouter();
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm(`Xóa báo cáo "${report.company_name}"?`)) return;
    setDeleting(true);
    try {
      await api.deleteReport(report.id);
      router.refresh();
    } catch (err) {
      alert(err instanceof Error ? err.message : "Xóa thất bại.");
      setDeleting(false);
    }
  };

  return (
    <div className="card p-5 hover:shadow-md transition-shadow flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h2
            className="font-semibold text-navy-800 truncate"
            title={report.company_name}
          >
            {report.company_name}
          </h2>
          <p className="mt-0.5 text-xs text-navy-400">
            {formatDate(report.created_at)}
          </p>
        </div>
        <JobStatusBadge status={report.status} />
      </div>

      {report.error_message && (
        <p className="rounded-lg bg-red-50 border border-red-100 px-3 py-2 text-xs text-red-600 leading-relaxed">
          {report.error_message}
        </p>
      )}

      <div className="mt-auto flex items-center gap-2 pt-1 border-t border-navy-50">
        <Link
          href={`/report/${report.id}`}
          className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg border border-navy-200 px-3 py-2 text-xs font-medium text-navy-700 hover:bg-navy-50 transition-colors"
        >
          <Eye className="h-3.5 w-3.5" />
          Xem
        </Link>

        {report.status === "DONE" && report.pdf_url && (
          <a
            href={report.pdf_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-lg bg-green-50 border border-green-200 px-3 py-2 text-xs font-medium text-green-700 hover:bg-green-100 transition-colors"
          >
            <Download className="h-3.5 w-3.5" />
            PDF
          </a>
        )}

        <button
          onClick={handleDelete}
          disabled={deleting}
          className="inline-flex items-center justify-center rounded-lg border border-red-100 bg-red-50 p-2 text-red-500 hover:bg-red-100 hover:text-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Xóa báo cáo"
        >
          {deleting ? (
            <svg
              className="h-3.5 w-3.5 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
          ) : (
            <Trash2 className="h-3.5 w-3.5" />
          )}
        </button>
      </div>
    </div>
  );
}
