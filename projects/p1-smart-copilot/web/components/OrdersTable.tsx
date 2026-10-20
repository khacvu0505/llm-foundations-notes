// Claude viết theo yêu cầu, 2026-10-19 — Bài 3 bước 2: bảng cho data của tool query_orders

import { formatDate, formatVnd } from "@/lib/format";

// khớp tay với OrderItem / OrderResponse ở backend/app/tools.py
type OrderStatus = "delivered" | "shipping" | "pending" | "cancelled";

export type Order = {
  order_id: number;
  customer: string;
  product: string;
  quantity: number;
  unit_price: number;
  status: OrderStatus;
  created_at: string; // "2026-09-28"
  city: string;
};

export type OrdersData = {
  orders: Order[];
  order_count: number;
  total_amount_vnd: number;
};

// status lạ (backend thêm giá trị mới) → hiện nguyên chuỗi, không crash
const STATUS_LABEL: Record<OrderStatus, { label: string; className: string }> = {
  delivered: { label: "Đã giao", className: "bg-green-100 text-green-800" },
  shipping: { label: "Đang giao", className: "bg-blue-100 text-blue-800" },
  pending: { label: "Chờ xử lý", className: "bg-amber-100 text-amber-800" },
  cancelled: { label: "Đã huỷ", className: "bg-zinc-200 text-zinc-700" },
};

export function OrdersTable({ data }: { data: OrdersData }) {
  if (data.orders.length === 0) {
    return <p className="rounded-lg border p-4 text-sm text-zinc-500">Không có đơn nào khớp.</p>;
  }

  return (
    <div className="rounded-lg border">
      {/* không lọc thì tool trả cả file (~50 đơn) → giới hạn chiều cao, cuộn trong bảng */}
      <div className="max-h-80 overflow-auto">
        <table className="w-full text-left text-sm">
          <thead className="sticky top-0 bg-zinc-50 text-xs text-zinc-500 dark:bg-zinc-900">
            <tr>
              <th className="px-3 py-2">Mã</th>
              <th className="px-3 py-2">Khách</th>
              <th className="px-3 py-2">Món</th>
              <th className="px-3 py-2 text-right">SL</th>
              <th className="px-3 py-2 text-right">Thành tiền</th>
              <th className="px-3 py-2">Trạng thái</th>
              <th className="px-3 py-2">Ngày</th>
            </tr>
          </thead>
          <tbody>
            {data.orders.map((o) => {
              const status = STATUS_LABEL[o.status] ?? { label: o.status, className: "bg-zinc-100" };
              return (
                <tr key={o.order_id} className="border-t">
                  <td className="px-3 py-2 text-zinc-500">#{o.order_id}</td>
                  <td className="px-3 py-2">
                    {o.customer}
                    <span className="block text-xs text-zinc-500">{o.city}</span>
                  </td>
                  <td className="px-3 py-2">{o.product}</td>
                  <td className="px-3 py-2 text-right">{o.quantity}</td>
                  <td className="px-3 py-2 text-right whitespace-nowrap">
                    {formatVnd(o.quantity * o.unit_price)}
                  </td>
                  <td className="px-3 py-2">
                    <span className={`rounded px-2 py-0.5 text-xs whitespace-nowrap ${status.className}`}>
                      {status.label}
                    </span>
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap">{formatDate(o.created_at)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="border-t px-3 py-2 text-sm">
        {data.order_count} đơn · Tổng <strong>{formatVnd(data.total_amount_vnd)}</strong>
      </p>
    </div>
  );
}
