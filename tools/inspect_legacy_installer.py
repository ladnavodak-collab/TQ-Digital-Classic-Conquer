#!/usr/bin/env python3
"""Inspect untrusted PE installers without executing them or extracting payloads."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess

def inspect(path, sevenzip="7z"):
    path=Path(path)
    size=path.stat().st_size
    sha=hashlib.sha256()
    with path.open("rb") as stream:
        prefix=stream.read(min(size,1024*1024))
        sha.update(prefix)
        for chunk in iter(lambda: stream.read(1024*1024),b""):
            sha.update(chunk)
    result={"name":path.name,"size_bytes":size,"sha256":sha.hexdigest(),
            "pe_header_valid":False,"pe_machine":None,"sfx_markers":[],"listing_status":"not_attempted"}
    if len(prefix)>=64 and prefix[:2]==b"MZ":
        loc=struct.unpack_from("<I",prefix,0x3c)[0]
        if loc+6 <= len(prefix) and prefix[loc:loc+4]==b"PE\0\0":
            result["pe_header_valid"]=True
            result["pe_machine"]=hex(struct.unpack_from("<H",prefix,loc+4)[0])
    for signature, name in ((b"NullsoftInst", "nsis"),(b"Inno Setup","inno_setup"),
                            (b"7z\xbc\xaf\x27\x1c","7zip"),(b"Rar!\x1a\x07","rar")):
        if signature in prefix: result["sfx_markers"].append(name)
    try:
        proc=subprocess.run([sevenzip,"l","-slt",str(path.resolve())],capture_output=True,
                            text=True,errors="replace",timeout=25,check=False)
        result["listing_status"]="success" if proc.returncode==0 else "unsupported_or_corrupt"
        # Deliberately avoid recording internal payload filenames or untrusted verbose output.
        result["listing_entry_count"]=sum(line.startswith("Path = ") for line in proc.stdout.splitlines())
    except FileNotFoundError:
        result["listing_status"]="7zip_not_installed"
    except subprocess.TimeoutExpired:
        result["listing_status"]="timeout"
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("file",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    data=inspect(args.file)
    serialized=json.dumps(data,indent=2)+"\n"
    if args.output: args.output.write_text(serialized,encoding="utf-8")
    print(serialized,end="")
    return 0 if data["pe_header_valid"] else 1

if __name__=="__main__":
    raise SystemExit(main())
