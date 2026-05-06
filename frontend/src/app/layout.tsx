import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ValuAI - Định giá doanh nghiệp thông minh",
  description:
    "Hệ thống định giá doanh nghiệp thông minh ứng dụng trí tuệ nhân tạo — nhanh chóng, chính xác, chuyên nghiệp.",
  keywords: ["định giá doanh nghiệp", "AI", "valuation", "M&A", "Vietnam"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className={inter.variable}>
      <body className="font-sans min-h-screen">{children}</body>
    </html>
  );
}
