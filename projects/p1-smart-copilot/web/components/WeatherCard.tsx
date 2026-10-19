// Claude viết theo yêu cầu, 2026-10-19 — Bài 3 bước 1: card cho data của tool get_weather

// khớp tay với WeatherResponse ở backend/app/tools.py
export type WeatherData = {
  city: string;
  temperature_c: number;
  condition: string;
  observed_at: string; // "2026-10-19 21:15" — giờ VN, không có múi giờ
};

const tempFormat = new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 1 });

// không dùng new Date(): chuỗi không có múi giờ → trình duyệt đọc theo giờ máy (hoặc Invalid Date)
function formatObservedAt(value: string): string {
  const [date, time] = value.split(" ");
  const [year, month, day] = (date ?? "").split("-");
  if (!time || !year || !month || !day) return value;
  return `${time}, ${day}/${month}/${year}`;
}

export function WeatherCard({ data }: { data: WeatherData }) {
  return (
    <div className="w-fit min-w-56 rounded-lg border p-4">
      <p className="text-sm text-zinc-500">Thời tiết {data.city}</p>
      <p className="text-3xl font-semibold">{tempFormat.format(data.temperature_c)}°C</p>
      <p className="first-letter:uppercase">{data.condition}</p>
      <p className="mt-2 text-xs text-zinc-500">Cập nhật lúc {formatObservedAt(data.observed_at)}</p>
    </div>
  );
}
