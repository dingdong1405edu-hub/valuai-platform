"use client";

import { FileText, FileSpreadsheet, File, X } from "lucide-react";
import { DOCUMENT_TYPE_LABELS } from "@/lib/types";
import type { DocumentType, UploadedFile } from "@/lib/types";
import { formatFileSize } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface FileListProps {
  files: UploadedFile[];
  onChange: (index: number, docType: DocumentType) => void;
  onRemove: (index: number) => void;
}

function getFileIcon(file: File) {
  const ext = file.name.split(".").pop()?.toLowerCase();
  if (ext === "pdf") {
    return <FileText className="h-5 w-5 text-red-500 flex-shrink-0" />;
  }
  if (["xlsx", "xls", "csv"].includes(ext ?? "")) {
    return <FileSpreadsheet className="h-5 w-5 text-green-600 flex-shrink-0" />;
  }
  return <File className="h-5 w-5 text-blue-500 flex-shrink-0" />;
}

const documentTypeOptions = Object.entries(DOCUMENT_TYPE_LABELS) as [
  DocumentType,
  string
][];

export function FileList({ files, onChange, onRemove }: FileListProps) {
  if (files.length === 0) return null;

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-navy-700">
        {files.length} file đã chọn
      </p>
      <ul className="space-y-2">
        {files.map((uploadedFile, index) => (
          <li
            key={`${uploadedFile.file.name}-${index}`}
            className={cn(
              "flex items-center gap-3 rounded-xl border border-navy-200",
              "bg-white p-3 shadow-sm"
            )}
          >
            {getFileIcon(uploadedFile.file)}

            <div className="min-w-0 flex-1">
              <p
                className="truncate text-sm font-medium text-navy-800"
                title={uploadedFile.file.name}
              >
                {uploadedFile.file.name}
              </p>
              <p className="text-xs text-navy-400 mt-0.5">
                {formatFileSize(uploadedFile.file.size)}
              </p>
            </div>

            <select
              value={uploadedFile.docType}
              onChange={(e) => onChange(index, e.target.value as DocumentType)}
              className={cn(
                "flex-shrink-0 rounded-lg border border-navy-200 bg-navy-50 px-2 py-1.5",
                "text-xs text-navy-700 focus:outline-none focus:ring-2 focus:ring-navy-500",
                "cursor-pointer max-w-[180px]"
              )}
              aria-label={`Loại tài liệu cho ${uploadedFile.file.name}`}
            >
              {documentTypeOptions.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>

            <button
              onClick={() => onRemove(index)}
              aria-label={`Xóa ${uploadedFile.file.name}`}
              className={cn(
                "flex-shrink-0 rounded-lg p-1.5 text-navy-400",
                "hover:bg-red-50 hover:text-red-600 transition-colors",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
              )}
            >
              <X className="h-4 w-4" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
