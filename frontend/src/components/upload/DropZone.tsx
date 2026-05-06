"use client";

import { useCallback, useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { cn } from "@/lib/utils";

const ACCEPTED_TYPES = [
  "application/pdf",
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "text/plain",
  "text/csv",
];

const ACCEPTED_EXTENSIONS = [".pdf", ".xlsx", ".xls", ".docx", ".doc", ".txt", ".csv"];

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB
const MAX_FILES = 20;

interface DropZoneProps {
  onFilesAdded: (files: File[]) => void;
  currentCount?: number;
}

function validateFiles(
  files: File[],
  currentCount: number
): { valid: File[]; errors: string[] } {
  const errors: string[] = [];
  const valid: File[] = [];

  if (currentCount + files.length > MAX_FILES) {
    errors.push(`Tối đa ${MAX_FILES} file. Hiện đã có ${currentCount} file.`);
    return { valid, errors };
  }

  for (const file of files) {
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    const isValidType =
      ACCEPTED_TYPES.includes(file.type) ||
      ACCEPTED_EXTENSIONS.includes(ext);

    if (!isValidType) {
      errors.push(`"${file.name}" không được hỗ trợ.`);
      continue;
    }

    if (file.size > MAX_FILE_SIZE) {
      errors.push(`"${file.name}" vượt quá 50MB.`);
      continue;
    }

    valid.push(file);
  }

  return { valid, errors };
}

export function DropZone({ onFilesAdded, currentCount = 0 }: DropZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    (rawFiles: FileList | null) => {
      if (!rawFiles || rawFiles.length === 0) return;
      const fileArray = Array.from(rawFiles);
      const { valid, errors: errs } = validateFiles(fileArray, currentCount);
      setErrors(errs);
      if (valid.length > 0) {
        onFilesAdded(valid);
      }
    },
    [onFilesAdded, currentCount]
  );

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles]
  );

  const onInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      handleFiles(e.target.files);
      // Reset input so same file can be re-added after removal
      if (inputRef.current) inputRef.current.value = "";
    },
    [handleFiles]
  );

  return (
    <div className="space-y-3">
      <div
        role="button"
        tabIndex={0}
        aria-label="Kéo thả tài liệu vào đây hoặc nhấn để chọn file"
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        className={cn(
          "relative flex flex-col items-center justify-center gap-4",
          "min-h-[220px] w-full rounded-2xl border-2 border-dashed",
          "cursor-pointer transition-all duration-200 select-none",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-navy-500 focus-visible:ring-offset-2",
          isDragging
            ? "border-brand-blue bg-blue-50 scale-[1.01]"
            : "border-navy-300 bg-navy-50 hover:border-brand-blue hover:bg-blue-50"
        )}
      >
        <div
          className={cn(
            "flex h-16 w-16 items-center justify-center rounded-2xl transition-colors",
            isDragging ? "bg-brand-blue text-white" : "bg-navy-100 text-navy-600"
          )}
        >
          <UploadCloud className="h-8 w-8" />
        </div>
        <div className="text-center px-6">
          <p className="font-semibold text-navy-800">
            {isDragging ? "Thả file vào đây" : "Kéo & thả tài liệu"}
          </p>
          <p className="mt-1 text-sm text-navy-500">
            hoặc{" "}
            <span className="text-brand-blue font-medium underline underline-offset-2">
              nhấn để chọn file
            </span>
          </p>
          <p className="mt-3 text-xs text-navy-400">
            PDF, XLSX, XLS, DOCX, DOC, TXT, CSV · Tối đa 50MB/file · Tối đa 20 file
          </p>
        </div>

        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPTED_EXTENSIONS.join(",")}
          className="sr-only"
          onChange={onInputChange}
        />
      </div>

      {errors.length > 0 && (
        <div className="rounded-lg bg-red-50 border border-red-200 p-3 space-y-1">
          {errors.map((err, i) => (
            <p key={i} className="text-sm text-red-700 flex items-start gap-2">
              <span className="mt-0.5 flex-shrink-0">&#x26A0;</span>
              {err}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
