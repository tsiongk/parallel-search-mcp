# Copyright (c) 2025 Dedalus Labs, Inc. and its contributors
# SPDX-License-Identifier: MIT

from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings

from parallel import parallel_api, parallel_tools


# --- Server ------------------------------------------------------------------

server = MCPServer(
    name="parallel-search-mcp",
    connections=[parallel_api],
    http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    streamable_http_stateless=True,  # Required for Lambda deployments
)


async def main() -> None:
    server.collect(*parallel_tools)
    await server.serve(port=8080)
