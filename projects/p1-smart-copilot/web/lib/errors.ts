// Claude viết theo yêu cầu, 2026-10-19 — đổi lỗi trước stream thành câu ngắn cho người dùng

// A. Server trả lời nhưng status không phải 2xx (Route Handler gửi { error: string })
export async function errorFromResponse(res: Response): Promise<string> {
  if (res.status === 429) {
    const seconds = Number(res.headers.get("retry-after"));
    return Number.isFinite(seconds) && seconds > 0
      ? `Bạn hỏi nhanh quá, thử lại sau ${seconds} giây`
      : "Bạn hỏi nhanh quá, thử lại sau ít phút";
  }
  // key sai là lỗi cấu hình server, user không gửi key → không nói "sai key"
  if (res.status === 401) {
    return "Trợ lý đang lỗi cấu hình, vui lòng báo quản trị viên";
  }
  if (res.status >= 500) {
    return "Không kết nối được trợ lý, thử lại sau";
  }
  // 500 do throw trong Route Handler là trang lỗi HTML của Next, không phải JSON → .catch
  const body: unknown = await res.json().catch(() => null);
  if (
    typeof body === "object" &&
    body !== null &&
    "error" in body &&
    typeof body.error === "string"
  ) {
    return body.error;
  }
  return "Yêu cầu không hợp lệ, thử lại";
}

// B. fetch / đọc stream ném lỗi. null = không phải lỗi (bấm Dừng), component tự hiện "đã dừng"
export function errorFromException(err: unknown): string | null {
  if (err instanceof DOMException && err.name === "AbortError") {
    return null;
  }
  // fetch ném TypeError khi mất mạng / server không trả lời
  if (err instanceof TypeError) {
    return "Không kết nối được, kiểm tra mạng rồi thử lại";
  }
  return "Có lỗi xảy ra, thử lại sau";
}
