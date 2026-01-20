# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Parallel Web Search API tools.

Uses API key authentication.
Credentials provided by client via token exchange.
No server-side environment variables required.

API docs: https://docs.parallel.ai
"""

from typing import Any

from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.auth import Connection, SecretKeys
from dedalus_mcp.types import ToolAnnotations
from pydantic import Field
from pydantic.dataclasses import dataclass

# Parallel API uses x-api-key header auth
# Base URL: https://api.parallel.ai
parallel = Connection(
    name="parallel",
    secrets=SecretKeys(token="PARALLEL_API_KEY"),
    auth_header_name="x-api-key",
    auth_header_format="{api_key}",
)

PARALLEL_BETA_HEADER = "search-extract-2025-10-10"


@dataclass(frozen=True)
class ParallelResult:
    """Parallel API result."""

    success: bool
    data: Any = None
    error: str | None = None


async def _req(method: HttpMethod, path: str, body: Any = None) -> ParallelResult:
    """Execute Parallel API request."""
    ctx = get_context()
    request = HttpRequest(
        method=method,
        path=path,
        body=body,
        headers={"parallel-beta": PARALLEL_BETA_HEADER},
    )
    resp = await ctx.dispatch("parallel", request)
    if resp.success:
        return ParallelResult(success=True, data=resp.response.body)
    return ParallelResult(success=False, error=resp.error.message if resp.error else "Request failed")


# --- Search ---


@tool(
    description="Search the web using Parallel's Search API",
    tags=["search", "web"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def parallel_search(
    queries: list[str],
    objective: str | None = None,
    max_results: int = 10,
    max_chars_per_result: int = 10000,
) -> ParallelResult:
    """Execute parallel web searches.

    Args:
        queries: List of search queries to execute in parallel
        objective: Optional high-level objective to guide result relevance
        max_results: Maximum results per query (default: 10)
        max_chars_per_result: Maximum characters per result excerpt (default: 10000)

    Returns:
        ParallelResult with search results

    """
    body: dict[str, Any] = {
        "search_queries": queries,
        "max_results": max_results,
        "excerpts": {"max_chars_per_result": max_chars_per_result},
    }

    if objective:
        body["objective"] = objective
    else:
        body["objective"] = f"Find relevant information for: {', '.join(queries)}"

    return await _req(HttpMethod.POST, "/v1beta/search", body=body)


# --- Extract ---


@tool(
    description="Extract content from URLs using Parallel's Extract API",
    tags=["extract", "web"],
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def parallel_extract(
    urls: list[str],
    objective: str | None = None,
    excerpts: bool = True,
    full_content: bool = False,
) -> ParallelResult:
    """Extract content from web pages.

    Args:
        urls: List of public URLs to extract content from
        objective: What content to extract (guides excerpt selection)
        excerpts: Return focused passages aligned with objective (default: True)
        full_content: Return complete page content as markdown (default: False)

    Returns:
        ParallelResult with extracted content

    """
    body: dict[str, Any] = {
        "urls": urls,
        "excerpts": excerpts,
        "full_content": full_content,
    }

    if objective:
        body["objective"] = objective

    return await _req(HttpMethod.POST, "/v1beta/extract", body=body)


# --- Export ---

parallel_tools = [
    parallel_search,
    parallel_extract,
]
