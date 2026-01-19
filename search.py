# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Parallel Web API integration.

Provides Search and Extract functionality using Parallel's API.
API docs: https://docs.parallel.ai
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from pydantic import BaseModel, Field

PARALLEL_API_BASE = "https://api.parallel.ai/v1beta"
PARALLEL_BETA_HEADER = "search-extract-2025-10-10"


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


async def parallel_search(
    queries: list[str],
    objective: str | None = None,
    max_results: int = 10,
    max_chars_per_result: int = 10000,
    api_key: str | None = None,
) -> list[SearchResponse]:
    """Execute parallel web searches using Parallel API.

    Args:
        queries: List of search queries to execute in parallel
        objective: Optional high-level objective to guide result relevance
        max_results: Maximum results per query (default: 10)
        max_chars_per_result: Maximum characters per result excerpt (default: 10000)
        api_key: API key (defaults to PARALLEL_API_KEY env var)

    Returns:
        List of SearchResponse objects, one per query
    """
    api_key = api_key or os.getenv("PARALLEL_API_KEY")
    if not api_key:
        raise ValueError("PARALLEL_API_KEY environment variable not set")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "parallel-beta": PARALLEL_BETA_HEADER,
    }

    # Build the request body
    body: dict[str, Any] = {
        "search_queries": queries,
        "max_results": max_results,
        "excerpts": {"max_chars_per_result": max_chars_per_result},
    }

    if objective:
        body["objective"] = objective
    else:
        # Default objective based on queries
        body["objective"] = f"Find relevant information for: {', '.join(queries)}"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{PARALLEL_API_BASE}/search",
            headers=headers,
            json=body,
        )

        if response.status_code != 200:
            raise Exception(f"Parallel API error ({response.status_code}): {response.text}")

        data = response.json()

    # Parse results - API returns results grouped by query
    responses: list[SearchResponse] = []

    # Handle the response format from Parallel API
    results_data = data.get("results", [])

    # If results are grouped by query
    if isinstance(results_data, list) and len(results_data) > 0:
        # Check if results have query-level grouping
        if isinstance(results_data[0], dict) and "query" in results_data[0]:
            for result_group in results_data:
                query = result_group.get("query", "")
                items = result_group.get("results", [])
                search_results = [
                    SearchResult(
                        title=item.get("title"),
                        url=item.get("url"),
                        excerpt=item.get("excerpt") or item.get("content"),
                        source=item.get("source"),
                    )
                    for item in items
                ]
                responses.append(SearchResponse(
                    query=query,
                    results=search_results,
                    total_results=len(search_results),
                ))
        else:
            # Flat results - excerpts is a list, join into single string
            search_results = [
                SearchResult(
                    title=item.get("title"),
                    url=item.get("url"),
                    excerpt="\n\n".join(item.get("excerpts", [])) if item.get("excerpts") else item.get("content"),
                    source=item.get("source"),
                )
                for item in results_data
            ]
            # All results belong to the batch of queries
            responses.append(SearchResponse(
                query=", ".join(queries),
                results=search_results,
                total_results=len(search_results),
            ))
    else:
        # Empty or unexpected format - return empty responses
        for query in queries:
            responses.append(SearchResponse(
                query=query,
                results=[],
                total_results=0,
            ))

    return responses


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


async def extract(
    urls: list[str],
    objective: str | None = None,
    excerpts: bool = True,
    full_content: bool = False,
    api_key: str | None = None,
) -> ExtractResponse:
    """Extract content from URLs using Parallel API.

    Args:
        urls: List of public URLs to extract content from
        objective: What content to extract (guides excerpt selection)
        excerpts: Return focused passages aligned with objective (default: True)
        full_content: Return complete page content as markdown (default: False)
        api_key: API key (defaults to PARALLEL_API_KEY env var)

    Returns:
        ExtractResponse with results per URL
    """
    api_key = api_key or os.getenv("PARALLEL_API_KEY")
    if not api_key:
        raise ValueError("PARALLEL_API_KEY environment variable not set")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "parallel-beta": PARALLEL_BETA_HEADER,
    }

    body: dict[str, Any] = {
        "urls": urls,
        "excerpts": excerpts,
        "full_content": full_content,
    }

    if objective:
        body["objective"] = objective

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{PARALLEL_API_BASE}/extract",
            headers=headers,
            json=body,
        )

        if response.status_code != 200:
            raise Exception(f"Parallel API error ({response.status_code}): {response.text}")

        data = response.json()

    results = [
        ExtractResult(
            url=item.get("url", ""),
            title=item.get("title"),
            publish_date=item.get("publish_date"),
            excerpts=item.get("excerpts"),
            full_content=item.get("full_content"),
        )
        for item in data.get("results", [])
    ]

    return ExtractResponse(
        extract_id=data.get("extract_id"),
        results=results,
        errors=data.get("errors", []),
    )
