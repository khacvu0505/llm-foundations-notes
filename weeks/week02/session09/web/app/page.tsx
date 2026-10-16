"use client";

import { useRef, useState } from "react";

type Usage = {
  input_tokens: number | null;
  output_tokens: number | null;
  cost_usd: number | null;
};

export default function Home() {
  const [input, setInput] = useState<string>("");
  const [answer, setAnswer] = useState<string>("");
  const [usage, setUsage] = useState<Usage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const handleReset = () => {
    setAnswer("");
    setUsage(null);
    setError(null);
  };

  function handleEvent(raw: string) {
    const lines = raw.split("\n");
    let eventName = "";
    let data = "";
    for (const line of lines) {
      if (line.startsWith("event:")) {
        eventName = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        data = line.slice(5).trim();
      }
    }

    if (!data) return;
    const parsed = JSON.parse(data)

    switch (eventName) {
      case "delta":
        setAnswer(prev => prev + parsed.content);
        break;

      case "done":
        setUsage(parsed)
        break;

      case "error":
        setError(parsed.message);
        break;

      default:
        console.warn("event lạ:", eventName)
        break;
    }
  }

  async function handleSend(e: React.SubmitEvent<HTMLFormElement>) {
    e.preventDefault();
    const message = input.trim();
    if (!message) return;
    setLoading(true);
    handleReset();


    const controller = new AbortController();
    abortRef.current = controller;
    const signal = controller.signal;

    try {
      const res = await fetch("http://127.0.0.1:8000/chat/stream", {
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": process.env.NEXT_PUBLIC_APP_API_KEY as string,
        },
        method: "POST",
        body: JSON.stringify({ message }),
        signal,
      });
      if (res.ok) {
        if (!res.body) {
          setError("Response body is empty");
          return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();

        let buffer = "";
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;
          const parts = buffer.split("\n\n");
          buffer = parts.pop() ?? "";
          for (const part of parts) {
            handleEvent(part);
          }
        }
      } else {
        setError(`${res.status}: ${res.statusText}`);
      }
    } catch (error) {
      if (error instanceof Error && error.name === "AbortError") {
        setError("Đã dừng");
      } else if (error instanceof Error) {
        setError(error.message);
      }
    } finally {
      setLoading(false);
      abortRef.current = null
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-col gap-4 p-8">
      <form onSubmit={handleSend} className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Hỏi gì đó..."
          className="flex-1 rounded border px-3 py-2"
        />
        <button
          type="submit"
          disabled={loading || input.trim() === ""}
          className="rounded bg-black px-4 py-2 text-white disabled:opacity-40"
        >
          Gửi
        </button>
        {loading && (
          <button type="button" className="rounded border px-4 py-2" onClick={() => abortRef.current?.abort()}>
            Dừng
          </button>
        )}
      </form>

      <div className="min-h-24 whitespace-pre-wrap rounded border p-4">
        {answer}
      </div>

      {usage && (
        <p className="text-sm text-zinc-500">
          Tokens: {usage.input_tokens ?? "?"} in / {usage.output_tokens ?? "?"}{" "}
          out · Cost: ${usage.cost_usd?.toFixed(6) ?? "?"}
        </p>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}
    </main>
  );
}
