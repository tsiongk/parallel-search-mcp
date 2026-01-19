# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Parallel Web Search MCP Server.

Exposes Parallel's Search API via Dedalus MCP framework.
API docs: https://docs.parallel.ai

Environment Variables:
    PARALLEL_API_KEY: Your Parallel API key
    DEDALUS_AS_URL: Optional Dedalus authorization server URL
"""

from __future__ import annotations

import asyncio
import os

from dedalus_mcp import MCPServer, tool
from dedalus_mcp.server import TransportSecuritySettings

from search import parallel_search, extract as parallel_extract


AS_URL = os.getenv("DEDALUS_AS_URL")

server = MCPServer(
    name="parallel-web-search",
    version="1.0.0",
    instructions="Parallel Web Search MCP server. Search the web using Parallel's Search API.",
    http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    streamable_http_stateless=True,
    authorization_server=AS_URL,
)


@tool(description="Search the web using Parallel's Search API")
async def search(
    queries: list[str],
    objective: str | None = None,
    max_results: int = 10,
) -> list[dict]:
    """Search the web.

    Args:
        queries: List of search queries
        objective: Optional context to guide result relevance
        max_results: Maximum results per query (default: 10)

    Returns:
        List of results per query, each with title, url, excerpt, source
    """
    results = await parallel_search(
        queries=queries,
        objective=objective,
        max_results=max_results,
    )
    return [r.model_dump() for r in results]


@tool(description="Extract content from URLs using Parallel's Extract API")
async def extract(
    urls: list[str],
    objective: str | None = None,
    excerpts: bool = True,
    full_content: bool = False,
) -> dict:
    """Extract content from web pages.

    Args:
        urls: List of public URLs to extract content from
        objective: What content to extract (guides excerpt selection)
        excerpts: Return focused passages aligned with objective (default: True)
        full_content: Return complete page content as markdown (default: False)

    Returns:
        Extracted content with title, publish_date, excerpts/full_content per URL
    """
    result = await parallel_extract(
        urls=urls,
        objective=objective,
        excerpts=excerpts,
        full_content=full_content,
    )
    return result.model_dump()


server.collect(search, extract)


async def main() -> None:
    """Start MCP server on port 8080."""
    await server.serve(port=8080)


if __name__ == "__main__":
    asyncio.run(main())
