#!/usr/bin/env python3
"""Re-login an existing COPS character over the actual localhost game protocol.

Requires the earlier live registration fixture in this disposable CI server.
Not a retail 5065 client or actual Twin City graphic/map asset.
"""
import socket
import struct

from cops_account_success_probe import ACCOUNT_ID, PASSWORD, request_response
from cops_game_ticket_redemption_probe import (
    HOST, GAME_PORT, read_challenge, select_dh_response,
    make_dh_response, make_connect
)
from cops_game_dh_proof_probe import transform

SEAL=b"TQServer"
MSG_TALK=1004
MSG_DATE=1033
MSG_USERINFO=1006
MAX_WIRE=16384
MAX_MESSAGE=4096
EXPECTED_NAME=b"AlphaTester"

def split_frames(clear):
    """Return (type, payload) complete COPS frames; tolerate trailing fragments."""
    if len(clear)>MAX_WIRE:
        raise ValueError("oversized game reply stream")
    result=[]
    pos=0
    while len(clear)-pos>=4:
        size,kind=struct.unpack_from("<HH",clear,pos)
        if not 4<=size<=MAX_MESSAGE:
            raise ValueError("invalid COPS game message length")
        end=pos+size+len(SEAL)
        if end>len(clear):
            break
        if clear[pos+size:end]!=SEAL:
            raise ValueError("missing COPS server packet seal")
        result.append((kind,clear[pos:pos+size]))
        pos=end
    return result,clear[pos:]

def inspect_userinfo(packet):
    """Validate the exact MsgUserInfo positional layout from upstream COPS."""
    if len(packet)<74:
        raise ValueError("truncated MsgUserInfo")
    size,kind=struct.unpack_from("<HH",packet)
    if size!=len(packet) or kind!=MSG_USERINFO:
        raise ValueError("wrong MsgUserInfo header")
    uid=struct.unpack_from("<I",packet,4)[0]
    money,cps=struct.unpack_from("<II",packet,14)
    force,dexterity,health,soul=struct.unpack_from("<HHHH",packet,50)
    level,profession,autoallot,rebirth,showname=struct.unpack_from("<BBBBB",packet,66)
    if packet[71]<1 or packet[72]!=len(EXPECTED_NAME):
        raise ValueError("invalid player name string packing")
    name=packet[73:73+packet[72]]
    if name!=EXPECTED_NAME:
        raise ValueError("wrong loaded character name")
    expected=(money,cps,force,dexterity,health,soul,level,profession,rebirth,showname)
    if uid==0 or expected!=(0,0,4,5,6,7,1,10,0,1):
        raise ValueError("loaded player stats diverged from classic fixture")
    return {"uid":uid,"name":name.decode("ascii"),"level":level,
            "profession":profession,"cps":cps,"rebirths":rebirth}

def reenter_character():
    with socket.create_connection((HOST,GAME_PORT),timeout=4) as sock:
        sock.settimeout(8)
        params=read_challenge(sock)
        public,secret=select_dh_response(params)
        if not 16<=len(secret)<=72:
            raise RuntimeError("unexpected game DH secret size")
        size,typ,uid,ticket,ip,port=request_response(PASSWORD)
        if (size,typ,uid,port)!=(32,1055,ACCOUNT_ID,GAME_PORT) or ticket<10000:
            raise RuntimeError("account server rejected re-login")
        if ip.split(bytes([0]),1)[0]!=HOST.encode("ascii"):
            raise RuntimeError("non-local game redirect")
        encrypted_dh=transform(make_dh_response(public),encrypt=True)
        encrypted_connect=transform(make_connect(uid,ticket),key=secret,
                                    iv=params["decrypt_iv"],encrypt=True)
        # Existing COPS requires DH and first encrypted post-DH frame together.
        sock.sendall(encrypted_dh+encrypted_connect)
        raw=bytearray()
        seen={}
        for _ in range(16):
            chunk=sock.recv(4096)
            if not chunk:
                break
            raw.extend(chunk)
            if len(raw)>MAX_WIRE:
                raise RuntimeError("oversized character entry output")
            clear=transform(bytes(raw),key=secret,iv=params["encrypt_iv"],encrypt=False)
            frames,tail=split_frames(clear)
            for typ,payload in frames:
                seen.setdefault(typ,payload)
            if all(t in seen for t in (MSG_TALK,MSG_DATE,MSG_USERINFO)):
                break
        if not all(t in seen for t in (MSG_TALK,MSG_DATE,MSG_USERINFO)):
            raise RuntimeError("character re-login lacked entrance reply, date, or MsgUserInfo: "+
                               repr(sorted(seen.keys())))
        info=inspect_userinfo(seen[MSG_USERINFO])
        print("PASS: COPS redeemed a NEW single-use ticket for an existing character",flush=True)
        print("PASS: encrypted entrance reply, server date and real MsgUserInfo decoded",flush=True)
        print("PASS: server reloaded classic level-1 Trojan with zero CP and zero rebirth",info,flush=True)
        print("Not a retail 5065 login, client-rendered map, or movement test.",flush=True)

if __name__=="__main__":
    reenter_character()
