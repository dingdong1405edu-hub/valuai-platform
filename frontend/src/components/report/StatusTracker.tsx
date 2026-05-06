"use client";

import { useEffect, useRef, useState } from "react";
import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatElapsedTime } from "@/lib/utils";
import type { JobStatus } from "@/lib/types";

interface StatusTrackerProps {
  status: JobStatus;
  progress_pct: number;
  message: string;
}

const STEPS: { key: JobStatus; label: string; description: string }[] = [
  {
    key: "PARSING",
    label: "Đọc tài liệu",
    description: "Trích xuất nội dung từ tài liệu",
  },
  {
    key: "RUNNING_AGENTS",
    label: "AI phân tích",
    description: "Các AI agent phân tích đa chiều",
  },
  {
    key: "AGGREGATING",
    label: "Tổng hợp",
    description: "Kết hợp và đánh giá kết quả",
  },
  {
    key: "BUILDING_PDF",
    label: "Tạo báo cáo",
    description: "Xây dựng báo cáo PDF",
  },
  {
    key: "DONE",
    label: "Hoàn thành",
    description: "Báo cáo đã sẵn sàng",
  },
];

const STATUS_ORDER: JobStatus[] = [
  "PENDING",
  "PARSING",
  "RUNNING_AGENTS",
  "AGGREGATING",
  "BUILDING_PDF",
  "DONE",
];

function getStepState(
  stepKey: JobStatus,
  currentStatus: JobStatus
): "done" | "active" | "pending" {
  if (currentStatus === "FAILED") return "pending";
  const stepIdx = STATUS_ORDER.indexOf(stepKey);
  const currentIdx = STATUS_ORDER.indexOf(currentStatus);
  if (stepIdx < currentIdx) return "done";
  if (stepIdx === currentIdx) return "active";
  return "pending";
}

export function StatusTracker({
  status,
  progress_pct,
  message,
}: StatusTrackerProps) {
  const startRef = useRef<Date>(new Date());
  const [elapsed, setElapsed] = useState("0s");

  useEffect(() => {
    if (status === "DONE" || status === "FAILED") return;

    const interval = setInterval(() => {
      setElapsed(formatElapsedTime(startRef.current));
    }, 1000);

    return () => clearInterval(interval);
  }, [status]);

  const clampedPct = Math.max(0, Math.min(100, progress_pct));

  return (
    <div className="space-y-8">
      {/* Progress bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="font-medium text-navy-700">
            {status === "FAILED" ? "Xử lý thất bại" : message || "Đang xử lý..."}
          </span>
          <span className="text-navy-500 tabular-nums">
            {status === "DONE" ? "100%" : `${Math.round(clampedPct)}%`}
          </span>
        </div>
        <div className="h-3 w-full rounded-full bg-navy-100 overflow-hidden">
          <div
            className={cn(
              "h-full rounded-full transition-all duration-700 ease-out",
              status === "FAILED"
                ? "bg-red-500"
                : status === "DONE"
                ? "bg-green-500"
                : "bg-gradient-to-r from-brand-blue to-navy-600 animate-progress-pulse"
            )}
            style={{ width: `${status === "DONE" ? 100 : clampedPct}%` }}
          />
        </div>
      </div>

      {/* Step indicators */}
      <ol className="space-y-4">
        {STEPS.map((step) => {
          const state = getStepState(step.key, status);
          return (
            <li key={step.key} className="flex items-start gap-4">
              {/* Icon */}
              <div className="flex-shrink-0 mt-0.5">
                {state === "done" ? (
                  <div className="flex h-7 w-7 items-center justify-center rounded-full bg-green-500">
                    <Check className="h-4 w-4 text-white" strokeWidth={3} />
                  </div>
                ) : state === "active" ? (
                  <div className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-blue">
                    <Loader2 className="h-4 w-4 text-white animate-spin" />
                  </div>
                ) : (
                  <div className="flex h-7 w-7 items-center justify-center rounded-full bg-navy-100">
                    <div className="h-2 w-2 rounded-full bg-navy-300" />
                  </div>
                )}
              </div>

              {/* Text */}
              <div className="min-w-0 pt-0.5">
                <p
                  className={cn(
                    "text-sm font-semibold",
                    state === "done"
                      ? "text-green-700"
                      : state === "active"
                      ? "text-navy-900"
                      : "text-navy-400"
                  )}
                >
                  {step.label}
                </p>
                <p
                  className={cn(
                    "text-xs mt-0.5",
                    state === "pending" ? "text-navy-300" : "text-navy-500"
                  )}
                >
                  {step.description}
                </p>
              </div>
            </li>
          );
        })}
      </ol>

      {/* Time elapsed */}
      {status !== "DONE" && status !== "FAILED" && (
        <p className="text-center text-xs text-navy-400 tabular-nums">
          Thời gian đã xử lý: {elapsed}
        </p>
      )}
    </div>
  );
}
