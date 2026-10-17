# \# Agentia Guardrail

# 

# \*\*Policy-as-Code for Safe AI-Driven Salesforce Delivery\*\*

# 

# > AI decides how to write the code. Your organization decides whether it is allowed to ship.

# 

# Built for the Agentia Headless Virtual Hackathon 2026.

# 

# \## Problem

# AI coding agents can produce Salesforce changes in minutes, but delivery policies often live in wikis or depend on manual review. Teams need version-controlled, explainable, auditable rules that apply to AI-generated changes the same way every time.

# 

# \## What it does

# Guardrail reads the real Git diff, applies rules from `guardrail.yml`, and returns one deterministic decision:

# 

# `PASS` | `WARN` | `APPROVAL REQUIRED` | `BLOCK` (strictest finding wins)

# 

# | Rule | Behaviour |

# |---|---|

# | APEX\_TEST\_REQUIRED | Changed Apex class with no changed `\*Test.cls` is blocked |

# | PERMISSION\_APPROVAL | Permission set / profile changes need human approval |

# | DESTRUCTIVE\_CHANGE | Deleting an object or field is blocked |

# | SENSITIVE\_METADATA | Configured paths (connected apps, remote sites) need approval |

# 

# Roles are separate: \*\*the policy engine decides, the AI agent explains and fixes, a human approves.\*\* No LLM makes the decision.

# 

# \## How it uses Agentia extensibility

# \- \*\*Command / local quality gate:\*\* `.agentia\_quality\_gates.cmd` calls `guardrail.py`. `agentia cicd work test --local` and `submit` run it, and a non-zero exit fails the gate.

# \- \*\*Skill:\*\* `.agents/skills/guardrail/SKILL.md` teaches agents to run the check, fix findings, and never approve for themselves.

# \- \*\*AGENTS.md:\*\* points agents to the skill before submit, publish or promote.

# 

# \## Audit trail

# Every finding, approval and final decision is appended to `.guardrail/audit.jsonl` (timestamp, commit, rule, result, reason, approver).

# 

# \## Quick start

# ```

# npm install -g @copado/agentia-cli

# pip install pyyaml

# python guardrail.py                       # run the check

# python guardrail.py approve RULE\_ID PATH  # human approval

# agentia cicd work test --local            # run through Agentia

# python run\_scenarios.py                   # run 10 scenarios

# ```

# 

# \## Results

# `python run\_scenarios.py` builds 10 temporary repos and checks each decision. \*\*10/10 scenarios produced the expected decision\*\* (see `scenario\_results.json`). These scenarios were designed with the rules, so this shows the engine behaves as specified, not that it catches every real-world risk.

# 

# \## Honest limitations

# \- Approval is not tamper-proof: an agent with shell access could run `approve` or edit `.guardrail/approvals.json`. Hardening idea: CODEOWNERS or PR review as the approval source.

# \- `agentia ... --skip-local-tests` bypasses local gates. The skill forbids it, but a second check (pre-push hook or CI) is needed for enforcement.

# \- The test check is a filename heuristic. It does not prove tests pass or cover the change.

# \- No Copado API key was available, so promotion to Copado is not shown live. Result upload prints a warning about the missing key; the local block still works.

# \- Alpha CLI: plugins cannot yet register MCP tools or wrap existing commands, so Guardrail uses the local gate and skill rather than a plugin.

# 

# \## Dependencies

# Python 3, PyYAML (MIT). Agentia CLI (Copado).

# 

# \## License

# MIT

