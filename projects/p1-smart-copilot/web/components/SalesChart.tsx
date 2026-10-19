// Claude viết theo yêu cầu, 2026-10-19 — Bài 3 bước 3: chart cho data của tool sales_summary
// Tự vẽ bằng div + % (không thêm thư viện): data chỉ vài chục dòng, 1 kiểu chart cột → không cần Recharts.

import { formatDate, formatVnd } from "@/lib/format";

// khớp tay với SalesRow ở backend/app/tools.py — tool trả LIST (2 tool kia trả object)
export type SalesRow = {
  label: string; // "2026-09-28" (group_by=day) hoặc tên món (group_by=product)
  revenue_vnd: number;
  order_count: number;
};

export type SalesData = SalesRow[];

const DAY_LABEL = /^\d{4}-\d{2}-\d{2}$/;

// "29.000 ₫" quá dài cho nhãn cột → 1,2tr / 388k
function shortVnd(value: number): string {
  if (value >= 1_000_000) return `${(value / 1_000_000).toLocaleString("vi-VN", { maximumFractionDigits: 1 })}tr`;
  if (value >= 1_000) return `${Math.round(value / 1_000)}k`;
  return String(value);
}

export function SalesChart({ data }: { data: SalesData }) {
  if (data.length === 0) {
    return <p className="rounded-lg border p-4 text-sm text-zinc-500">Chưa có doanh thu.</p>;
  }

  const max = Math.max(...data.map((r) => r.revenue_vnd), 1);
  const total = data.reduce((sum, r) => sum + r.revenue_vnd, 0);
  // data không mang group_by → đoán từ nhãn: toàn ngày → cột theo thời gian, còn lại → thanh ngang xếp hạng
  const byDay = data.every((r) => DAY_LABEL.test(r.label));

  return (
    <div className="rounded-lg border p-4">
      <p className="mb-3 text-sm text-zinc-500">
        Doanh thu {byDay ? "theo ngày" : "theo món"} · Tổng <strong>{formatVnd(total)}</strong>
      </p>

      {byDay ? (
        // cột dọc: xu hướng theo thời gian; nhiều ngày → cuộn ngang
        <div className="overflow-x-auto">
          <div className="flex h-48 min-w-fit items-end gap-1">
            {data.map((r) => (
              <div
                key={r.label}
                title={`${formatDate(r.label)}: ${formatVnd(r.revenue_vnd)} · ${r.order_count} đơn`}
                className="flex h-full w-8 flex-col items-center gap-1"
              >
                {/* vùng cột riêng (flex-1) → height % tính trên vùng này, không tính 2 nhãn → cột cao nhất không tràn */}
                <div className="flex w-full flex-1 flex-col items-center justify-end gap-1">
                  <span className="text-[10px] text-zinc-500">{shortVnd(r.revenue_vnd)}</span>
                  <div
                    className="w-full rounded-t bg-blue-500"
                    style={{ height: `${(r.revenue_vnd / max) * 85}%` }}
                  />
                </div>
                <span className="text-[10px] text-zinc-500">{formatDate(r.label).slice(0, 5)}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        // thanh ngang: xếp hạng (backend đã sắp doanh thu giảm dần)
        <ul className="flex flex-col gap-2">
          {data.map((r) => (
            <li key={r.label} className="text-sm">
              <div className="flex justify-between gap-2">
                <span>{r.label}</span>
                <span className="whitespace-nowrap text-zinc-500">
                  {formatVnd(r.revenue_vnd)} · {r.order_count} đơn
                </span>
              </div>
              <div className="mt-1 h-2 rounded bg-zinc-100 dark:bg-zinc-800">
                <div className="h-2 rounded bg-blue-500" style={{ width: `${(r.revenue_vnd / max) * 100}%` }} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
