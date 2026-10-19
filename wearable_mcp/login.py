"""One-time interactive Garmin login (handles MFA) that caches tokens.

Usage:  docker compose run --rm wearable-mcp wearable-login
   or:  uv run wearable-login
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from garminconnect import Garmin


def main() -> None:
    load_dotenv()
    email, password = os.getenv("GARMIN_EMAIL"), os.getenv("GARMIN_PASSWORD")
    if not email or not password:
        sys.exit("Set GARMIN_EMAIL and GARMIN_PASSWORD in .env")
    tokenstore = os.path.abspath(os.getenv("GARMINTOKENS", "./garmin-tokens"))
    os.makedirs(tokenstore, exist_ok=True)
    api = Garmin(email, password, prompt_mfa=lambda: input("Garmin MFA code: ").strip())
    api.login(tokenstore)
    api.client.dump(tokenstore)
    name = api.get_full_name() if hasattr(api, "get_full_name") else "ok"
    print(f"Logged in as {name}. Tokens cached in {tokenstore}")


if __name__ == "__main__":
    main()
