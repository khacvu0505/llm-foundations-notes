// Claude viết theo yêu cầu, 2026-10-19 — Bài 3 bước 4+5: 1 ToolPart → trạng thái / component / cảnh báo

import type { ReactNode } from "react";
import { OrdersTable, type OrdersData } from "@/components/OrdersTable";
import { SalesChart, type SalesData } from "@/components/SalesChart";
import { WeatherCard, type WeatherData } from "@/components/WeatherCard";
import type { ToolPart } from "@/lib/types";

type ToolUI = {
  // câu hiện lúc status "running" — lấy thêm chi tiết từ arguments model gửi
  running: (args: Record<string, unknown>) => string;
  // data là unknown (từ mạng) → cast ở đúng 1 chỗ này, component bên dưới nhận type đã rõ
  render: (data: unknown) => ReactNode;
};

const text = (value: unknown): string | null => (typeof value === "string" && value ? value : null);

// Registry name → UI, giống TOOLS_REGISTRY ở backend. Thêm tool mới = thêm 1 dòng ở đây.
const TOOL_UI: Record<string, ToolUI> = {
  query_orders: {
    running: (args) => {
      const customer = text(args.customer);
      return customer ? `Đang tra đơn hàng của ${customer}…` : "Đang tra đơn hàng…";
    },
    render: (data) => <OrdersTable data={data as OrdersData} />,
  },
  sales_summary: {
    running: (args) => (args.group_by === "day" ? "Đang tính doanh thu theo ngày…" : "Đang tính doanh thu theo món…"),
    render: (data) => <SalesChart data={data as SalesData} />,
  },
  get_weather: {
    running: (args) => {
      const city = text(args.city);
      return city ? `Đang xem thời tiết ${city}…` : "Đang xem thời tiết…";
    },
    render: (data) => <WeatherCard data={data as WeatherData} />,
  },
};

export function ToolView({ part }: { part: ToolPart }) {
  const ui = TOOL_UI[part.name];

  if (part.status === "running") {
    return (
      <p className="flex items-center gap-2 text-sm text-zinc-500">
        <span className="size-2 animate-pulse rounded-full bg-blue-500" />
        {ui ? ui.running(part.arguments) : `Đang chạy ${part.name}…`}
      </p>
    );
  }

  if (part.status === "error") {
    // cảnh báo nhỏ; chữ của model vẫn hiện ở part text phía sau
    return (
      <p className="rounded border border-amber-300 bg-amber-50 px-3 py-2 text-sm text-amber-800">
        ⚠️ {part.error ?? `Tool ${part.name} lỗi`}
      </p>
    );
  }

  // tool lạ / chưa có component → JSON gọn, không crash
  if (!ui) {
    return (
      <details className="rounded border px-3 py-2 text-sm">
        <summary className="cursor-pointer text-zinc-500">Kết quả {part.name}</summary>
        <pre className="mt-2 overflow-x-auto text-xs">{JSON.stringify(part.data, null, 2)}</pre>
      </details>
    );
  }

  return ui.render(part.data);
}
