<!-- Agentia managed skill file: agentia setup skills -->

# CRT Testing Reference

Use this reference for Copado Robotic Testing commands under `agentia testing`.

## Authentication And Context

```sh
agentia auth set --crt <pak> --crt-domain <domain> --crt-org <organization-id>
agentia auth get --crt --json
```

Proceed only when the CRT credential entry reports `ready: true`. CRT commands resolve the configured CRT keychain context or supported `AGENTIA_CRT_*` process overrides. Do not pass PAKs in URLs or report them in output. Test14 is a CICD environment and is not a substitute for CRT credentials.

Use explicit `--project` and `--job` context. Agentia does not reproduce the legacy CLI's hidden active project/job selection.

## Canonical Test Workflow

1. Discover or create a project and robot.
2. Create a job/test using snapshot files or validated Git-backed storage.
3. Run through `testing test run` and optionally wait for the terminal build.
4. Inspect build detail, search, logs, artifacts, or xUnit.
5. Update the job or data inputs as needed.
6. Clean up regression-owned resources in reverse order with explicit confirmation.

```sh
agentia testing project list --json
agentia testing robot list --json
agentia testing test create --project <project-id> --robot <robot-id> --name "Smoke" --file tests/smoke.robot --json
agentia testing test run <job-id> --project <project-id> --wait-for-result --json
agentia testing build get <build-id> --project <project-id> --job <job-id> --json
agentia testing test logs <build-id> --project <project-id> --job <job-id> --output ./crt.log --json
```

## Command Areas

| Area | Commands |
| --- | --- |
| Projects | `testing project list|get|create|update|delete`; `project permission list|get|set|update` |
| Robots | `testing robot list|get|create|update|delete` |
| Jobs | `testing job list|get|create|update|delete|run|files|refs|upload|download` |
| Schedules | `testing job schedule get|set|remove` |
| Builds | `testing build run|list|get|latest|search|logs|abort` |
| Variables | `testing variable list|get|create|update|delete` |
| User parameters | `testing user-parameter list|get|create|update|delete` |
| Data tables | `testing data-table list|get|create|update|delete|export` |
| Live testing | `testing live start|stop|status|execute|continue|interrupt|inspect|screenshot|reports|set-options|history|view|recorder` |

`testing create|update|run|status|logs` remain compatibility aliases. Prefer `testing test` for test workflows and canonical resource commands for new automation.

## Execution And Builds

- Use `--wait-for-result` when the result must include terminal build data.
- `--timeout` bounds waiting; `--no-exit-code` keeps a failed remote run from failing the local command when explicitly desired.
- `--save-artifacts` and `--xunit` write only to validated explicit paths.
- `--stream-logs` and `--watch` are human-only and cannot be combined with `--json`.
- Repeated `--datatable TABLE_ID:SELECTION` starts data-driven batch execution. It cannot be combined with wait, stream, artifact-save, or xUnit modes.
- Use build `get`, `latest`, and `search` instead of assuming list order.

## Schedules And Data Tables

Schedules support get, set with cron/timezone/record policy, and remove. Data tables accept CSV, TSV, JSON, and XLSX imports and support bounded preview and dataset selection. Export supports CSV, TSV, and XLSX.

Data-table create/update/delete and existing-file overwrite are protected operations. Never overwrite or delete without user intent.

## Live Testing

Use a regression-owned job:

```sh
agentia testing live start <job-id> --project <project-id> --json
agentia testing live status --project <project-id> --json
agentia testing live execute --project <project-id> --line "GoTo  https://example.com" --json
agentia testing live inspect --project <project-id> --json
agentia testing live stop --project <project-id> --yes --json
```

Live viewer secrets remain in the keychain. Session cookies and XSRF values are in-memory only. `view` opens an authenticated page without putting secrets in the URL. `recorder` is long-running and uses an owner-scoped local lock; neither `view` nor `recorder` is exposed through MCP.

## Secret Inputs And Redaction

- Prefer `--value-stdin`/`--value-file` for variable values.
- Prefer `--git-password-stdin`/`--git-password-file` or a CRT domain credential for Git authentication.
- Sensitive variable and user-parameter values must remain redacted in human, JSON, MCP, debug, and error output.
- Validate local paths, remote paths, and Git refs before mutation.

## Confirmation

Destructive or protected CLI actions prompt in an interactive TTY. JSON and non-TTY calls require `--yes`. Matching MCP tools require `confirm: true`, not a `yes` field.

This applies to resource deletion, build abort, schedule removal, live stop, protected data-table imports/deletion, and output overwrite.

## Gotchas

- `testing job` is a CRT test definition; `cicd job` is a Copado CICD JobExecution.
- There is no `testing test get` or `testing test delete`; use `testing job get` and `testing job delete`.
- CRT tenant users, organizations, groups, roles, licenses, and cross-region migration are intentionally not Agentia testing commands.
- Log, artifact, data-table, DOM, screenshot, and report commands may write files. Keep JSON stdout structured and report only sanitized output metadata.
