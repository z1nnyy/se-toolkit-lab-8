"""Stdio MCP server exposing observability tools."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

from mcp_obs.client import ObservabilityClient
from mcp_obs.models import ErrorCount, LogEntry, TraceDetails, TraceSummary
from mcp_obs.settings import resolve_settings


class LogsSearchArgs(BaseModel):
    query: str = ""
    service: str | None = None
    severity: str | None = None
    minutes: int = Field(default=10, ge=1, le=1440)
    limit: int = Field(default=20, ge=1, le=200)


class LogsErrorCountArgs(BaseModel):
    service: str | None = None
    minutes: int = Field(default=10, ge=1, le=1440)
    limit: int = Field(default=200, ge=1, le=1000)


class TracesListArgs(BaseModel):
    service: str = "Learning Management Service"
    minutes: int = Field(default=10, ge=1, le=1440)
    limit: int = Field(default=10, ge=1, le=100)


class TracesGetArgs(BaseModel):
    trace_id: str


ToolPayload = LogEntry | ErrorCount | TraceSummary | TraceDetails


class ToolSpec(BaseModel):
    name: str
    description: str
    model: type[BaseModel]
    handler_name: str

    def as_tool(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.model.model_json_schema(),
        )


TOOL_SPECS = [
    ToolSpec(
        name="logs_search",
        description="Search VictoriaLogs by query, service, severity, and time window.",
        model=LogsSearchArgs,
        handler_name="logs_search",
    ),
    ToolSpec(
        name="logs_error_count",
        description="Count recent error logs per service over a time window.",
        model=LogsErrorCountArgs,
        handler_name="logs_error_count",
    ),
    ToolSpec(
        name="traces_list",
        description="List recent traces for a service from VictoriaTraces.",
        model=TracesListArgs,
        handler_name="traces_list",
    ),
    ToolSpec(
        name="traces_get",
        description="Fetch a specific trace by ID from VictoriaTraces.",
        model=TracesGetArgs,
        handler_name="traces_get",
    ),
]
TOOLS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}


def _text(data: ToolPayload | list[ToolPayload]) -> list[TextContent]:
    if isinstance(data, list):
        payload = [item.model_dump() for item in data]
    else:
        payload = data.model_dump()
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]


async def _dispatch(
    client: ObservabilityClient,
    name: str,
    arguments: dict[str, Any] | None,
) -> list[TextContent]:
    spec = TOOLS_BY_NAME.get(name)
    if spec is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    try:
        args = spec.model.model_validate(arguments or {})
        result = await getattr(client, spec.handler_name)(**args.model_dump())
        return _text(result)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


def create_server(client: ObservabilityClient) -> Server:
    server = Server("obs")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [spec.as_tool() for spec in TOOL_SPECS]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[TextContent]:
        return await _dispatch(client, name, arguments)

    _ = list_tools, call_tool
    return server


async def main() -> None:
    settings = resolve_settings()
    async with ObservabilityClient(
        settings.victorialogs_url,
        settings.victoriatraces_url,
    ) as client:
        server = create_server(client)
        async with stdio_server() as (read_stream, write_stream):
            init_options = server.create_initialization_options()
            await server.run(read_stream, write_stream, init_options)
