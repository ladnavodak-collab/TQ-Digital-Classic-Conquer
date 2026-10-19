#!/usr/bin/env python3
"""Generate a small ORIGINAL synthetic COPS DMap for isolated loader CI only.
No 5065 client assets; not a visual or playable Twin City.
"""
import argparse
import struct
from pathlib import Path

def make_map(width=16, height=16):
    if not (2 <= width <= 128 and 2 <= height <= 128):
        raise ValueError("Synthetic diagnostic map dimensions must be 2..128")
    header=struct.pack("<II",1003,0)+bytes(260)+struct.pack("<II",width,height)
    rows=bytearray()
    for y in range(height):
        checksum=0
        for x in range(width):
            mask,terrain,altitude=0,0,0  # entirely walkable flat test grid
            rows += struct.pack("<HHh",mask,terrain,altitude)
            checksum += mask*(terrain+y+1)+(altitude+2)*(x+1+terrain)
        rows += struct.pack("<I",checksum & 0xffffffff)
    # No passages or scene layers: diagnostic map has no client graphics.
    return header+rows+struct.pack("<ii",0,0)

def write_fixture(root:Path):
    root.mkdir(parents=True,exist_ok=True)
    (root/"tq-ci-1002.dmap").write_bytes(make_map())
    (root/"GameMap.ini").write_text("[Map1002]\nFile=tq-ci-1002.dmap\n",encoding="utf-8")
    return root

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("output_directory",type=Path)
    args=parser.parse_args()
    root=write_fixture(args.output_directory)
    print("Generated synthetic DMap and GameMap.ini:",root)
    print("NOT a 5065 client map and NOT playable.")
if __name__=="__main__":
    main()
