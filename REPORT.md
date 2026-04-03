# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

Prompt:
`What is 2+2?`

Agent response:

```text
2 + 2 equals 4.
```

Prompt:
`What labs are available in our LMS?`

Agent response before live LMS wiring:

```text
The LMS MCP tools aren't currently connected in my runtime, so I can't query live LMS data. However, I can see the lab tasks available in this environment:

Lab 8 — Required Tasks:
1 task-1.md
2 task-2.md
3 task-3.md
4 task-4.md
5 task-5.md
```

## Task 1B — Agent with LMS tools

Prompt:
`What labs are available?`

Agent response:

```text
The following labs are available:

1 Lab 01 – Products, Architecture & Roles
2 Lab 02 — Run, Fix, and Deploy a Backend Service
3 Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4 Lab 04 — Testing, Front-end, and AI Agents
5 Lab 05 — Data Pipeline and Analytics Dashboard
6 Lab 06 — Build Your Own Agent
7 Lab 07 — Build a Client with an AI Coding Agent
8 Lab 08
```

Prompt:
`Is the LMS backend healthy?`

Agent response summary:

```text
The LMS backend is currently healthy with 56 items and no reported errors.
```

## Task 1C — Skill prompt

Prompt:
`Show me the scores`

Agent response:

```text
Here are the scores from the LMS:

Lab 01 — Products, Architecture & Roles
Completion Rate: 93.9% (108 passed / 115 total)

Task                                        Avg Score  Attempts
Lab setup                                   97.2%      119
Task 0: Practice the Git workflow           65.2%      214
Task 1: Product & architecture description  59.4%      90
Task 2: Roles and skills mapping            53.9%      42
Optional: Resolve a merge conflict          41.7%      6
Optional: Create a release                  50.0%      2
Optional: Add a CI check                    25.0%      4
Optional: Plan skill development            0.0%       1

Labs 02–08
No submission data yet — all show 0 completions and no pass rate data.
```

## Task 2A — Deployed agent

Startup log excerpt:

```text
Using config: /app/nanobot/config.resolved.json
🐈 Starting nanobot gateway version 0.1.4.post5 on port 18790...
WebChat channel enabled
Channels enabled: webchat
MCP server 'lms': connected, 9 tools registered
MCP server 'webchat': connected, 1 tools registered
Agent loop started
```

## Task 2B — Web client

Web client evidence:

```text
GET /flutter/ -> HTTP/1.1 200 OK
GET /ws/chat with plain curl -> HTTP/1.1 426 Upgrade Required
```

Conversation evidence:

```text
User: What labs are available?
Agent:
1 Lab 01 – Products, Architecture & Roles
2 Lab 02 — Run, Fix, and Deploy a Backend Service
3 Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4 Lab 04 — Testing, Front-end, and AI Agents
5 Lab 05 — Data Pipeline and Analytics Dashboard
6 Lab 06 — Build Your Own Agent
7 Lab 07 — Build a Client with an AI Coding Agent
8 Lab 08
```

## Task 3A — Structured logging

Happy-path log excerpt:

```text
HTTP Request: POST https://portal.qwen.ai/v1/chat/completions "HTTP/1.1 200 OK"
POST /v1/chat/completions HTTP/1.1" 200 OK
```

Error-path log excerpt:

```text
socket.gaierror: [Errno -2] Name or service not known
HTTP/1.1 500 Internal Server Error
```

VictoriaLogs query used:

```text
_time:10m service.name:"Learning Management Service" severity:ERROR
```

## Task 3B — Traces

Trace evidence summary:

```text
Healthy traces showed LMS requests completing successfully.
Failure traces showed the same request path ending in a database connectivity failure.
The failing path correlated with logs containing:
socket.gaierror: [Errno -2] Name or service not known
```

## Task 3C — Observability MCP tools

Prompt:
`Any LMS backend errors in the last 10 minutes?`

Normal-condition response:

```text
No LMS backend errors in the last 2 minutes. The system looks healthy.
```

Failure-condition response after stopping PostgreSQL:

```text
Yes, there are LMS backend errors.

Root Cause: PostgreSQL container has exited

Component   Status
postgres-1  Exited
backend-1   Running, but all endpoints failing

All LMS endpoints are failing:
- /items/ -> 404 Not Found
- /learners/ -> 500 Internal Server Error
- /pipeline/sync -> 500 Internal Server Error
```

## Task 4A — Multi-step investigation

Prompt:
`What went wrong?`

Agent response:

```text
Here's what I found from the last 30 minutes:

Root Cause: Database DNS Resolution Failure (Learning Management Service)

9 errors in the Learning Management Service, all stemming from the same issue:
- Error: socket.gaierror: [Errno -2] Name or service not known
- Affected endpoints: /items/, /learners/, and /pipeline/sync
- Trace evidence: Multiple traces all show the same gaierror at the asyncpg.connect -> uvloop.create_connection level.

Secondary Issue: Token Refresh Failure (Qwen Code API)
The Qwen Code API token refresh endpoint returned an HTML WAF block page instead of JSON.
```

## Task 4B — Proactive health check

Health-check creation transcript:

```text
Done! Health check cron job created:
- Job ID: ce48a251
- Interval: Every 2 minutes
- Behavior: Checks for LMS/backend errors in the last 2 minutes, inspects traces if needed, and posts a short summary here.
```

Scheduled-jobs transcript:

```text
Here are your scheduled jobs:
Health check: Check for LMS/backend errors  ce48a251  Every 2 minutes
```

## Task 4C — Bug fix and recovery

Root cause:

```text
The backend items router hid real backend/database failures behind a broad exception handler and returned a misleading 404 "Items not found".
```

Fix:

```text
Removed the broad exception handling in backend/src/lms_backend/routers/items.py so the real database failure now surfaces through the global exception handler as HTTP 500.
```

Post-fix failure evidence:

```text
HTTP/1.1 500 Internal Server Error
{"detail":"[Errno -2] Name or service not known","type":"gaierror","path":"/items/"}
```

Healthy follow-up:

```text
Prompt: Any LMS backend errors in the last 2 minutes?
Response: No LMS backend errors in the last 2 minutes. The system looks healthy.
```
