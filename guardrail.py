import fnmatch
import getpass
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


def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def write_audit(cfg, entry):
    os.makedirs(os.path.dirname(cfg["audit_log"]), exist_ok=True)
    with open(cfg["audit_log"], "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def now():
    return datetime.now(timezone.utc).isoformat()


def evaluate(cfg, files):
    findings = []
    paths = [p for _, p in files]
    sev = {r["id"]: r for r in cfg["rules"]}

    if "APEX_TEST_REQUIRED" in sev:
        has_test = any(is_apex_test(p) for p in paths)
        for p in paths:
            if is_apex_class(p) and not has_test:
                findings.append(("APEX_TEST_REQUIRED", "BLOCK",
                    f"{p} changed but no test class (*Test.cls) changed.", p))

    if "PERMISSION_APPROVAL" in sev:
        for p in paths:
            if p.endswith(".permissionset-meta.xml") or p.endswith(".profile-meta.xml"):
                findings.append(("PERMISSION_APPROVAL", "APPROVAL REQUIRED",
                    f"{p} changes permissions and needs human approval.", p))

    if "DESTRUCTIVE_CHANGE" in sev:
        for status, p in files:
            if status == "D" and (".object-meta.xml" in p or ".field-meta.xml" in p):
                findings.append(("DESTRUCTIVE_CHANGE", "BLOCK",
                    f"{p} deletes an object or field.", p))

    if "SENSITIVE_METADATA" in sev:
        for pat in sev["SENSITIVE_METADATA"].get("paths", []):
            for p in paths:
                if fnmatch.fnmatch(p, pat):
                    findings.append(("SENSITIVE_METADATA", "APPROVAL REQUIRED",
                        f"{p} is sensitive metadata and needs review.", p))
    return findings


def check(cfg):
    files = changed_files(cfg.get("base_branch", "main"))
    findings = evaluate(cfg, files)
    approvals = load_json(cfg["approvals_file"])
    commit = git("rev-parse", "--short", "HEAD") or "none"

    decision = "PASS"
    print("Agentia Guardrail")
    print("-" * 40)
    print(f"{len(files)} file(s) changed")

    for rule_id, result, reason, path in findings:
        key = f"{rule_id}:{path}"
        approved = result == "APPROVAL REQUIRED" and key in approvals
        shown = "APPROVED" if approved else result
        print(f"[{shown}] {rule_id}: {reason}")
        if approved:
            print(f"    approved by {approvals[key]['by']} at {approvals[key]['at']}")
        elif ORDER[result] > ORDER[decision]:
            decision = result
        write_audit(cfg, {
            "timestamp": now(), "commit": commit, "rule": rule_id,
            "result": shown, "reason": reason,
            "approvedBy": approvals[key]["by"] if approved else None,
        })

    write_audit(cfg, {
        "timestamp": now(), "commit": commit, "rule": "FINAL_DECISION",
        "result": decision, "reason": f"{len(findings)} finding(s) evaluated.",
        "approvedBy": None,
    })
    print("-" * 40)
    print(f"Decision: {decision}")
    return 0 if decision in ("PASS", "WARN") else 1


def approve(cfg, rule_id, path):
    approvals = load_json(cfg["approvals_file"])
    key = f"{rule_id}:{path}"
    who = os.environ.get("GUARDRAIL_APPROVER") or getpass.getuser()
    approvals[key] = {"by": who, "at": now()}
    os.makedirs(os.path.dirname(cfg["approvals_file"]), exist_ok=True)
    with open(cfg["approvals_file"], "w", encoding="utf-8") as f:
        json.dump(approvals, f, indent=2)
    write_audit(cfg, {
        "timestamp": now(), "commit": git("rev-parse", "--short", "HEAD") or "none",
        "rule": rule_id, "result": "APPROVAL GRANTED",
        "reason": f"Approval recorded for {path}.", "approvedBy": who,
    })
    print(f"Approval recorded for {key} by {who}")
    return 0


def main():
    with open("guardrail.yml", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if len(sys.argv) >= 4 and sys.argv[1] == "approve":
        sys.exit(approve(cfg, sys.argv[2], sys.argv[3]))
    sys.exit(check(cfg))


if __name__ == "__main__":
    main()