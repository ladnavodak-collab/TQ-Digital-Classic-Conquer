#!/usr/bin/env python3
"""Defensive, offline COPS-v7 source audit. Does not read or print secret values."""
from __future__ import annotations
import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

@dataclass
class Finding:
    rule: str
    severity: str
    file: str
    line: int
    description: str

RULES = [
    ("COPS001", "high", re.compile(r"^\s*SQL_USER\s*=\s*root\s*$", re.I),
     "Example config uses database superuser; configure an application-specific SQL account."),
    ("COPS002", "critical", re.compile(r"^\s*SQL_PWD\s*=\s*(?:root|admin|password|123456)\s*$", re.I),
     "Example config uses a well-known database password; never deploy it."),
    ("COPS003", "critical", re.compile(r"password\.compare\s*\(\s*aPassword\s*\)\s*==\s*0"),
     "Direct password comparison suggests plaintext credential storage; replace with a tested password KDF."),
    ("COPS004", "high", re.compile(r"LOG\s*\(\s*DBG\s*,[^\n]*getSqlCommand\s*\("),
     "Logging SQL with bound values risks exposing passwords and other private data."),
]

def scan(root: Path) -> list[Finding]:
    findings = []
    for relative in ("data/settings.cfg", "src/Database/database.cpp"):
        path = root / relative
        if not path.is_file():
            findings.append(Finding("COPS000", "info", relative, 0, "File unavailable; scan incomplete."))
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for code, severity, regex, description in RULES:
                if regex.search(line):
                    findings.append(Finding(code, severity, relative, number, description))
    return findings

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Path to locally obtained upstream COPS v7 checkout")
    parser.add_argument("--output", type=Path, help="Optional JSON report output")
    args = parser.parse_args()
    if not args.source.is_dir():
        parser.error("The provided source directory does not exist.")
    findings = scan(args.source)
    report = {"source": str(args.source), "findings": [asdict(item) for item in findings],
              "critical_or_high": sum(f.severity in ("critical", "high") for f in findings)}
    encoded = json.dumps(report, indent=2)
    if args.output:
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 1 if report["critical_or_high"] else 0

if __name__ == "__main__":
    raise SystemExit(main())
