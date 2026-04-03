# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

Prompt:
`What is 2+2?`

Agent response:

```text
2 + 2 = 4 🐈
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
`Describe the architecture of the LMS system`

Agent response:

```text
The LMS system follows a layered architecture:

- Browser clients access the system through Caddy on port 42002.
- Caddy reverse-proxies API requests to the backend service.
- The backend service exposes LMS endpoints and analytics endpoints.
- PostgreSQL stores LMS items, learners, and interactions.
- The ETL pipeline syncs data from the autochecker into the backend database.
- Nanobot can access the LMS through the mcp_lms server, which calls the backend.
- Qwen Code API provides the LLM endpoint used by nanobot.
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

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
