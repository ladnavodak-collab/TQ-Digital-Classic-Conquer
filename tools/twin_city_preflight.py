#!/usr/bin/env python3
"""Twin City layout and optional local COPS GameMap.ini preflight. No asset copies."""
import argparse
import configparser
import json
from pathlib import Path
import struct

def validate(spec):
    issues = []
    if spec.get("map_id") != 1002: issues.append("Twin City map_id must be 1002")
    districts = {x["id"] for x in spec.get("districts", [])}
    ids = [x["id"] for x in spec.get("npcs", [])]
    if len(ids) != len(set(ids)): issues.append("duplicate NPC IDs")
    if len(districts) != len(spec.get("districts", [])): issues.append("duplicate district IDs")
    for npc in spec.get("npcs", []):
        if npc["district"] not in districts: issues.append("unknown district for NPC "+npc["id"])
        coords = npc.get("coordinates")
        if coords is not None and (not isinstance(coords, list) or len(coords) != 2 or
           any(not isinstance(v,int) or isinstance(v,bool) or v < 0 for v in coords)):
            issues.append("invalid coordinates for NPC "+npc["id"])
    declared = {x["id"] for x in spec.get("npcs", [])}
    for district in spec.get("districts", []):
        for npc_id in district["npc_ids"]:
            if npc_id not in declared: issues.append("unknown NPC slot "+npc_id)
            elif next(x for x in spec["npcs"] if x["id"] == npc_id)["district"] != district["id"]:
                issues.append("NPC district mismatch: "+npc_id)
    rules = spec.get("rules",{})
    if rules.get("conquer_points") is not False or rules.get("shopping_mall") is not False:
        issues.append("CP and mall must be disabled")
    if rules.get("max_rebirths") != 1 or rules.get("currency") != "silver":
        issues.append("classic rebirth/economy invariant failed")
    if any(q["reward_currency"] != "silver" for q in spec.get("daily_quests", [])):
        issues.append("unsupported quest currency")
    if spec.get("releases",{}).get("playable") is True:
        issues.append("cannot mark playable without integration evidence")
    return issues

def map_preflight(ini_path, asset_root):
    issues=[]
    config=configparser.ConfigParser(interpolation=None, strict=True)
    config.optionxform = str
    try: config.read(ini_path, encoding="utf-8")
    except (OSError, configparser.Error) as err: return ["GameMap.ini unreadable: "+str(err)]
    if not config.has_section("Map1002"): return ["GameMap.ini missing [Map1002]"]
    map_file=config.get("Map1002","File",fallback="").strip().replace("\\","/")
    if not map_file or map_file == "N/A": return ["Map1002 File entry missing"]
    root=asset_root.resolve()
    candidate=(root / map_file).resolve()
    if not candidate.is_relative_to(root): return ["Map1002 path escapes asset root"]
    if not candidate.is_file(): return ["Map1002 DMap file is missing"]
    try:
        with candidate.open("rb") as fp:
            header=fp.read(4+4+260+4+4)
        if len(header)!=276: return ["Map1002 DMap header too short"]
        width,height=struct.unpack_from("<II",header,268)
        if not (1 <= width < 65535 and 1 <= height < 65535): issues.append("invalid DMap dimensions")
    except OSError as err: issues.append("cannot read DMap: "+str(err))
    return issues

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("manifest",type=Path)
    parser.add_argument("--gamemap-ini",type=Path)
    parser.add_argument("--asset-root",type=Path)
    args=parser.parse_args()
    spec=json.loads(args.manifest.read_text(encoding="utf-8"))
    issues=validate(spec)
    if bool(args.gamemap_ini) != bool(args.asset_root):
        issues.append("--gamemap-ini and --asset-root must be supplied together")
    elif args.gamemap_ini:
        issues+=map_preflight(args.gamemap_ini,args.asset_root)
    for issue in issues: print("FAIL:",issue)
    if issues: return 1
    print("PASS: Twin City content contract" + (" and local DMap header" if args.asset_root else " (no map assets supplied)"))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
