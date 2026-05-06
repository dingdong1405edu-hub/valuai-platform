"use client";

import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { clearToken } from "@/lib/auth";

export function DashboardActions() {
  const router = useRouter();

  const handleSignOut = () => {
    clearToken();
    router.push("/login");
    router.refresh();
  };

  return (
    <button
      onClick={handleSignOut}
      className="inline-flex items-center gap-1.5 rounded-lg border border-navy-200 px-3 py-2 text-sm text-navy-600 hover:bg-navy-50 transition-colors"
      aria-label="Đăng xuất"
    >
      <LogOut className="h-4 w-4" />
      <span className="hidden sm:inline">Đăng xuất</span>
    </button>
  );
}
