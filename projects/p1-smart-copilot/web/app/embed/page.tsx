// Claude viết theo yêu cầu, 2026-10-20 — Bài 4 bước 7: trang chỉ có widget, để trang ở origin khác nhúng bằng <iframe>

import type { Metadata } from "next";
import { ChatWidget } from "@/components/ChatWidget";

export const metadata: Metadata = {
  title: "Smart Copilot",
};

// Server Component: không cần "use client", ChatWidget tự là client.
// data-embed → globals.css cho body nền trong suốt (trang chủ nhìn xuyên qua iframe, chỉ bong bóng + khung chat có nền)
export default function EmbedPage() {
  return (
    <div data-embed>
      <ChatWidget />
    </div>
  );
}
