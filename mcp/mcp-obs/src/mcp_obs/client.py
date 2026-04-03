"""Async HTTP client for VictoriaLogs and VictoriaTraces."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from mcp_obs.models import ErrorCount, LogEntry, TraceDetails, TraceSpan, TraceSummary


def _now_us() -> int:
    return int(datetime.now(UTC).timestamp() * 1_000_000)


def _time_window_us(minutes: int) -> tuple[int, int]:
    end = _now_us()
    start = int((datetime.now(UTC) - timedelta(minutes=minutes)).timestamp() * 1_000_000)
    return start, end


def _quote(value: str) -> str:
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def _build_logs_query(
    *,
    query: str = "",
    service: str | None = None,
    severity: str | None = None,
    minutes: int = 10,
) -> str:
    parts: list[str] = [f"_time:{minutes}m"]
    if service:
        parts.append(f"service.name:{_quote(service)}")
    if severity:
        parts.append(f"severity:{severity.upper()}")
    if query:
        parts.append(query)
    return " ".join(parts)


def _deep_get(value: Any, *path: str) -> Any:
    current = value
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def _pick_field(payload: dict[str, Any], *candidates: str) -> Any:
    for candidate in candidates:
        if candidate in payload:
            return payload[candidate]
        if "." in candidate:
            nested = _deep_get(payload, *candidate.split("."))
            if nested is not None:
                return nested
    resource = payload.get("resource", {})
    attributes = resource.get("attributes", {}) if isinstance(resource, dict) else {}
    for candidate in candidates:
        if candidate in attributes:
            return attributes[candidate]
    return None


def _to_log_entry(payload: dict[str, Any]) -> LogEntry:
    status_code = _pick_field(payload, "status_code", "http.status_code")
    try:
        status_code_int = int(status_code) if status_code is not None else None
    except (TypeError, ValueError):
        status_code_int = None

    return LogEntry(
        timestamp=_pick_field(payload, "_time", "time", "timestamp", "Timestamp"),
        service=_pick_field(payload, "service.name", "service_name"),
        severity=_pick_field(payload, "severity", "severity_text", "SeverityText"),
        event=_pick_field(payload, "event"),
        trace_id=_pick_field(payload, "trace_id", "TraceId"),
        message=_pick_field(payload, "_msg", "body", "message", "msg"),
        path=_pick_field(payload, "path", "http.target", "http.route"),
        status_code=status_code_int,
        error=_pick_field(payload, "error", "exception.message"),
        raw=payload,
    )


def _span_error(tags: list[dict[str, Any]]) -> bool:
    for tag in tags:
        key = str(tag.get("key", ""))
        value = tag.get("value")
        if key == "error" and value in (True, "true", "True"):
            return True
        if key in {"otel.status_code", "status.code"} and value == "ERROR":
            return True
    return False


def _span_tags(tags: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for tag in tags:
        key = str(tag.get("key", ""))
        if key:
            result[key] = tag.get("value")
    return result


def _trace_summary(trace: dict[str, Any]) -> TraceSummary:
    spans = trace.get("spans", [])
    processes = trace.get("processes", {})
    service_names = sorted(
        {
            str(processes.get(span.get("processID"), {}).get("serviceName", ""))
            for span in spans
            if span.get("processID") in processes
        }
        - {""}
    )
    if spans:
        start = min(int(span.get("startTime", 0)) for span in spans)
        end = max(int(span.get("startTime", 0)) + int(span.get("duration", 0)) for span in spans)
        duration_ms = round((end - start) / 1000, 2)
        root_operation = spans[0].get("operationName")
    else:
        start = None
        duration_ms = None
        root_operation = None
    error_span_count = sum(_span_error(span.get("tags", [])) for span in spans)
    return TraceSummary(
        trace_id=str(trace.get("traceID", "")),
        service_names=service_names,
        span_count=len(spans),
        root_operation=root_operation,
        start_time=start,
        duration_ms=duration_ms,
        error_span_count=error_span_count,
    )


def _trace_details(trace: dict[str, Any]) -> TraceDetails:
    processes = trace.get("processes", {})
    spans: list[TraceSpan] = []
    service_names: set[str] = set()
    error_count = 0
    for span in trace.get("spans", []):
        process = processes.get(span.get("processID"), {})
        service_name = process.get("serviceName")
        if isinstance(service_name, str) and service_name:
            service_names.add(service_name)
        tags = span.get("tags", [])
        is_error = _span_error(tags)
        if is_error:
            error_count += 1
        spans.append(
            TraceSpan(
                span_id=str(span.get("spanID", "")),
                operation=str(span.get("operationName", "")),
                service_name=service_name if isinstance(service_name, str) else None,
                start_time=span.get("startTime"),
                duration_ms=round(int(span.get("duration", 0)) / 1000, 2)
                if span.get("duration") is not None
                else None,
                error=is_error,
                tags=_span_tags(tags),
            )
        )
    return TraceDetails(
        trace_id=str(trace.get("traceID", "")),
        service_names=sorted(service_names),
        spans=spans,
        error_span_count=error_count,
    )


class ObservabilityClient:
    """Client for VictoriaLogs and VictoriaTraces APIs."""

    def __init__(
        self,
        victorialogs_url: str,
        victoriatraces_url: str,
        *,
        timeout: float = 10.0,
    ) -> None:
        self._logs = httpx.AsyncClient(base_url=victorialogs_url.rstrip("/"), timeout=timeout)
        self._traces = httpx.AsyncClient(base_url=victoriatraces_url.rstrip("/"), timeout=timeout)

    async def __aenter__(self) -> ObservabilityClient:
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._logs.aclose()
        await self._traces.aclose()

    async def logs_search(
        self,
        *,
        query: str = "",
        service: str | None = None,
        severity: str | None = None,
        minutes: int = 10,
        limit: int = 20,
    ) -> list[LogEntry]:
        logs_query = _build_logs_query(
            query=query,
            service=service,
            severity=severity,
            minutes=minutes,
        )
        response = await self._logs.get(
            "/select/logsql/query",
            params={"query": logs_query, "limit": limit},
        )
        response.raise_for_status()
        entries: list[LogEntry] = []
        for line in response.text.splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                entries.append(LogEntry(message=line, raw={"line": line}))
                continue
            if isinstance(payload, dict):
                entries.append(_to_log_entry(payload))
        return entries

    async def logs_error_count(
        self,
        *,
        service: str | None = None,
        minutes: int = 10,
        limit: int = 200,
    ) -> list[ErrorCount]:
        entries = await self.logs_search(
            service=service,
            severity="ERROR",
            minutes=minutes,
            limit=limit,
        )
        counts = Counter(entry.service or "unknown" for entry in entries)
        return [
            ErrorCount(service=name, count=count)
            for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]

    async def traces_list(
        self,
        *,
        service: str,
        minutes: int = 10,
        limit: int = 10,
    ) -> list[TraceSummary]:
        start, end = _time_window_us(minutes)
        response = await self._traces.get(
            "/select/jaeger/api/traces",
            params={
                "service": service,
                "limit": limit,
                "start": start,
                "end": end,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return [_trace_summary(trace) for trace in payload.get("data", []) if isinstance(trace, dict)]

    async def traces_get(self, trace_id: str) -> TraceDetails:
        response = await self._traces.get(f"/select/jaeger/api/traces/{trace_id}")
        response.raise_for_status()
        payload = response.json()
        traces = payload.get("data", [])
        if not traces:
            return TraceDetails(trace_id=trace_id, service_names=[], spans=[], error_span_count=0)
        trace = traces[0]
        return _trace_details(trace if isinstance(trace, dict) else {})
