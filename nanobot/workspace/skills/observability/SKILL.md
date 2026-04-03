---
name: observability
description: Use logs and traces MCP tools to diagnose recent backend failures
always: true
---

# Observability Skill

Use the observability MCP tools whenever the user asks about errors, failures,
incidents, traces, logs, or what went wrong.

## Available tools

- `logs_search`: search recent logs in VictoriaLogs
- `logs_error_count`: count recent errors per service
- `traces_list`: list recent traces for a service
- `traces_get`: fetch a specific trace by ID

## Strategy

- For error questions, start with `logs_error_count`.
- For backend-focused questions, prefer the service name `Learning Management Service`.
- If there are recent errors, call `logs_search` with a narrow time window and
  inspect the most recent backend errors first.
- If a log entry contains a `trace_id`, call `traces_get` for that trace and
  use the trace to confirm where the failure happened.
- Use `traces_list` when you need recent traces for a service but do not have a
  trace ID yet.
- When the user asks `What went wrong?` or `Check system health`, perform one
  coherent investigation: error counts, recent backend logs, then a matching
  trace when a recent `trace_id` is available.
- In that explanation, explicitly mention both log evidence and trace evidence
  when you have both.
- When the user asks for a recurring health check in the current chat, use the
  built-in `cron` tool. Do not move that request into `HEARTBEAT.md`.
- For a chat health-check cron job, check recent backend errors first, inspect
  a trace when needed, and post a short summary that either names the failing
  service/root cause or says the system looks healthy.
- Summarize the root cause, affected service, and the most relevant failing
  path or operation. Do not dump raw JSON unless the user explicitly asks for it.

## Response style

- Keep answers short and diagnostic.
- Mention the time window you checked.
- When there are no recent backend errors, say that clearly.
