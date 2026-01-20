# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Parallel Web Search API operations for MCP server.

Provides Search and Extract functionality using Parallel's API.
API docs: https://docs.parallel.ai

Required environment variables:
    PARALLEL_API_KEY: API key from Parallel
"""

from typing import Any
from urllib.parse import urlencode

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.auth import Connection, SecretKeys


load_dotenv()


# --- Connection --------------------------------------------------------------

PARALLEL_BETA_HEADER = "search-extract-2025-10-10"

parallel_api = Connection(
    name="parallel",
    secrets=SecretKeys(token="PARALLEL_API_KEY"),
    base_url="https://api.parallel.ai/v1beta",
    auth_header_format="x-api-key: {api_key}",
    default_headers={"parallel-beta": PARALLEL_BETA_HEADER},
)


# --- Response Models ---------------------------------------------------------


class SearchResult(BaseModel):
    """A single search result from Parallel API."""

    title: str | None = None
    url: str | None = None
    excerpt: str | None = None
    source: str | None = None


class SearchResponse(BaseModel):
    """Response from a parallel web search."""

    query: str
    results: list[SearchResult] = Field(default_factory=list)
    total_results: int = 0


class ExtractResult(BaseModel):
    """A single extraction result from Parallel API."""

    url: str
    title: str | None = None
    publish_date: str | None = None
    excerpts: list[str] | None = None
    full_content: str | None = None


class ExtractResponse(BaseModel):
    """Response from Parallel Extract API."""

    extract_id: str | None = None
    results: list[ExtractResult] = Field(default_factory=list)
    errors: list[dict] = Field(default_factory=list)


class ParallelResult(BaseModel):
    """Generic Parallel API result."""

    success: bool
    data: Any = None
    error: str | None = None


# --- Helper ------------------------------------------------------------------


async def _request(
    method: HttpMethod,
    path: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> ParallelResult:
    """Make a Parallel API request via the enclave dispatch."""
    ctx = get_context()

    # Build path with query params
    if params:
        query_string = urlencode({k: v for k, v in params.items() if v is not None})
        if query_string:
            path = f"{path}?{query_string}"

    request = HttpRequest(method=method, path=path, body=body)
    response = await ctx.dispatch("parallel", request)

    if response.success:
        return ParallelResult(success=True, data=response.response.body)

    msg = response.error.message if response.error else "Request failed"
    return ParallelResult(success=False, error=msg)


# --- Search Tools ------------------------------------------------------------


@tool(description="Search the web using Parallel's Search API")
async def parallel_search(
    queries: list[str],
    objective: str | None = None,
    max_results: int = 10,
    max_chars_per_result: int = 10000,
) -> ParallelResult:
    """Execute parallel web searches using Parallel API.

    Args:
        queries: List of search queries to execute in parallel
        objective: Optional high-level objective to guide result relevance
        max_results: Maximum results per query (default: 10)
        max_chars_per_result: Maximum characters per result excerpt (default: 10000)
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

    return await _request(HttpMethod.POST, "/search", body=body)


# --- Extract Tools -----------------------------------------------------------


@tool(description="Extract content from URLs using Parallel's Extract API")
async def parallel_extract(
    urls: list[str],
    objective: str | None = None,
    excerpts: bool = True,
    full_content: bool = False,
) -> ParallelResult:
    """Extract content from web pages using Parallel API.

    Args:
        urls: List of public URLs to extract content from
        objective: What content to extract (guides excerpt selection)
        excerpts: Return focused passages aligned with objective (default: True)
        full_content: Return complete page content as markdown (default: False)
    """
    body: dict[str, Any] = {
        "urls": urls,
        "excerpts": excerpts,
        "full_content": full_content,
    }

    if objective:
        body["objective"] = objective

    return await _request(HttpMethod.POST, "/extract", body=body)


# --- Export ------------------------------------------------------------------

parallel_tools = [
    parallel_search,
    parallel_extract,
]
