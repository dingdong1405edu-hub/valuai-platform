"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Eye, EyeOff, UserPlus } from "lucide-react";
import { setToken } from "@/lib/auth";
import { Button } from "@/components/ui/Button";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validate = (): string | null => {
    if (!fullName.trim()) return "Vui lòng nhập họ tên.";
    if (!email.trim()) return "Vui lòng nhập email.";
    if (password.length < 6) return "Mật khẩu phải có ít nhất 6 ký tự.";
    if (password !== confirmPassword) return "Mật khẩu xác nhận không khớp.";
    return null;
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    try {
      const resp = await fetch(`${API_BASE}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password, full_name: fullName.trim() }),
      });

      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        setError((body as { detail?: string }).detail || "Đã có lỗi xảy ra.");
        return;
      }

      // Auto-login after register
      const loginResp = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      if (loginResp.ok) {
        const { access_token } = await loginResp.json() as { access_token: string };
        setToken(access_token);
        router.push("/dashboard");
        router.refresh();
      } else {
        router.push("/login");
      }
    } catch {
      setError("Đã có lỗi xảy ra. Vui lòng thử lại.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-navy-800">Tạo tài khoản</h1>
        <p className="mt-2 text-sm text-navy-500">
          Đã có tài khoản?{" "}
          <Link href="/login" className="font-medium text-brand-blue hover:underline">
            Đăng nhập
          </Link>
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        {error && (
          <div className="rounded-xl bg-red-50 border border-red-200 p-3.5 text-sm text-red-700">
            {error}
          </div>
        )}

        <div>
          <label htmlFor="fullName" className="label-base">Họ và tên</label>
          <input
            id="fullName"
            type="text"
            autoComplete="name"
            required
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="input-base"
            placeholder="Nguyễn Văn A"
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="email" className="label-base">Email</label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-base"
            placeholder="you@example.com"
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="password" className="label-base">Mật khẩu</label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-base pr-10"
              placeholder="Tối thiểu 6 ký tự"
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-navy-400 hover:text-navy-600"
              aria-label={showPassword ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <div>
          <label htmlFor="confirmPassword" className="label-base">Xác nhận mật khẩu</label>
          <div className="relative">
            <input
              id="confirmPassword"
              type={showConfirm ? "text" : "password"}
              autoComplete="new-password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="input-base pr-10"
              placeholder="Nhập lại mật khẩu"
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => setShowConfirm((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-navy-400 hover:text-navy-600"
              aria-label={showConfirm ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
            >
              {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        <Button type="submit" variant="primary" size="lg" loading={loading} className="w-full">
          <UserPlus className="h-4 w-4" />
          Tạo tài khoản
        </Button>

        <p className="text-center text-xs text-navy-400">
          Bằng cách đăng ký, bạn đồng ý với{" "}
          <Link href="/terms" className="text-brand-blue hover:underline">Điều khoản dịch vụ</Link>{" "}
          và{" "}
          <Link href="/privacy" className="text-brand-blue hover:underline">Chính sách bảo mật</Link>.
        </p>
      </form>
    </div>
  );
}
