#!/usr/bin/env python3
"""Walk one step in the synthetic COPS map and verify real save-on-disconnect.

Original 16x16 test-only map and disposable MariaDB; no retail 5065 client.
"""
import argparse
import socket
import struct
import subprocess
import time

from cops_account_success_probe import ACCOUNT_ID,PASSWORD,request_response
from cops_game_ticket_redemption_probe import (
    HOST,GAME_PORT,read_challenge,select_dh_response,make_dh_response,make_connect
)
from cops_game_dh_proof_probe import transform
from cops_existing_character_relogin import check_userinfo,MSG_USERINFO
from cops_world_entry_probe import receive_until,make_enter_map,decode_enter_map,MSG_MAPINFO

SEAL=b"TQClient"
MSG_WALK=1005
EAST=6
# Original COPS Entity::isPlayer accepted range; not every uint32 is a player.
PLAYER_UID_MIN=1000000
PLAYER_UID_MAX=1999999999

def walk_packet(uid,direction=EAST,mode=0):
    if not PLAYER_UID_MIN<=uid<=PLAYER_UID_MAX:
        raise ValueError("MsgWalk requires a UID from the real COPS player range")
    if direction not in range(8) or mode not in (0,1):
        raise ValueError("invalid classic walk direction or mode")
    return struct.pack("<HHIBBh",12,MSG_WALK,uid,direction,mode,0)+SEAL

def verify_walk_echo(frame,uid):
    if len(frame)!=12:raise RuntimeError("incorrect walk acknowledgement length")
    values=struct.unpack("<HHIBBh",frame)
    if values!=(12,MSG_WALK,uid,EAST,0,0):
        raise RuntimeError("unexpected real COPS walk response")

def move_one_step():
    with socket.create_connection((HOST,GAME_PORT),timeout=4) as sock:
        sock.settimeout(12)
        params=read_challenge(sock)
        public_b,shared=select_dh_response(params)
        if not 16<=len(shared)<=72:raise RuntimeError("unsupported DH key size")
        size,kind,account,ticket,ip,port=request_response(PASSWORD)
        if (size,kind,account,port)!=(32,1055,ACCOUNT_ID,GAME_PORT) or ticket<10000:
            raise RuntimeError("account login did not authorize game transfer")
        if ip.split(b"\0",1)[0]!=HOST.encode("ascii"):
            raise RuntimeError("nonlocal redirect")
        clear_connect=make_connect(account,ticket)
        sock.sendall(transform(make_dh_response(public_b),encrypt=True)+
                     transform(clear_connect,key=shared,iv=params["decrypt_iv"],encrypt=True))
        wire,frames=receive_until(sock,shared,params["encrypt_iv"],b"",
            lambda f:any(typ==MSG_USERINFO for typ,_ in f))
        uid=next(check_userinfo(frame) for typ,frame in frames if typ==MSG_USERINFO)
        enter=make_enter_map(uid)
        clear_sent=clear_connect+enter
        all_encrypted=transform(clear_sent,key=shared,iv=params["decrypt_iv"],encrypt=True)
        sock.sendall(all_encrypted[len(clear_connect):])
        wire,frames=receive_until(sock,shared,params["encrypt_iv"],wire,
            lambda f:any(typ==MSG_MAPINFO for typ,_ in f))
        entered=[frame for typ,frame in frames if typ==1010 and len(frame)==24
                 and struct.unpack_from("<H",frame,22)[0]==74]
        if len(entered)!=1:raise RuntimeError("COPS did not confirm map entry")
        decode_enter_map(entered[0],uid)
        walk=walk_packet(uid)
        encrypted=transform(clear_sent+walk,key=shared,
                            iv=params["decrypt_iv"],encrypt=True)
        sock.sendall(encrypted[len(clear_sent):])
        wire,frames=receive_until(sock,shared,params["encrypt_iv"],wire,
            lambda f:any(typ==MSG_WALK for typ,_ in f))
        ack=[frame for typ,frame in frames if typ==MSG_WALK]
        if len(ack)!=1:raise RuntimeError("COPS did not acknowledge exactly one walk")
        verify_walk_echo(ack[0],uid)
    # Server::disconnectionHandler invokes Client::save when socket closes.
    print("PASS: actual COPS accepted authenticated eastward walk on synthetic map 1002",flush=True)
    print("PASS: COPS returned encrypted walk acknowledgment; disconnected to save",flush=True)

def verify_saved_coordinates(cli):
    query=("SELECT `record_map`,`record_x`,`record_y`,`cps`,`metempsychosis` "
           "FROM `user` WHERE `account_id`=78")
    deadline=time.monotonic()+8
    while True:
        result=subprocess.run(cli+["--batch","--skip-column-names","--execute",query],
                              text=True,capture_output=True)
        if result.returncode:raise RuntimeError("SQL verification failed: "+result.stderr[-250:])
        if result.stdout.strip()=="1002\t9\t8\t0\t0":
            print("PASS: real COPS persisted walked coordinates (1002,9,8) in MariaDB",flush=True)
            print("PASS: zero CP and rebirth maintained in save",flush=True)
            return
        if time.monotonic()>=deadline:
            raise RuntimeError("COPS did not persist east step: "+repr(result.stdout.strip()))
        time.sleep(0.15)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=("move","check-db"))
    p.add_argument("mysql",nargs="*")
    a=p.parse_args()
    if a.action=="move":move_one_step()
    else:
        if not a.mysql:p.error("check-db requires disposable MariaDB CLI")
        verify_saved_coordinates(a.mysql)
