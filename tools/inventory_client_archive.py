#!/usr/bin/env python3
"""Inventory public Internet Archive metadata without fetching/running installers."""
import json
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import sys
IDENTIFIERS=("conquer-online-v5039","conquer-patches-5000-5999")
def inventory(identifier):
    url="https://archive.org/metadata/"+identifier
    request=Request(url,headers={"User-Agent":"TQ-Classic-Conquer-preservation-inventory/1.0"})
    with urlopen(request,timeout=40) as response:
        record=json.load(response)
    entries=[]
    for f in record.get("files",[]):
        name=f.get("name","")
        if not name or name.startswith("__ia_thumb"):
            continue
        entries.append({"name":name,"size":f.get("size"),"sha1":f.get("sha1"),
                        "md5":f.get("md5"),"source":f.get("source"),"format":f.get("format")})
    return {"identifier":identifier,"url":"https://archive.org/details/"+identifier,
            "metadata_title":record.get("metadata",{}).get("title",""),
            "files":entries}
def main():
    out=Path("archive-client-inventory.json")
    results=[]
    failures=[]
    for ident in IDENTIFIERS:
        try: results.append(inventory(ident))
        except (URLError,HTTPError,TimeoutError,ValueError) as exc:
            failures.append(ident+": "+type(exc).__name__+": "+str(exc)[:140])
    out.write_text(json.dumps({"archive_records":results,"errors":failures,
       "target_patch":5065,"status":"inventory_only_not_downloaded_or_verified_client"},indent=2)+"\n")
    for result in results:
        print(result["identifier"]+": "+str(len(result["files"]))+" archive file entries")
        for f in result["files"]:
            if any(tok in f["name"].lower() for tok in ("5039","5065","5064","5040")):
                print("Candidate: "+f["name"]+" ("+str(f["size"])+" bytes)")
    for failure in failures: print("FAIL "+failure,file=sys.stderr)
    if failures: return 1
    if not all(x["files"] for x in results): return 1
    return 0
if __name__=="__main__":
    raise SystemExit(main())
