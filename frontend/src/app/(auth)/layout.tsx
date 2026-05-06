import Link from "next/link";
import { BarChart3 } from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-900 via-navy-800 to-brand-blue flex flex-col">
      {/* Header */}
      <div className="p-6">
        <Link href="/" className="inline-flex items-center gap-2 text-white">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/20">
            <BarChart3 className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold">ValuAI</span>
        </Link>
      </div>

      {/* Centered card */}
      <div className="flex flex-1 items-center justify-center px-4 pb-10">
        <div className="w-full max-w-md">
          <div className="card p-8 shadow-2xl">{children}</div>
        </div>
      </div>

      {/* Footer */}
      <div className="py-4 text-center text-sm text-white/40">
        &copy; {new Date().getFullYear()} ValuAI
      </div>
    </div>
  );
}
