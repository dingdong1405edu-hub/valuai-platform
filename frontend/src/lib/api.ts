import { getToken } from "@/lib/auth";
import type {
  JobStatusResponse,
  Report,
  UploadedFile,
} from "@/lib/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchWithAuth(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getToken();

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> ?? {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      // ignore parse errors
    }
    throw new ApiError(response.status, message);
  }

  return response;
}

export const api = {
  async uploadDocuments(
    files: UploadedFile[],
    companyName: string
  ): Promise<{ report_id: string; job_id: string }> {
    const formData = new FormData();
    formData.append("company_name", companyName);

    files.forEach((uploadedFile) => {
      formData.append("files", uploadedFile.file);
      formData.append("doc_types", uploadedFile.docType);
    });

    const response = await fetchWithAuth("/api/upload/", {
      method: "POST",
      body: formData,
    });

    return response.json() as Promise<{ report_id: string; job_id: string }>;
  },

  async getReports(): Promise<Report[]> {
    const response = await fetchWithAuth("/api/reports");
    return response.json() as Promise<Report[]>;
  },

  async getReport(reportId: string): Promise<Report> {
    const response = await fetchWithAuth(`/api/reports/${reportId}`);
    return response.json() as Promise<Report>;
  },

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const response = await fetchWithAuth(`/api/jobs/${jobId}/status`);
    return response.json() as Promise<JobStatusResponse>;
  },

  async deleteReport(reportId: string): Promise<void> {
    await fetchWithAuth(`/api/reports/${reportId}`, { method: "DELETE" });
  },
};

export { ApiError };
