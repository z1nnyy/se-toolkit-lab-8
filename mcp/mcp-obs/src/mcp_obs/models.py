"""Typed models for observability MCP responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    timestamp: str | None = None
    service: str | None = None
    severity: str | None = None
    event: str | None = None
    trace_id: str | None = None
    message: str | None = None
    path: str | None = None
    status_code: int | None = None
    error: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ErrorCount(BaseModel):
    service: str
    count: int


class TraceSummary(BaseModel):
    trace_id: str
    service_names: list[str]
    span_count: int
    root_operation: str | None = None
    start_time: int | None = None
    duration_ms: float | None = None
    error_span_count: int = 0


class TraceSpan(BaseModel):
    span_id: str
    operation: str
    service_name: str | None = None
    start_time: int | None = None
    duration_ms: float | None = None
    error: bool = False
    tags: dict[str, Any] = Field(default_factory=dict)


class TraceDetails(BaseModel):
    trace_id: str
    service_names: list[str]
    spans: list[TraceSpan]
    error_span_count: int
