// Claude viết theo yêu cầu, 2026-10-20 — Bài 4 bước 7: trang chủ demo + widget.
// Trang thử Bài 2–3 (form + <pre> JSON debug) đã bỏ: logic gửi / dừng giờ nằm trong ChatWidget; bản cũ ở commit 6b54d8c.

import Link from "next/link";
import { ChatWidget } from "@/components/ChatWidget";

const SAMPLE_QUESTIONS = [
  "Đơn nào của An đang giao?",
  "Tuần này món nào bán chạy nhất?",
  "Mai Đà Nẵng mưa không, có nên giao đơn không?",
  "So sánh doanh thu theo ngày với thời tiết Hà Nội hôm nay",
];

export default function Home() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-col gap-4 p-6">
      <h1 className="text-xl font-semibold">Smart Copilot</h1>
      <p className="text-zinc-500">Bấm bong bóng 💬 ở góc phải dưới để hỏi. Câu mẫu:</p>
      <ul className="list-disc pl-5 text-sm">
        {SAMPLE_QUESTIONS.map((q) => (
          <li key={q}>{q}</li>
        ))}
      </ul>
      <p className="text-sm text-zinc-500">
        Bản nhúng (chỉ có widget, dùng trong <code>&lt;iframe&gt;</code>):{" "}
        <Link href="/embed" className="underline">
          /embed
        </Link>
      </p>

      <ChatWidget />
    </main>
  );
}
