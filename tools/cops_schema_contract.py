#!/usr/bin/env python3
"""Check test-only SQL schema against startup SELECT queries in COPS source."""
from __future__ import annotations
import re
import sys
from pathlib import Path

TABLES = ("map", "itemtype", "npc", "monstertype", "generator", "magictype")
MAP_COLUMNS = ("id", "doc_id", "type", "weather", "portal_x",
               "portal_y", "reborn_map", "reborn_portal", "light")

def verify(upstream_source: str, schema: str) -> list[str]:
    errors = []
    for name in TABLES:
        pat = r"CREATE\s+TABLE\s+IF\s+NOT\s+EXISTS\s+`" + name + r"`"
        if not re.search(pat, schema, re.IGNORECASE):
            errors.append(f"missing schema table: {name}")
        if not re.search(r"FROM\s+`" + name + r"`", upstream_source):
            errors.append(f"upstream loader query not found: {name}")
    for col in MAP_COLUMNS:
        if not re.search(r"`" + col + r"`\s+(?:INT|BIGINT)", schema):
            errors.append(f"missing map column: {col}")
    return errors

def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: cops_schema_contract.py <database.cpp> <ci_loader_schema.sql>", file=sys.stderr)
        return 2
    source = Path(sys.argv[1]).read_text(encoding="utf-8")
    schema = Path(sys.argv[2]).read_text(encoding="utf-8")
    errors = verify(source, schema)
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1
    print("PASS: six COPS startup loader tables and nine map columns match upstream source.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
