#!/usr/bin/env python3
"""Summarize a 7-Zip listing of a legacy Conquer client. Never unpack/run it."""
import argparse
import json
import re
import subprocess
from pathlib import Path

def inspect_archive(path: Path):
    run = subprocess.run(["7z", "l", "-slt", str(path.resolve())],
                         capture_output=True, text=True, errors="replace",
                         timeout=180, check=False)
    if run.returncode:
        return {"status": "not_listable", "return_code": run.returncode,
                "map_candidates": [], "entries": 0}
    names = [m.group(1) for m in re.finditer(r"^Path = (.+)$", run.stdout, re.MULTILINE)]
    # First Path describes the archive, not an archived payload entry.
    if names and names[0] in (str(path), str(path.resolve())):
        names = names[1:]
    matches = [n for n in names if re.search(
        r"(?:\.dmap$|gamemap\.(?:ini|dat)$|(?:^|[\\/])map(?:[\\/]|$)|(?:^|[\\/])scene(?:[\\/]|$)|minimap)",
        n, re.IGNORECASE)]
    return {"status": "listed", "entries": len(names),
            "map_candidates": matches[:150],
            "candidate_count": len(matches)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("installer",type=Path)
    p.add_argument("--output",type=Path,default=Path("client-5039-map-inventory.json"))
    args=p.parse_args()
    result=inspect_archive(args.installer)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"entries":result["entries"],
                       "map_candidates":result.get("candidate_count",0)},indent=2))
    return 0 if result["status"] == "listed" else 1
if __name__=="__main__": raise SystemExit(main())
