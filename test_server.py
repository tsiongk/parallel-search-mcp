#!/usr/bin/env python3
"""Test script for parallel-search-mcp server using Dedalus SDK."""

import asyncio
import os
import sys

sys.path.insert(0, "src")

from dotenv import load_dotenv

load_dotenv()

from dedalus_mcp.auth import SecretValues
from dedalus_labs import AsyncDedalus, DedalusRunner

from parallel import parallel_api


# --- Configuration ------------------------------------------------------------

DEDALUS_API_KEY = os.getenv("DEDALUS_API_KEY")

# --- Secret Bindings ----------------------------------------------------------

parallel_secrets = SecretValues(parallel_api, token=os.getenv("PARALLEL_API_KEY", "")).to_dict()

# --- Main ---------------------------------------------------------------------

async def main() -> None:
    client = AsyncDedalus(api_key=DEDALUS_API_KEY)

    runner = DedalusRunner(client)
    result = await runner.run(
        input="Search the web for 'latest AI news January 2025'",
        model="anthropic/claude-sonnet-4-20250514",
        mcp_servers=["tsion/parallel-search-mcp"],
        credentials=[parallel_secrets],
    )
    print("Result:")
    print(result.output)


if __name__ == "__main__":
    asyncio.run(main())
