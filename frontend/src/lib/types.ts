export type JobStatus =
  | "PENDING"
  | "PARSING"
  | "RUNNING_AGENTS"
  | "AGGREGATING"
  | "BUILDING_PDF"
  | "DONE"
  | "FAILED";

export type DocumentType =
  | "financial_report"
  | "website_fanpage"
  | "catalogue_brochure"
  | "company_profile"
  | "business_plan"
  | "ceo_cv"
  | "crm_export"
  | "accounting_export"
  | "erp_export"
  | "other";

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  financial_report: "Báo cáo tài chính",
  website_fanpage: "Website / Fanpage",
  catalogue_brochure: "Catalogue / Brochure",
  company_profile: "Hồ sơ năng lực",
  business_plan: "Kế hoạch kinh doanh (1-3 năm)",
  ceo_cv: "CV Chủ doanh nghiệp",
  crm_export: "Dữ liệu CRM",
  accounting_export: "Xuất phần mềm kế toán",
  erp_export: "Hệ thống ERP",
  other: "Tài liệu khác",
};

export const JOB_STATUS_LABELS: Record<JobStatus, string> = {
  PENDING: "Đang chờ xử lý",
  PARSING: "Đang đọc tài liệu",
  RUNNING_AGENTS: "AI đang phân tích",
  AGGREGATING: "Đang tổng hợp kết quả",
  BUILDING_PDF: "Đang tạo báo cáo PDF",
  DONE: "Hoàn thành",
  FAILED: "Thất bại",
};

export interface Report {
  id: string;
  company_name: string;
  status: JobStatus;
  created_at: string;
  updated_at: string;
  pdf_url: string | null;
  error_message: string | null;
  job_id: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  progress_pct: number;
  message: string;
  pdf_url: string | null;
  error_message: string | null;
}

export interface UploadedFile {
  file: File;
  docType: DocumentType;
  preview?: string;
}
