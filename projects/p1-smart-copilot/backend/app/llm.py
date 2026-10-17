from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

client = AsyncOpenAI()
MODEL = "gpt-6-luna"

PRICES: dict[str, tuple[float, float]] = {
  "gpt-4.1-nano": (0.10, 0.40),
  "gpt-4o-mini": (0.15, 0.60),
  "gpt-6-luna": (0.10, 0.50),
}


def cost_usd(
  input_tokens: int,
  output_tokens: int,
  price_in_per_mtok: float,
  price_out_per_mtok: float,
) -> float:
  return (input_tokens / 1_000_000) * price_in_per_mtok + (
    output_tokens / 1_000_000
  ) * price_out_per_mtok


def get_openai_client() -> AsyncOpenAI:
  return client
