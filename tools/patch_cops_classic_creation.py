#!/usr/bin/env python3
"""Repair real COPS first-level point allocation and enforce classic starter professions."""
from pathlib import Path
import sys

def replace(path, before, after):
    source=path.read_text(encoding="utf-8")
    count=source.count(before)
    if count != 1:
        raise RuntimeError("COPS source anchor mismatch in %s: %d"%(path,count))
    path.write_text(source.replace(before,after),encoding="utf-8")

def patch(root):
    root=Path(root)
    header=root/"src/Database/database.h"
    db=root/"src/Database/database.cpp"
    # Upstream mistakenly passes Soul by *value*, so starting mana cannot be set.
    replace(header,
        "uint16_t& aOutHealth, uint16_t aOutSoul,",
        "uint16_t& aOutHealth, uint16_t& aOutSoul,")
    replace(db,
        "uint16_t& aOutHealth, uint16_t aOutSoul,",
        "uint16_t& aOutHealth, uint16_t& aOutSoul,")
    replace(db,
        '''    ASSERT_ERR(aName != nullptr && aName[0] != '\0', ERROR_INVALID_PARAMETER);

    static const char cmd[] =''',
        '''    ASSERT_ERR(aName != nullptr && aName[0] != '\0', ERROR_INVALID_PARAMETER);

    // Classic character selection: Trojan, Warrior, Archer and Taoist.
    // Reject Ninja and all post-Ninja starter classes at the server boundary.
    if (!(aProfession == 10 || aProfession == 20 ||
          aProfession == 40 || aProfession == 100))
        return ERROR_INVALID_PARAMETER;

    static const char cmd[] =''')
    replace(db,
        '''    uint16_t force = 0, dexterity = 0, health = 0, soul = 0;
    getPointAllot(force, dexterity, health, soul, 1, aProfession);

    query.bindValue(":force", force);''',
        '''    uint16_t force = 0, dexterity = 0, health = 0, soul = 0;
    // Do not create a character from absent/failed point-allot SQL.
    const err_t allotErr = getPointAllot(
        force, dexterity, health, soul, 1, aProfession);
    if (allotErr != ERROR_SUCCESS)
        return allotErr;

    query.bindValue(":force", force);''')

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: patch_cops_classic_creation.py <upstream-cops>")
    patch(Path(sys.argv[1]))
    print("Patched starting profession, point-allot error handling and Soul output")
