---
name: agentia-testing
description: Use this skill when creating, updating, running, inspecting, or troubleshooting Copado Robotic Testing with the Agentia CLI, including projects, permissions, robots, jobs, builds, schedules, data tables, variables, user parameters, live testing, Git-backed storage, and Robot Framework execution.
---

<!-- Agentia managed skill file: agentia setup skills -->

# Agentia Testing

Use this skill to operate Copado Robotic Testing through Agentia without confusing CRT resources, executions, live sessions, and Copado CICD records.

Prefer Agentia MCP tools when they are available and match the task. Use CLI examples as the fallback, and add `--json` whenever the result will be parsed or reused.

## Start Here

1. Confirm CRT auth with `agentia auth get --crt --json`. Configure missing credentials with `agentia auth set --crt ...` or the supported `AGENTIA_CRT_*` environment variables.
2. Identify or create the CRT Project and Robot before creating or running tests. Use explicit project and job IDs; do not invent hidden active-resource defaults.
3. Use `testing test ...` as the canonical namespace for test workflows. The shorter `testing run|logs|status|create|update` forms exist for compatibility.
4. Never expose PAKs, session cookies, viewer keys, variable values, or generated log content that contains secrets.

## Reference

- CRT lifecycle, execution, schedules, data tables, live testing, and safety rules: [references/tests.md](references/tests.md)

## General Rules

- `agentia testing test run` starts CRT Robot Framework execution. It is different from `agentia cicd work test --local`.
- `agentia testing job` manages CRT job/test definitions. It is different from `agentia cicd job`, which manages Copado CICD JobExecution records.
- Use `--wait-for-result` on `testing test run` when the agent must return the final build result in one turn.
- Use Git-backed job flags only when the user or project clearly uses repository-backed CRT test storage.
- In JSON or non-interactive CLI calls, destructive actions require `--yes`; matching MCP tools require `confirm: true`.
- Prefer `--value-stdin` and `--git-password-stdin` over putting secrets in process arguments.
- Use the currently configured CRT credential context for validation. Test14 credentials belong to CICD and must not be substituted for CRT credentials.

## Report Back

Report the CRT project, robot, job/test ID, build or live-session ID when present, final status, cleanup, and where outputs were written. Do not include PAKs or other secrets.
