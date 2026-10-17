\---

name: guardrail

description: Use this skill before submitting, publishing or promoting any change with the Agentia CLI. It runs the Agentia Guardrail policy check on the Git diff, explains each finding, and tells the agent how to fix it. Use it whenever the user asks to submit, publish, promote or deploy Salesforce changes.

\---



\# Agentia Guardrail



Guardrail checks the actual Git changes against the organization's rules in `guardrail.yml` and returns one decision: PASS, WARN, APPROVAL REQUIRED or BLOCK. The policy engine decides. You explain and fix. A human approves.



\## Before submitting



1\. Commit your changes on the feature branch.

2\. Run `python guardrail.py` from the project root.

3\. Read the decision and every finding line.



\## How to react



\- \*\*PASS\*\*: continue with `agentia cicd work submit`.

\- \*\*BLOCK\*\*: do not submit. Fix the cause, commit, and run the check again.

&#x20; - `APEX\_TEST\_REQUIRED`: add or update a matching `\*Test.cls` class.

&#x20; - `DESTRUCTIVE\_CHANGE`: restore the deleted object or field, or ask the user.

\- \*\*APPROVAL REQUIRED\*\*: stop. Tell the user which rule fired and which file. Ask them to review and approve it themselves. Wait for the user.



\## Hard rules



\- Never run `python guardrail.py approve ...`. Only a human may approve.

\- Never edit `.guardrail/approvals.json`, `.guardrail/audit.jsonl` or `guardrail.yml`.

\- Never use `--skip-local-tests` or edit `.agentia\_quality\_gates.cmd` to avoid the check.

\- Never report a change as safe unless the latest run printed `Decision: PASS`.



\## Report back



State the decision, each rule that fired, what you changed to fix it, and whether a human approval is still needed.

