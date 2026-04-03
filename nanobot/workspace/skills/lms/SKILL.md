---
name: lms
description: Use LMS MCP tools for live LMS data and ask for a lab when needed
always: true
---

# LMS Skill

Use the `lms_*` MCP tools whenever the user asks about real LMS data.

## Available tools

- `lms_health`: check whether the LMS backend is healthy
- `lms_labs`: list available labs
- `lms_learners`: list learners
- `lms_pass_rates`: get pass rates for a lab
- `lms_timeline`: get a submission timeline for a lab
- `lms_groups`: get group performance for a lab
- `lms_top_learners`: get top learners for a lab
- `lms_completion_rate`: get lab completion rate
- `lms_sync_pipeline`: trigger LMS sync if backend data is missing or stale

## Strategy

- Prefer live `lms_*` tools over guessing from local files.
- If the user asks about labs, scores, pass rates, completion, groups, timeline,
  or top learners without naming a lab, call `lms_labs` first.
- If multiple labs are available and the user did not specify one, ask them to
  choose a lab.
- When the current channel supports interactive UI and the `mcp_webchat_ui_message`
  tool is available, let the shared `structured-ui` skill present the lab choice.
- If the backend is healthy but no lab data is available yet, use
  `lms_sync_pipeline` and retry the question.

## Response style

- Keep answers concise.
- Format percentages and scores clearly.
- When listing labs, prefer stable identifiers such as `lab-01`.
- When the user asks "what can you do?", explain that you can answer questions
  using live LMS data through MCP tools, but only for tools that are currently
  configured.
