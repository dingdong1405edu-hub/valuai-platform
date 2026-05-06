import Link from "next/link";
import {
  BarChart3,
  FileText,
  Zap,
  Upload,
  Bot,
  Download,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-navy-100 bg-white/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-navy-800">
              <BarChart3 className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-bold text-navy-800">ValuAI</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-navy-700 hover:bg-navy-50 transition-colors"
            >
              Đăng nhập
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-navy-800 px-4 py-2 text-sm font-medium text-white hover:bg-navy-700 transition-colors shadow-sm"
            >
              Đăng ký miễn phí
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-navy-800 via-navy-700 to-brand-blue px-4 pt-20 pb-24 text-white sm:px-6 sm:pt-28 sm:pb-32">
        {/* Background decoration */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-white/5 blur-3xl" />
          <div className="absolute -bottom-20 -left-20 h-80 w-80 rounded-full bg-brand-blue/20 blur-3xl" />
        </div>

        <div className="relative mx-auto max-w-4xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm font-medium backdrop-blur-sm">
            <Zap className="h-4 w-4 text-yellow-300" />
            Công nghệ AI thế hệ mới
          </div>
          <h1 className="text-balance text-4xl font-bold leading-tight sm:text-5xl lg:text-6xl">
            Định giá doanh nghiệp{" "}
            <span className="text-yellow-300">chính xác</span>{" "}
            bằng AI
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-balance text-lg text-white/80 sm:text-xl">
            Tải lên tài liệu doanh nghiệp, hệ thống AI đa tác nhân sẽ phân
            tích và tạo báo cáo định giá chuyên nghiệp trong vài phút.
          </p>
          <div className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link
              href="/upload"
              className="group inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3.5 text-base font-semibold text-navy-800 shadow-lg hover:bg-yellow-50 transition-colors"
            >
              Bắt đầu ngay
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-0.5" />
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-xl border border-white/30 px-6 py-3.5 text-base font-semibold text-white hover:bg-white/10 transition-colors"
            >
              Xem demo
            </Link>
          </div>

          {/* Trust indicators */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-6 text-sm text-white/60">
            {["Bảo mật SSL", "Dữ liệu riêng tư", "Không lưu tài liệu gốc"].map(
              (item) => (
                <span key={item} className="flex items-center gap-1.5">
                  <CheckCircle2 className="h-4 w-4 text-green-400" />
                  {item}
                </span>
              )
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-4 py-20 sm:px-6 sm:py-28">
        <div className="mx-auto max-w-6xl">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-navy-800 sm:text-4xl">
              Tại sao chọn ValuAI?
            </h2>
            <p className="mt-4 text-navy-500 text-lg max-w-2xl mx-auto">
              Giải pháp định giá doanh nghiệp toàn diện, thay thế cho quy trình
              tư vấn truyền thống tốn kém và mất thời gian.
            </p>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: BarChart3,
                color: "bg-blue-100 text-blue-700",
                title: "Phân tích đa chiều",
                description:
                  "Kết hợp nhiều phương pháp định giá: DCF, P/E, EV/EBITDA và so sánh thị trường. AI phân tích đồng thời từ nhiều góc độ để đảm bảo tính toàn diện.",
                points: ["DCF & FCFF analysis", "Market comparables", "Asset-based valuation"],
              },
              {
                icon: FileText,
                color: "bg-green-100 text-green-700",
                title: "Báo cáo chuyên nghiệp",
                description:
                  "Xuất báo cáo PDF định dạng chuyên nghiệp, sẵn sàng trình bày với nhà đầu tư, ngân hàng hoặc đối tác chiến lược.",
                points: ["Chuẩn IFRS & VAS", "Biểu đồ trực quan", "Phân tích rủi ro"],
              },
              {
                icon: Zap,
                color: "bg-yellow-100 text-yellow-700",
                title: "Nhanh chóng & tiết kiệm",
                description:
                  "Kết quả trong vài phút thay vì vài tuần. Chi phí thấp hơn 90% so với thuê tư vấn M&A truyền thống.",
                points: ["< 10 phút xử lý", "Tiết kiệm 90% chi phí", "Cập nhật theo thời gian thực"],
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="card p-6 hover:shadow-md transition-shadow"
              >
                <div
                  className={`inline-flex h-12 w-12 items-center justify-center rounded-xl ${feature.color} mb-4`}
                >
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-bold text-navy-800 mb-2">
                  {feature.title}
                </h3>
                <p className="text-navy-500 text-sm leading-relaxed mb-4">
                  {feature.description}
                </p>
                <ul className="space-y-1.5">
                  {feature.points.map((point) => (
                    <li
                      key={point}
                      className="flex items-center gap-2 text-sm text-navy-600"
                    >
                      <CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="bg-navy-50 px-4 py-20 sm:px-6 sm:py-28">
        <div className="mx-auto max-w-4xl">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-navy-800 sm:text-4xl">
              Quy trình 3 bước đơn giản
            </h2>
            <p className="mt-4 text-navy-500 text-lg">
              Từ tài liệu đến báo cáo hoàn chỉnh chỉ trong vài phút.
            </p>
          </div>

          <div className="relative">
            {/* Connector line (desktop) */}
            <div className="absolute top-10 left-1/2 hidden h-0.5 w-2/3 -translate-x-1/2 bg-navy-200 lg:block" />

            <div className="grid gap-8 lg:grid-cols-3">
              {[
                {
                  step: "01",
                  icon: Upload,
                  title: "Upload tài liệu",
                  description:
                    "Tải lên báo cáo tài chính, hồ sơ năng lực, kế hoạch kinh doanh và các tài liệu liên quan.",
                },
                {
                  step: "02",
                  icon: Bot,
                  title: "AI phân tích",
                  description:
                    "Hệ thống AI đa tác nhân tự động đọc, phân tích và định giá doanh nghiệp theo nhiều phương pháp.",
                },
                {
                  step: "03",
                  icon: Download,
                  title: "Nhận báo cáo",
                  description:
                    "Tải báo cáo định giá PDF chuyên nghiệp với đầy đủ số liệu, biểu đồ và phân tích chi tiết.",
                },
              ].map((step) => (
                <div key={step.step} className="relative text-center">
                  <div className="relative mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-2xl bg-navy-800 shadow-lg">
                    <step.icon className="h-9 w-9 text-white" />
                    <div className="absolute -top-3 -right-3 flex h-7 w-7 items-center justify-center rounded-full bg-brand-accent text-xs font-bold text-white shadow-sm">
                      {step.step}
                    </div>
                  </div>
                  <h3 className="text-lg font-bold text-navy-800 mb-2">
                    {step.title}
                  </h3>
                  <p className="text-navy-500 text-sm leading-relaxed max-w-xs mx-auto">
                    {step.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 py-20 sm:px-6 sm:py-28">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold text-navy-800 sm:text-4xl text-balance">
            Sẵn sàng định giá doanh nghiệp của bạn?
          </h2>
          <p className="mt-4 text-lg text-navy-500">
            Tạo tài khoản miễn phí và bắt đầu ngay hôm nay.
          </p>
          <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link
              href="/upload"
              className="group inline-flex items-center gap-2 rounded-xl bg-navy-800 px-8 py-4 text-base font-semibold text-white shadow-lg hover:bg-navy-700 transition-colors"
            >
              Bắt đầu ngay — miễn phí
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-0.5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-navy-100 bg-navy-800 px-4 py-8 sm:px-6">
        <div className="mx-auto max-w-6xl flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
          <div className="flex items-center gap-2 text-white">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-white/10">
              <BarChart3 className="h-4 w-4 text-white" />
            </div>
            <span className="font-semibold">ValuAI</span>
          </div>
          <p className="text-sm text-white/50">
            &copy; {new Date().getFullYear()} ValuAI. Định giá thông minh cho doanh nghiệp Việt.
          </p>
        </div>
      </footer>
    </div>
  );
}
