#!/usr/bin/env python3
"""Exercise server-side map entry with a saved COPS character on synthetic map 1002.

Fresh authenticated account -> game DH/token -> saved MsgUserInfo ->
encrypted MsgAction ACTION_ENTER_MAP -> MsgMapInfo. Loopback-only CI.
"""
import argparse
import socket
import struct

from cops_account_success_probe import ACCOUNT_ID, PASSWORD, request_response
from cops_game_ticket_redemption_probe import (
    HOST,GAME_PORT,read_challenge,select_dh_response,make_dh_response,make_connect
)
from cops_game_dh_proof_probe import transform
from cops_existing_character_relogin import parse_frames,check_userinfo,MSG_USERINFO

SEAL=b"TQClient"
MSG_ACTION=1010
MSG_MAPINFO=1110
ACTION_ENTER_MAP=74
ACTION_MAP_ARGB=104
MAP_ID=1002
MAX_WIRE=32768

def make_enter_map(uid):
    if not 1 <= uid <= 0xFFFFFFFF:
        raise ValueError("invalid character UID")
    # Packed upstream MsgAction::MsgInfo: length,type,timestamp,uid,
    # data,x,y,direction,action; per-frame TQClient suffix.
    return struct.pack("<HHiIiHHHH",24,MSG_ACTION,0,uid,0,0,0,0,ACTION_ENTER_MAP)+SEAL

def decode_enter_map(frame,expected_uid,expected_x=8,expected_y=8):
    if len(frame)!=24:
        raise RuntimeError("unexpected enter-map action length")
    (size,msg_type,timestamp,uid,data,x,y,direction,action)=struct.unpack(
        "<HHiIiHHHH",frame)
    if (size,msg_type,uid,data,x,y,action)!=(24,MSG_ACTION,expected_uid,MAP_ID,expected_x,expected_y,ACTION_ENTER_MAP):
        raise RuntimeError("unexpected COPS map entry action payload")
    return (x,y)

def decode_mapinfo(frame):
    if len(frame)!=16:
        raise RuntimeError("unexpected COPS map metadata length")
    size,msg_type,uid,doc,type_flags=struct.unpack("<HHIII",frame)
    if (size,msg_type,uid,doc)!=(16,MSG_MAPINFO,MAP_ID,MAP_ID):
        raise RuntimeError("COPS did not confirm synthetic Twin City map 1002")
    return type_flags

def receive_until(sock,shared,iv,ciphertext,predicate):
    raw=bytearray(ciphertext)
    while len(raw)<MAX_WIRE:
        plain=transform(bytes(raw),key=shared,iv=iv,encrypt=False)
        frames,_=parse_frames(plain)
        if predicate(frames):
            return bytes(raw),frames
        try:
            chunk=sock.recv(min(4096,MAX_WIRE-len(raw)))
        except socket.timeout as err:
            kinds=[(typ,len(frame)) for typ,frame in frames]
            raise RuntimeError("Timed out waiting for map packets; "
                               "received frame types/lengths: "+repr(kinds)) from err
        if not chunk:
            raise RuntimeError("COPS game disconnected before requested map data")
        raw.extend(chunk)
    raise RuntimeError("COPS encrypted game stream exceeded bounded test window")

def enter_synthetic_map(expected_x=8,expected_y=8):
    with socket.create_connection((HOST,GAME_PORT),timeout=4) as sock:
        sock.settimeout(12)
        params=read_challenge(sock)
        public_b,shared=select_dh_response(params)
        if not 16<=len(shared)<=72:
            raise RuntimeError("game DH session key out of range")
        size,kind,account,ticket,ip,port=request_response(PASSWORD)
        if (size,kind,account,port)!=(32,1055,ACCOUNT_ID,GAME_PORT) or ticket<10000:
            raise RuntimeError("account server failed to authorize world-entry login")
        if ip.split(b"\0",1)[0]!=HOST.encode("ascii"):
            raise RuntimeError("COPS redirected nonlocal game client")
        clear_connect=make_connect(account,ticket)
        dh_wire=transform(make_dh_response(public_b),encrypt=True)
        game_wire=transform(clear_connect,key=shared,iv=params["decrypt_iv"],encrypt=True)
        sock.sendall(dh_wire+game_wire)
        incoming,frames=receive_until(
            sock,shared,params["encrypt_iv"],b"",
            lambda items:any(typ==MSG_USERINFO for typ,_ in items)
        )
        uid=next(check_userinfo(frame) for typ,frame in frames if typ==MSG_USERINFO)
        action=make_enter_map(uid)
        # CFB64 encryption must CONTINUE from the original MsgConnect frame.
        next_bytes=transform(clear_connect+action,key=shared,
                             iv=params["decrypt_iv"],encrypt=True)[len(clear_connect):]
        sock.sendall(next_bytes)
        incoming,frames=receive_until(
            sock,shared,params["encrypt_iv"],incoming,
            lambda items:any(typ==MSG_MAPINFO for typ,_ in items)
        )
        actions=[frame for typ,frame in frames
                 if typ==MSG_ACTION and len(frame)==24
                 and struct.unpack_from("<H",frame,22)[0]==ACTION_ENTER_MAP]
        if len(actions)!=1:
            raise RuntimeError("COPS did not acknowledge exactly one enter-map action")
        x,y=decode_enter_map(actions[0],uid,expected_x,expected_y)
        matches=[frame for typ,frame in frames if typ==MSG_MAPINFO]
        if len(matches)!=1:
            raise RuntimeError("ambiguous map metadata response from COPS")
        flags=decode_mapinfo(matches[0])
        if not any(typ==MSG_ACTION and len(frame)==24
                   and struct.unpack_from("<H",frame,22)[0]==ACTION_MAP_ARGB
                   for typ,frame in frames):
            raise RuntimeError("COPS did not send map-entry lighting state")
    print("PASS: real COPS accepted ACTION_ENTER_MAP for authenticated persisted character",flush=True)
    print("PASS: original synthetic map 1002 loaded at coordinates (%d,%d)"%(x,y),flush=True)
    print("PASS: decoded encrypted MsgMapInfo and map lighting action",flush=True)
    print("The retail 5065 client, actual Twin City art and visible gameplay are NOT verified.",flush=True)
    return uid,flags

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--expected-x",type=int,default=8)
    parser.add_argument("--expected-y",type=int,default=8)
    args=parser.parse_args()
    if not 0<=args.expected_x<16 or not 0<=args.expected_y<16:
        parser.error("synthetic map coordinates must be within 0..15")
    enter_synthetic_map(args.expected_x,args.expected_y)
