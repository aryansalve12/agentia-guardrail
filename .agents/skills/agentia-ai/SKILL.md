---
name: agentia-ai
description: Use this skill when prompting Copado AI agents through the Agentia CLI or MCP, including `agentia ai agent ask`, `agentia ai agent chat`, Plan, Build, Test, Release, Operate, Knowledge, workspace, dialogue, user story, Salesforce org, and component context.
---

<!-- Agentia managed skill file: agentia setup skills -->

# Agentia AI

Use this skill to ask Copado AI agents through Agentia with the right agent selector, workspace context, and output mode.

Prefer the `agentia_ai_ask` MCP tool when it is available for single-turn prompts. Use CLI examples as the fallback. Use `agentia ai agent chat` only for interactive terminal sessions.

## Start Here

1. Confirm AI auth with `agentia auth get --ai --json`. Configure missing credentials with `agentia auth set --ai ...` or the supported `AGENTIA_AI_*` environment variables.
2. Choose exactly one required `--agent` option for `ask`: `plan`, `build`, `test`, `release`, `operate`, or `knowledge`. `orchestrate` is not valid for `ask`.
3. Choose exactly one required `--agent` option for `chat`: `plan`, `build`, `test`, `release`, `operate`, `knowledge`, or `orchestrate`.
4. Add useful context flags when available: `--workspace`, `--dialogue`, `--user-story`, `--sf-org`, and `--component`.
5. Use `--json` for automation. Use `--no-stream` when the caller needs a buffered response.

## Reference

- Copado AI agent prompts, chat sessions, workspace context, MCP parity, and gotchas: [references/ai-agents.md](references/ai-agents.md)

## General Rules

- Keep prompts specific and include IDs or names read from Copado or the local project.
- Use the Knowledge agent for Copado AI Knowledge grounding and product questions.
- Use the Plan, Build, Test, Release, and Operate agents according to the lifecycle intent.
- Do not paste PATs or secrets into prompts.

## Report Back

Report the selected AI agent, workspace/dialogue identifiers when returned, whether the response was streamed or buffered, and any follow-up action. Do not include secrets.
