import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(ROOT, "guardrail.py")
CONFIG = os.path.join(ROOT, "guardrail.yml")

CLS = "force-app/main/default/classes/"
PS = "force-app/main/default/permissionsets/"
PR = "force-app/main/default/profiles/"
OBJ = "force-app/main/default/objects/Account/"
APP = "force-app/main/default/connectedApps/"

# (name, files to add, files to delete (must exist in base), expected decision)
SCENARIOS = [
    ("01 Apex class without test", {CLS + "A.cls": "x"}, [], "BLOCK"),
    ("02 Apex class with test", {CLS + "A.cls": "x", CLS + "ATest.cls": "x"}, [], "PASS"),
    ("03 Only test class changed", {CLS + "ATest.cls": "x"}, [], "PASS"),
    ("04 Permission set changed", {PS + "Admin.permissionset-meta.xml": "x"}, [], "APPROVAL REQUIRED"),
    ("05 Profile changed", {PR + "Admin.profile-meta.xml": "x"}, [], "APPROVAL REQUIRED"),
    ("06 Field deleted", {}, [OBJ + "fields/Old__c.field-meta.xml"], "BLOCK"),
    ("07 Object deleted", {}, [OBJ + "Account.object-meta.xml"], "BLOCK"),
    ("08 Connected app changed", {APP + "MyApp.connectedApp-meta.xml": "x"}, [], "APPROVAL REQUIRED"),
    ("09 README only", {"README.md": "x"}, [], "PASS"),
    ("10 Class + permission set, no test", {CLS + "A.cls": "x", PS + "Admin.permissionset-meta.xml": "x"}, [], "BLOCK"),
]


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def write(base, rel, content):
    full = os.path.join(base, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def decision_from(output):
    for line in output.splitlines():
        if line.startswith("Decision:"):
            return line.split(":", 1)[1].strip()
    return "ERROR"


def main():
    rows = []
    for name, adds, deletes, expected in SCENARIOS:
        tmp = tempfile.mkdtemp()
        try:
            run(["git", "init", "-b", "main"], tmp)
            run(["git", "config", "user.email", "t@t.t"], tmp)
            run(["git", "config", "user.name", "t"], tmp)
            shutil.copy(CONFIG, os.path.join(tmp, "guardrail.yml"))
            write(tmp, "base.txt", "base")
            for d in deletes:
                write(tmp, d, "x")
            run(["git", "add", "."], tmp)
            run(["git", "commit", "-m", "base"], tmp)
            run(["git", "checkout", "-b", "feature/US-0001"], tmp)
            for rel, content in adds.items():
                write(tmp, rel, content)
            for d in deletes:
                os.remove(os.path.join(tmp, d))
            run(["git", "add", "-A"], tmp)
            run(["git", "commit", "-m", "change"], tmp)
            r = run([sys.executable, ENGINE], tmp)
            got = decision_from(r.stdout)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        rows.append((name, expected, got, "OK" if got == expected else "MISMATCH"))

    print(f"{'Scenario':40} {'Expected':20} {'Actual':20} Result")
    print("-" * 90)
    for r in rows:
        print(f"{r[0]:40} {r[1]:20} {r[2]:20} {r[3]}")
    ok = sum(1 for r in rows if r[3] == "OK")
    print("-" * 90)
    print(f"{ok}/{len(rows)} scenarios matched the expected decision.")
    with open("scenario_results.json", "w", encoding="utf-8") as f:
        json.dump([dict(zip(["scenario", "expected", "actual", "result"], r)) for r in rows], f, indent=2)


if __name__ == "__main__":
    main()