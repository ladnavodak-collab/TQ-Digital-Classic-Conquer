#!/usr/bin/env python3
"""Harden COPS Player::SQLDATA_* positional loading and classic character rules."""
from pathlib import Path
import sys

ORDERED_COLUMNS = (
    "account_id","id","name","mate","lookface","hair","money","money_saved",
    "cps","level","exp","force","dexterity","health","soul","add_points",
    "life","mana","profession","pk","virtue","nobility","metempsychosis",
    "syndicate_id","record_map","record_x","record_y","last_login"
)
def replace_one(p,old,new):
    text=p.read_text(encoding="utf-8")
    if text.count(old)!=1:
        raise RuntimeError("COPS database upstream anchor mismatch: %s (%d)"%(p,text.count(old)))
    p.write_text(text.replace(old,new),encoding="utf-8")
def patch(root):
    p=Path(root)/"src/Database/database.cpp"
    columns=", ".join("`%s`"%c for c in ORDERED_COLUMNS)
    replace_one(p,
        '''    static const char cmd[] =
            "SELECT * FROM `user` WHERE `account_id` = :account_id";''',
        '''    // Player::SQLDATA_* relies on a fixed 28-column ordinal layout.
    // Never use SELECT * here; schema reordering must not corrupt characters.
    static const char cmd[] =
            "SELECT '''+columns+''' FROM `user` WHERE `account_id` = :account_id";''')
    replace_one(p,
        '''            uint32_t uid = (uint32_t)query.value(Player::SQLDATA_ID).toUInt();
            Player* player = new Player(aClient, uid);''',
        '''            // Reject invalid classic rows before allocating a Player.
            const uint32_t uid = query.value(Player::SQLDATA_ID).toUInt();
            const uint32_t cps = query.value(Player::SQLDATA_CONQUER_POINTS).toUInt();
            const uint32_t rebirths = query.value(Player::SQLDATA_METEMPSYCHOSIS).toUInt();
            const uint32_t mapId = query.value(Player::SQLDATA_RECORD_MAP).toUInt();
            if (uid == 0 || cps != 0 || rebirths > 1 || mapId == 0)
            {
                LOG(ERROR, "Rejected invalid classic character row (id=%u).", uid);
                return ERROR_INVALID_PARAMETER;
            }
            Player* player = new Player(aClient, uid);''')
    replace_one(p,
        '''    query.bindValue(":cps", player.getCPs());''',
        '''    // Classic-only server: never persist premium currency.
    query.bindValue(":cps", 0);''')
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: patch_cops_character_load.py <upstream-cops-dir>")
    patch(Path(sys.argv[1]))
    print("Hardened COPS character SELECT projection and zero-CP save")
