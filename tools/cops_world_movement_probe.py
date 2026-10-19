#!/usr/bin/env python3
"""Exercise a real persisted COPS player's walking movement in synthetic map 1002.

Complete account login/DH/token, enter the map, send MsgWalk and request a fresh
ACTION_ENTER_MAP acknowledgement to verify server-authoritative coordinates.
Only 127.0.0.1, no proprietary client or retail world assets.
"""
import socket
import struct

from cops_account_success_probe import ACCOUNT_ID,PASSWORD,request_response
from cops_game_ticket_redemption_probe import (
    HOST,GAME_PORT,read_challenge,select_dh_response,make_dh_response,make_connect
)
from cops_game_dh_proof_probe import transform
from cops_existing_character_relogin import check_userinfo,MSG_USERINFO
from cops_world_entry_probe import (
    SEAL,MSG_ACTION,MSG_MAPINFO,ACTION_ENTER_MAP,MAP_ID,
    make_enter_map,decode_enter_map,receive_until,decode_mapinfo
)

MSG_WALK=1005
START_X,START_Y=8,8
NEXT_X,NEXT_Y=9,8
DIRECTION_EAST=6

def make_walk(uid,direction=DIRECTION_EAST):
    if not 1<=uid<=0xffffffff or not 0<=direction<=7:
        raise ValueError("invalid character walk identity or direction")
    # MsgWalk::MsgInfo: Length, Type, UniqId, Direction, Mode, Padding1.
    return struct.pack("<HHIBBh",12,MSG_WALK,uid,direction,0,0)+SEAL

def decode_walk_ack(packet,uid):
    if len(packet)!=12:
        raise ValueError("unexpected MsgWalk byte count")
    length,kind,returned,direction,mode,padding=struct.unpack("<HHIBBh",packet)
    if (length,kind,returned,direction,mode,padding)!=(12,MSG_WALK,uid,DIRECTION_EAST,0,0):
        raise ValueError("incorrect MsgWalk echo")
    return True

def enter_ack(frames,uid,x,y):
    for typ,packet in frames:
        if typ!=MSG_ACTION or len(packet)!=24:
            continue
        if struct.unpack_from("<H",packet,22)[0]!=ACTION_ENTER_MAP:
            continue
        if struct.unpack_from("<I",packet,8)[0]!=uid:
            continue
        if struct.unpack_from("<HH",packet,16)==(x,y):
            return True
    return False

def verify_movement():
    with socket.create_connection((HOST,GAME_PORT),timeout=4) as sock:
        sock.settimeout(12)
        params=read_challenge(sock)
        public,shared=select_dh_response(params)
        if not 16<=len(shared)<=72:
            raise RuntimeError("invalid game session key")
        size,kind,account,ticket,ip,port=request_response(PASSWORD)
        if (size,kind,account,port)!=(32,1055,ACCOUNT_ID,GAME_PORT) or ticket<10000:
            raise RuntimeError("account login failed before movement")
        if ip.split(bytes([0]),1)[0]!=HOST.encode("ascii"):
            raise RuntimeError("non-local game redirect")
        connect=make_connect(account,ticket)
        dh=transform(make_dh_response(public),encrypt=True)
        encrypted_connect=transform(connect,key=shared,iv=params["decrypt_iv"],encrypt=True)
        sock.sendall(dh+encrypted_connect)
        raw,frames=receive_until(
            sock,shared,params["encrypt_iv"],b"",
            lambda fs:any(t==MSG_USERINFO for t,_ in fs))
        uid=next(check_userinfo(payload) for t,payload in frames if t==MSG_USERINFO)

        enter=make_enter_map(uid)
        sent=connect+enter
        sock.sendall(transform(sent,key=shared,iv=params["decrypt_iv"],encrypt=True)[len(connect):])
        raw,frames=receive_until(
            sock,shared,params["encrypt_iv"],raw,
            lambda fs:any(t==MSG_MAPINFO for t,_ in fs) and enter_ack(fs,uid,START_X,START_Y))
        if not any(t==MSG_MAPINFO and decode_mapinfo(payload)>=0 for t,payload in frames if t==MSG_MAPINFO):
            raise RuntimeError("synthetic map entry metadata missing")

        walk=make_walk(uid)
        sock.sendall(transform(sent+walk,key=shared,iv=params["decrypt_iv"],encrypt=True)[len(sent):])
        raw,frames=receive_until(
            sock,shared,params["encrypt_iv"],raw,
            lambda fs:any(t==MSG_WALK for t,_ in fs))
        echoes=[payload for t,payload in frames if t==MSG_WALK]
        if len(echoes)!=1:
            raise RuntimeError("wrong number of walking acknowledgement frames")
        decode_walk_ack(echoes[0],uid)

        # The echo precedes the actual player.move() call in COPS. Ask the
        # server for its authoritative coordinates; don't trust only the echo.
        sock.sendall(transform(sent+walk+enter,key=shared,iv=params["decrypt_iv"],encrypt=True)[len(sent)+len(walk):])
        raw,frames=receive_until(
            sock,shared,params["encrypt_iv"],raw,
            lambda fs:enter_ack(fs,uid,NEXT_X,NEXT_Y))
        if not enter_ack(frames,uid,NEXT_X,NEXT_Y):
            raise RuntimeError("COPS did not move player on test-only flat map")
        print("PASS: real COPS accepted authenticated MsgWalk east on synthetic map 1002",flush=True)
        print("PASS: authoritative ACTION_ENTER_MAP confirms movement (8,8) -> (9,8)",flush=True)
        print("Original protocol-only CI fixture; no actual 5065 client or graphical world is tested.",flush=True)

if __name__=="__main__":
    verify_movement()
