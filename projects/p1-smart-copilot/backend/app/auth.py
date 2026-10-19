import os
import secrets
from typing import Annotated

from fastapi import Header, HTTPException


def verify_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
  key = os.getenv("APP_API_KEY")
  if key is None or len(key) == 0:
    raise HTTPException(status_code=500, detail="Server misconfigured")
  if x_api_key is None:
    raise HTTPException(status_code=401, detail="Missing API Key")
  if not secrets.compare_digest(key, x_api_key):
    raise HTTPException(status_code=401, detail="Invalid API Key")
