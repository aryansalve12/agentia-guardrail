<!-- Agentia managed skill file: agentia setup skills -->

# AI Agents Reference

Use this reference for `agentia ai agent ask`, `agentia ai agent chat`, and the matching `agentia_ai_ask` MCP tool.

## Authentication And Context

Configure AI once:

```sh
agentia auth set --ai --ai-domain <domain> --ai-org <organization-id> --ai-workspace <workspace-id>
agentia auth get --ai --json
```

Operational options include `--workspace` and `--timeout`; authentication is resolved from `agentia auth set`, supported `AGENTIA_AI_*` environment variables, or the configured profile. Do not print PAT values.

## Agent Selectors

| Selector | Use For |
| --- | --- |
| `plan` | Break requirements into delivery plans and acceptance criteria. |
| `build` | Implementation guidance, code-level questions, and construction tasks. |
| `test` | Test strategy, regression selection, and test troubleshooting. |
| `release` | Release, promotion, packaging, and deployment questions. |
| `operate` | Operational diagnostics, monitoring, and runbook style questions. |
| `knowledge` | Copado AI Knowledge grounding, product documentation, personas, and troubleshooting. |
| `orchestrate` | Chat-only orchestration mode for interactive sessions. |

Pass the selected value with the required `--agent` option. `ask` accepts `plan`, `build`, `test`, `release`, `operate`, or `knowledge`; `chat` also accepts `orchestrate`. `ask` requires a prompt with `-p` or `--prompt`; `chat` is TTY-only and prompts interactively.

## Single-Turn Ask

Use `ask` for automation and agent-to-agent workflows:

```sh
agentia ai agent ask --agent plan -p "Break this user story into implementation steps" --json
agentia ai agent ask --agent knowledge -p "Summarize Copado guidance for data template sync" --no-stream --json
agentia ai agent ask --agent build --user-story US-1042 --component AccountService -p "Review the implementation approach" --json
```

MCP `agentia_ai_ask` mirrors the buffered JSON-safe ask flow. It does not provide interactive chat.

## Interactive Chat

Use `chat` only when a human is present in a terminal:

```sh
agentia ai agent chat --agent build --user-story US-1042
agentia ai agent chat --agent orchestrate --workspace <workspace-id>
```

Chat creates or reuses one dialogue for the session and supports session slash commands. It is not suitable for headless JSON workflows.

## Workspace And Quota Helpers

Use these adjacent commands when the prompt workflow needs context setup:

| Command | Use For |
| --- | --- |
| `ai workspace list|get|create|update` | Inspect or manage Copado AI workspaces. |
| `ai workspace member list|invite` | Inspect or invite workspace members. |
| `ai quota get` | Check organization quota before large AI activity. |

## Gotchas

- `--workspace` selects the workspace; `--dialogue` reuses a conversation inside that workspace.
- `--user-story`, `--sf-org`, and `--component` enrich prompt context but do not replace a clear prompt.
- Streaming is human-friendly. For tools, CI, or follow-up parsing, use `--json` and consider `--no-stream`.
- `chat` has no MCP equivalent and should not be used in non-interactive shells.
