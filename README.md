# parallel-search-mcp

A [Dedalus MCP server](https://www.dedaluslabs.ai) for Parallel Web Search and Extract API.

## Features

- **2 tools** for web search and content extraction
- Search: parallel web searches with customizable objectives
- Extract: content extraction from URLs with excerpt or full content modes
- Secure API key authentication via Dedalus enclave

## Available Tools

| Tool | Description |
|------|-------------|
| `parallel_search` | Search the web using Parallel's Search API |
| `parallel_extract` | Extract content from URLs using Parallel's Extract API |

## Requirements

- Python 3.10+
- Parallel API key
- Dedalus account

## Setup

1. Clone the repository:
```bash
git clone https://github.com/dedalus-labs/parallel-search-mcp.git
cd parallel-search-mcp
```

2. Install dependencies:
```bash
uv sync
```

3. Create a `.env` file with your credentials:
```bash
PARALLEL_API_KEY=your_api_key_here
```

4. Run the server locally:
```bash
cd src && uv run python main.py
```

## Getting a Parallel API Key

1. Go to the [Parallel Developer Portal](https://docs.parallel.ai)
2. Create an account and generate an API key
3. Copy the key to your `.env` file

## Usage with Dedalus

This server is available on the [Dedalus Marketplace](https://www.dedaluslabs.ai) with slug `dedalus-labs/parallel-search-mcp`.

```python
from dedalus_labs import AsyncDedalus, DedalusRunner
from dedalus_mcp.auth import SecretValues

client = AsyncDedalus(api_key="your_dedalus_api_key")
runner = DedalusRunner(client)

result = await runner.run(
    input="Search for the latest AI news",
    model="anthropic/claude-sonnet-4-20250514",
    mcp_servers=["dedalus-labs/parallel-search-mcp"],
    credentials=[SecretValues(parallel_api, token="your_parallel_api_key")],
)
```

## Tool Details

### parallel_search

Search the web with multiple queries in parallel.

**Parameters:**
- `queries` (list[str]): List of search queries to execute
- `objective` (str, optional): High-level objective to guide result relevance
- `max_results` (int): Maximum results per query (default: 10)
- `max_chars_per_result` (int): Maximum characters per result excerpt (default: 10000)

### parallel_extract

Extract content from web pages.

**Parameters:**
- `urls` (list[str]): List of public URLs to extract content from
- `objective` (str, optional): What content to extract (guides excerpt selection)
- `excerpts` (bool): Return focused passages aligned with objective (default: True)
- `full_content` (bool): Return complete page content as markdown (default: False)

## License

MIT License - see [LICENSE](LICENSE) for details.
