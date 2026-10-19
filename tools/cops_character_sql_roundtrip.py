#!/usr/bin/env python3
"""Disposable MariaDB test of COPS character create/save/reload SQL contract."""
import argparse
import subprocess

COLUMNS = (
    "account_id","id","name","mate","lookface","hair","money","money_saved",
    "cps","level","exp","force","dexterity","health","soul","add_points",
    "life","mana","profession","pk","virtue","nobility","metempsychosis",
    "syndicate_id","record_map","record_x","record_y","last_login"
)

def sql(mysql, query):
    p=subprocess.run(mysql+["--batch","--skip-column-names","--execute",query],
                     text=True,capture_output=True,check=False)
    if p.returncode:
        raise RuntimeError("MariaDB SQL operation failed (exit %s): %s"%(p.returncode,p.stderr[-600:]))
    return p.stdout.strip()

def run(mysql):
    # Verify actual SELECT * shape, not hand-written projection order.
    names=sql(mysql, "SELECT COLUMN_NAME FROM information_schema.columns "
                   "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='user' ORDER BY ORDINAL_POSITION").splitlines()
    assert names == list(COLUMNS), "COPS SQLDATA positional mapping differs from schema"

    sql(mysql,"INSERT INTO account(id,name,password) VALUES(77,'fixture-only','not-a-real-password')")
    sql(mysql,"INSERT INTO user(account_id,name,lookface,profession,force,dexterity,health,soul,life,mana) "
              "VALUES(77,'BootTester',1003,10,4,5,6,7,180,35)")
    row=sql(mysql,"SELECT account_id,name,record_map,record_x,record_y,cps,metempsychosis "
                  "FROM user WHERE account_id=77")
    assert row=="77\tBootTester\t1002\t8\t8\t0\t0", ("create mismatch",row)

    # Match COPS Database::savePlayer changed fields (UPDATE WHERE account_id).
    sql(mysql, "UPDATE user SET mate='',lookface=1003,hair=1,money=125,cps=0,"
               "level=2,exp=42,force=5,dexterity=6,health=7,soul=8,add_points=2,"
               "life=205,mana=40,pk=0,virtue=10,metempsychosis=1,"
               "record_map=1002,record_x=9,record_y=10 WHERE account_id=77")
    persisted=sql(mysql, "SELECT name,level,money,exp,force,dexterity,health,soul,life,mana,"
                        "metempsychosis,record_map,record_x,record_y "
                        "FROM user WHERE account_id=77")
    expected="BootTester\t2\t125\t42\t5\t6\t7\t8\t205\t40\t1\t1002\t9\t10"
    assert persisted==expected, ("save/reload mismatch",persisted)
    result=subprocess.run(mysql+["--execute","UPDATE user SET cps=10 WHERE account_id=77"],
                          text=True,capture_output=True)
    assert result.returncode != 0, "Classic no-CP constraint was bypassed"
    result=subprocess.run(mysql+["--execute","UPDATE user SET metempsychosis=2 WHERE account_id=77"],
                          text=True,capture_output=True)
    assert result.returncode != 0, "Classic one-rebirth constraint was bypassed"
    print("PASS: COPS ordinal SQL layout and synthetic character create/save/reload")
    print("PASS: CI-only no-CP and single-rebirth database constraints")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("mysql_cli",nargs="+",help="e.g. mariadb tq_ci")
    a=ap.parse_args()
    run(a.mysql_cli)
