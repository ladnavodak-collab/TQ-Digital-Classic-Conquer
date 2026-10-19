#!/usr/bin/env python3
"""Send one real encrypted MsgWalk after COPS account/DH/world login.

Synthetic map 1002 only; confirms the saved character's server-side position.
"""
import argparse
import socket
import struct
import subprocess
import time

from cops_account_success_probe import ACCOUNT_ID, PASSWORD, request_response
from cops_game_ticket_redemption_probe import (
    HOST, GAME_PORT, read_challenge, select_dh_response, make_dh_response,
    make_connect
)
from cops_game_dh_proof_probe import transform
from cops_existing_character_relogin import check_userinfo, MSG_USERINFO
from cops_world_entry_probe import (
    make_enter_map, receive_until, MSG_MAPINFO, MAP_ID
)

WALK_TYPE=1005
EAST=6
START=(8,8)
DESTINATION=(9,8)
CLIENT_SEAL=b"TQClient"

def make_walk(uid,direction=EAST,mode=0):
    if not 1<=uid<=0xFFFFFFFF or not 0<=direction<8 or mode not in (0,1):
        raise ValueError("invalid classic walk parameters")
    return struct.pack("<HHIBBh",12,WALK_TYPE,uid,direction,mode,0)+CLIENT_SEAL

def verify_walk_frame(frame,uid,direction=EAST):
    if len(frame)!=12:
        raise RuntimeError("invalid MsgWalk response length")
    length,typ,got_uid,got_dir,mode,pad=struct.unpack("<HHIBBh",frame)
    if (length,typ,got_uid,got_dir,mode,pad)!=(12,WALK_TYPE,uid,direction,0,0):
        raise RuntimeError("COPS did not acknowledge the authenticated walk")

def advance_cipher(clear_history,new_packet,shared,iv):
    """Continue COPS CFB64 stream without resetting its per-socket counter."""
    raw=transform(clear_history+new_packet,key=shared,iv=iv,encrypt=True)
    return raw[len(clear_history):]

def walk_synthetic_twin_city():
    with socket.create_connection((HOST,GAME_PORT),timeout=4) as sock:
        sock.settimeout(12)
        params=read_challenge(sock)
        public_b,shared=select_dh_response(params)
        if not 16<=len(shared)<=72:
            raise RuntimeError("unsupported DH session key length")
        size,kind,account,ticket,ip,port=request_response(PASSWORD)
        if (size,kind,account,port)!=(32,1055,ACCOUNT_ID,GAME_PORT) or ticket<10000:
            raise RuntimeError("account ticket issuance failed")
        if ip.split(bytes([0]),1)[0]!=HOST.encode("ascii"):
            raise RuntimeError("nonloopback game redirect")
        clear_history=make_connect(account,ticket)
        dh_wire=transform(make_dh_response(public_b),encrypt=True)
        game_wire=transform(clear_history,key=shared,iv=params["decrypt_iv"],encrypt=True)
        sock.sendall(dh_wire+game_wire)
        received,frames=receive_until(
            sock,shared,params["encrypt_iv"],b"",
            lambda entries:any(typ==MSG_USERINFO for typ,_ in entries)
        )
        character=next(check_userinfo(frame) for typ,frame in frames if typ==MSG_USERINFO)

        enter=make_enter_map(character)
        sock.sendall(advance_cipher(clear_history,enter,shared,params["decrypt_iv"]))
        clear_history+=enter
        received,frames=receive_until(
            sock,shared,params["encrypt_iv"],received,
            lambda entries:any(typ==MSG_MAPINFO for typ,_ in entries)
        )

        walk=make_walk(character)
        sock.sendall(advance_cipher(clear_history,walk,shared,params["decrypt_iv"]))
        received,frames=receive_until(
            sock,shared,params["encrypt_iv"],received,
            lambda entries:any(typ==WALK_TYPE for typ,_ in entries)
        )
        echoes=[frame for typ,frame in frames if typ==WALK_TYPE]
        if len(echoes)!=1:
            raise RuntimeError("missing or duplicate COPS MsgWalk acknowledgement")
        verify_walk_frame(echoes[0],character)
    print("PASS: real COPS accepted encrypted authenticated MsgWalk east on map 1002",flush=True)
    print("PASS: player received validated MsgWalk echo after server movement processing",flush=True)
    print("Client disconnected; database save is checked independently after cleanup.",flush=True)

def check_database(cli):
    statement=("SELECT record_map,record_x,record_y FROM user "
               "WHERE account_id=%d"%ACCOUNT_ID)
    deadline=time.monotonic()+9
    last=""
    while time.monotonic()<deadline:
        result=subprocess.run(cli+["--batch","--skip-column-names","--execute",statement],
                              text=True,capture_output=True)
        if result.returncode:
            raise RuntimeError("character position SQL check failed: "+result.stderr[-250:])
        last=result.stdout.strip()
        if last=="1002\t9\t8":
            print("PASS: real COPS persisted first authenticated character walk to map 1002 tile (9,8)",flush=True)
            return
        time.sleep(.2)
    raise RuntimeError("COPS did not save expected post-walk position, last="+repr(last))

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("walk","check-db"))
    parser.add_argument("mysql_cli",nargs="*")
    args=parser.parse_args()
    if args.action=="walk":
        walk_synthetic_twin_city()
    else:
        if not args.mysql_cli:parser.error("check-db needs MariaDB CLI command")
        check_database(args.mysql_cli)
