"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  ArrowRight,
  Building2,
  Upload,
  CheckCircle2,
  BarChart3,
  FileText,
} from "lucide-react";
import { DropZone } from "@/components/upload/DropZone";
import { FileList } from "@/components/upload/FileList";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { DOCUMENT_TYPE_LABELS } from "@/lib/types";
import type { DocumentType, UploadedFile } from "@/lib/types";
import { cn } from "@/lib/utils";

type Step = 1 | 2 | 3;

const STEPS = [
  { id: 1, label: "Thông tin", icon: Building2 },
  { id: 2, label: "Tài liệu", icon: Upload },
  { id: 3, label: "Xác nhận", icon: CheckCircle2 },
] as const;

export default function UploadPage() {
  const router = useRouter();

  const [step, setStep] = useState<Step>(1);
  const [companyName, setCompanyName] = useState("");
  const [companyNameError, setCompanyNameError] = useState("");
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Step 1 → 2
  const handleStep1Next = () => {
    if (!companyName.trim()) {
      setCompanyNameError("Vui lòng nhập tên doanh nghiệp.");
      return;
    }
    setCompanyNameError("");
    setStep(2);
  };

  // Step 2 → 3
  const handleStep2Next = () => {
    if (files.length === 0) return;
    setStep(3);
  };

  const handleFilesAdded = useCallback((newFiles: File[]) => {
    setFiles((prev) => [
      ...prev,
      ...newFiles.map((file) => ({
        file,
        docType: "other" as DocumentType,
      })),
    ]);
  }, []);

  const handleDocTypeChange = useCallback(
    (index: number, docType: DocumentType) => {
      setFiles((prev) =>
        prev.map((f, i) => (i === index ? { ...f, docType } : f))
      );
    },
    []
  );

  const handleRemoveFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const handleSubmit = async () => {
    setUploading(true);
    setUploadError(null);

    try {
      const { report_id } = await api.uploadDocuments(
        files,
        companyName.trim()
      );
      router.push(`/report/${report_id}`);
    } catch (err) {
      setUploadError(
        err instanceof Error
          ? err.message
          : "Đã có lỗi xảy ra. Vui lòng thử lại."
      );
      setUploading(false);
    }
  };

  // Group files by doc type for summary
  const filesByType = files.reduce<Partial<Record<DocumentType, number>>>(
    (acc, f) => {
      acc[f.docType] = (acc[f.docType] ?? 0) + 1;
      return acc;
    },
    {}
  );

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Nav */}
      <nav className="sticky top-0 z-40 border-b border-navy-100 bg-white shadow-sm">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4 sm:px-6">
          <Link href="/dashboard" className="flex items-center gap-2">
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
            Về dashboard
          </Link>
        </div>
      </nav>

      <main className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        {/* Step indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-center gap-0">
            {STEPS.map((s, idx) => (
              <div key={s.id} className="flex items-center">
                <div className="flex flex-col items-center gap-1.5">
                  <div
                    className={cn(
                      "flex h-10 w-10 items-center justify-center rounded-full transition-all",
                      step > s.id
                        ? "bg-green-500 text-white"
                        : step === s.id
                        ? "bg-navy-800 text-white shadow-md"
                        : "bg-navy-100 text-navy-400"
                    )}
                  >
                    {step > s.id ? (
                      <CheckCircle2 className="h-5 w-5" />
                    ) : (
                      <s.icon className="h-5 w-5" />
                    )}
                  </div>
                  <span
                    className={cn(
                      "text-xs font-medium",
                      step === s.id ? "text-navy-800" : "text-navy-400"
                    )}
                  >
                    {s.label}
                  </span>
                </div>
                {idx < STEPS.length - 1 && (
                  <div
                    className={cn(
                      "mx-2 mb-5 h-0.5 w-16 sm:w-24 transition-colors",
                      step > s.id ? "bg-green-400" : "bg-navy-200"
                    )}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="card p-6 sm:p-8">
          {/* Step 1: Basic info */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <h1 className="text-xl font-bold text-navy-800">
                  Thông tin doanh nghiệp
                </h1>
                <p className="mt-1 text-sm text-navy-500">
                  Nhập tên doanh nghiệp cần định giá.
                </p>
              </div>

              <div>
                <label htmlFor="companyName" className="label-base">
                  Tên doanh nghiệp <span className="text-red-500">*</span>
                </label>
                <input
                  id="companyName"
                  type="text"
                  value={companyName}
                  onChange={(e) => {
                    setCompanyName(e.target.value);
                    if (e.target.value.trim()) setCompanyNameError("");
                  }}
                  onKeyDown={(e) => e.key === "Enter" && handleStep1Next()}
                  className={cn(
                    "input-base",
                    companyNameError && "border-red-400 focus:ring-red-400"
                  )}
                  placeholder="VD: Công ty TNHH ABC"
                  autoFocus
                />
                {companyNameError && (
                  <p className="mt-1.5 text-sm text-red-600">
                    {companyNameError}
                  </p>
                )}
              </div>

              <div className="flex justify-end">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleStep1Next}
                >
                  Tiếp theo
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 2: Upload */}
          {step === 2 && (
            <div className="space-y-6">
              <div>
                <h1 className="text-xl font-bold text-navy-800">
                  Upload tài liệu
                </h1>
                <p className="mt-1 text-sm text-navy-500">
                  Tải lên các tài liệu liên quan đến{" "}
                  <span className="font-medium text-navy-700">
                    {companyName}
                  </span>
                  . Chọn loại tài liệu phù hợp cho mỗi file.
                </p>
              </div>

              <DropZone
                onFilesAdded={handleFilesAdded}
                currentCount={files.length}
              />

              <FileList
                files={files}
                onChange={handleDocTypeChange}
                onRemove={handleRemoveFile}
              />

              <div className="flex justify-between">
                <Button variant="secondary" onClick={() => setStep(1)}>
                  <ArrowLeft className="h-4 w-4" />
                  Quay lại
                </Button>
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleStep2Next}
                  disabled={files.length === 0}
                >
                  Tiếp theo
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Confirm */}
          {step === 3 && (
            <div className="space-y-6">
              <div>
                <h1 className="text-xl font-bold text-navy-800">
                  Xác nhận & Bắt đầu
                </h1>
                <p className="mt-1 text-sm text-navy-500">
                  Kiểm tra thông tin trước khi phân tích.
                </p>
              </div>

              {/* Summary */}
              <div className="rounded-xl border border-navy-200 bg-navy-50 p-5 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-navy-800">
                    <Building2 className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <p className="text-xs text-navy-400">Doanh nghiệp</p>
                    <p className="font-semibold text-navy-800">{companyName}</p>
                  </div>
                </div>

                <div className="border-t border-navy-200 pt-4">
                  <p className="text-xs font-medium text-navy-500 mb-3">
                    {files.length} tài liệu sẽ được phân tích
                  </p>
                  <ul className="space-y-1.5">
                    {(
                      Object.entries(filesByType) as [DocumentType, number][]
                    ).map(([type, count]) => (
                      <li
                        key={type}
                        className="flex items-center justify-between text-sm"
                      >
                        <span className="flex items-center gap-2 text-navy-700">
                          <FileText className="h-4 w-4 text-navy-400" />
                          {DOCUMENT_TYPE_LABELS[type]}
                        </span>
                        <span className="font-medium text-navy-800">
                          {count} file
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {uploadError && (
                <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm text-red-700">
                  {uploadError}
                </div>
              )}

              <div className="flex justify-between">
                <Button
                  variant="secondary"
                  onClick={() => setStep(2)}
                  disabled={uploading}
                >
                  <ArrowLeft className="h-4 w-4" />
                  Quay lại
                </Button>
                <Button
                  variant="primary"
                  size="lg"
                  onClick={handleSubmit}
                  loading={uploading}
                >
                  Bắt đầu phân tích
                </Button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
