import { cn } from "@/lib/utils";
import type { JobStatus } from "@/lib/types";

type BadgeVariant = "success" | "error" | "warning" | "info" | "default";

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const variantClasses: Record<BadgeVariant, string> = {
  success: "bg-green-100 text-green-800 border-green-200",
  error: "bg-red-100 text-red-800 border-red-200",
  warning: "bg-yellow-100 text-yellow-800 border-yellow-200",
  info: "bg-blue-100 text-blue-800 border-blue-200",
  default: "bg-gray-100 text-gray-700 border-gray-200",
};

export function Badge({ variant = "default", children, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium border",
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

export function JobStatusBadge({ status }: { status: JobStatus }) {
  const config: Record<JobStatus, { variant: BadgeVariant; label: string; dot: string }> = {
    PENDING: { variant: "default", label: "Đang chờ", dot: "bg-gray-400" },
    PARSING: { variant: "info", label: "Đang đọc tài liệu", dot: "bg-blue-500" },
    RUNNING_AGENTS: { variant: "info", label: "AI đang phân tích", dot: "bg-blue-600 animate-pulse" },
    AGGREGATING: { variant: "warning", label: "Đang tổng hợp", dot: "bg-yellow-500 animate-pulse" },
    BUILDING_PDF: { variant: "warning", label: "Đang tạo PDF", dot: "bg-yellow-600 animate-pulse" },
    DONE: { variant: "success", label: "Hoàn thành", dot: "bg-green-500" },
    FAILED: { variant: "error", label: "Thất bại", dot: "bg-red-500" },
  };

  const { variant, label, dot } = config[status];

  return (
    <Badge variant={variant}>
      <span className={cn("w-1.5 h-1.5 rounded-full flex-shrink-0", dot)} />
      {label}
    </Badge>
  );
}
