import fnmatch
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import yaml

ORDER = {"PASS": 0, "WARN": 1, "APPROVAL REQUIRED": 2, "BLOCK": 3}


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.strip()


def changed_files(base):
    """Return list of (status, path) for changes vs base, plus uncommitted."""
    out = git("diff", "--name-status", f"{base}...HEAD")
    out2 = git("diff", "--name-status", "HEAD")
    rows = []
    for line in (out + "\n" + out2).splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            rows.append((parts[0][0], parts[-1].replace("\\", "/")))
    return sorted(set(rows))


def is_apex_class(p):
    return p.endswith(".cls") and not p.endswith("Test.cls")


def is_apex_test(p):
    return p.endswith("Test.cls")


def load_approvals(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def evaluate(cfg, files):
    findings = []
    paths = [p for _, p in files]
    sev = {r["id"]: r for r in cfg["rules"]}

    if "APEX_TEST_REQUIRED" in sev:
        has_test = any(is_apex_test(p) for p in paths)
        for p in paths:
            if is_apex_class(p) and not has_test:
                findings.append((
                    "APEX_TEST_REQUIRED",
                    "BLOCK" if sev["APEX_TEST_REQUIRED"]["severity"] == "block" else "WARN",
                    f"{p} changed but no test class (*Test.cls) changed.",
                    p,
                ))

    if "PERMISSION_APPROVAL" in sev:
        for p in paths:
            if p.endswith(".permissionset-meta.xml") or p.endswith(".profile-meta.xml"):
                findings.append((
                    "PERMISSION_APPROVAL", "APPROVAL REQUIRED",
                    f"{p} changes permissions and needs human approval.", p,
                ))

    if "DESTRUCTIVE_CHANGE" in sev:
        for status, p in files:
            if status == "D" and (".object-meta.xml" in p or ".field-meta.xml" in p):
                findings.append((
                    "DESTRUCTIVE_CHANGE", "BLOCK",
                    f"{p} deletes an object or field.", p,
                ))

    if "SENSITIVE_METADATA" in sev:
        for pat in sev["SENSITIVE_METADATA"].get("paths", []):
            for p in paths:
                if fnmatch.fnmatch(p, pat):
                    findings.append((
                        "SENSITIVE_METADATA", "APPROVAL REQUIRED",
                        f"{p} is sensitive metadata and needs review.", p,
                    ))
    return findings


def main():
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "guardrail.yml"
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    files = changed_files(cfg.get("base_branch", "main"))
    findings = evaluate(cfg, files)
    approvals = load_approvals(cfg["approvals_file"])
    commit = git("rev-parse", "--short", "HEAD") or "none"

    decision = "PASS"
    print("Agentia Guardrail")
    print("-" * 40)
    print(f"{len(files)} file(s) changed")

    for rule_id, result, reason, path in findings:
        approved = result == "APPROVAL REQUIRED" and approvals.get(f"{rule_id}:{path}")
        shown = "APPROVED" if approved else result
        print(f"[{shown}] {rule_id}: {reason}")
        if not approved and ORDER[result] > ORDER[decision]:
            decision = result
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "commit": commit,
            "rule": rule_id,
            "result": shown,
            "reason": reason,
            "approvedBy": approvals.get(f"{rule_id}:{path}") if approved else None,
        }
        os.makedirs(os.path.dirname(cfg["audit_log"]), exist_ok=True)
        with open(cfg["audit_log"], "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    print("-" * 40)
    print(f"Decision: {decision}")
    sys.exit(0 if decision in ("PASS", "WARN") else 1)


if __name__ == "__main__":
    main()