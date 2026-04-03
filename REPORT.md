# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

Prompt:
`What is the agentic loop?`

Agent response:

```text
The agentic loop is the cycle an AI agent follows to complete a task:

1. Understand the user's request and current context.
2. Decide what action to take next.
3. Use available tools when needed.
4. Observe the results of those tools.
5. Update its plan or response based on the new information.
6. Repeat until the task is finished.

In nanobot, this loop is built into the framework, so the agent can reason,
call tools, read their outputs, and continue iterating without you manually
implementing that control flow.
```

Prompt:
`What labs are available in our LMS?`

Agent response:

```text
Here are the available labs:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. Lab 08 — lab-08
```

## Task 1B — Agent with LMS tools

Prompt:
`What labs are available?`

Agent response:

```text
Here are the available labs:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. Lab 08 — lab-08

Would you like details on any specific lab, such as pass rates, completion
rates, group performance, or top learners?
```

Prompt:
`Is the LMS backend healthy?`

Agent response:

```text
Yes — the LMS backend is healthy.

The health check succeeded, and the backend currently has real data available,
including 8 labs in the LMS.
```

## Task 1C — Skill prompt

Prompt:
`Show me the scores`

Agent response:

```text
There are multiple labs available. Please choose which lab you want scores for:

1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. Lab 08 — lab-08
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
