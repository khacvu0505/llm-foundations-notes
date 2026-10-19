// Claude viết theo yêu cầu, 2026-10-19 — định dạng dùng chung cho các component Bài 3

const vndFormat = new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" });

// 29000 → "29.000 ₫"
export function formatVnd(value: number): string {
  return vndFormat.format(value);
}

// "2026-09-28" → "28/09/2026". Không dùng new Date(): chuỗi chỉ có ngày, new Date() đọc là UTC → lệch ngày theo múi giờ
export function formatDate(value: string): string {
  const [year, month, day] = value.split("-");
  if (!year || !month || !day) return value;
  return `${day}/${month}/${year}`;
}
