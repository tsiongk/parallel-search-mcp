# Copyright (c) 2026 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

"""Parallel Web MCP Server - Search and Extract APIs."""

from .search import (
    parallel_search,
    extract,
    SearchResponse,
    SearchResult,
    ExtractResponse,
    ExtractResult,
)

__all__ = [
    "parallel_search",
    "extract",
    "SearchResponse",
    "SearchResult",
    "ExtractResponse",
    "ExtractResult",
]
