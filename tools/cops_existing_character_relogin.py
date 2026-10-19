#!/usr/bin/env python3
"""Verify real COPS relogs a saved classic character via encrypted game login.

Only localhost with disposable MariaDB and synthetic map 1002 are supported.
This is not the retail 5065 client and does not prove rendered world entry.
"""
import socket
import struct

from cops_account_success_probe import ACCOUNT_ID, PASSWORD, request_response
from cops_game_ticket_redemption_probe import (
    HOST, GAME_PORT, MSG_TALK, read_challenge, select_dh_response,
    make_dh_response, make_connect
)
from cops_game_dh_proof_probe import transform

SEAL = b"TQServer"
MSG_USERINFO = 1006
MAX_MESSAGE = 2048
MAX_STREAM = 32768
CHARACTER = b"AlphaTester"

def parse_frames(plaintext):
    """Parse complete COPS frames with per-frame server seals.

    Return (decoded frames, offset to first incomplete frame) so fragmented
    TCP reads do not cause either false success or overreads.
    """
    frames = []
    offset = 0
    while len(plaintext)-offset >= 4:
        length, msg_type = struct.unpack_from("<HH", plaintext, offset)
        if length < 4 or length > MAX_MESSAGE:
            raise RuntimeError("invalid encrypted game packet header")
        end = offset + length
        if len(plaintext) < end + len(SEAL):
            break
        if plaintext[end:end+len(SEAL)] != SEAL:
            raise RuntimeError("invalid encrypted COPS server packet seal")
        frames.append((msg_type, plaintext[offset:end]))
        offset = end + len(SEAL)
    return frames, offset

def check_userinfo(packet):
    """Inspect original packed COPS MsgUserInfo layout, not just message type."""
    if len(packet) < 73:
        raise RuntimeError("truncated character MsgUserInfo")
    length, msg_type = struct.unpack_from("<HH", packet)
    if length != len(packet) or msg_type != MSG_USERINFO:
        raise RuntimeError("invalid MsgUserInfo packet")
    character_id = struct.unpack_from("<I", packet, 4)[0]
    money, cps = struct.unpack_from("<II", packet, 14)
    force, dexterity, health, soul, added, hp, mana = struct.unpack_from("<7H", packet, 50)
    level = packet[66]
    profession = packet[67]
    rebirth = packet[69]
    if character_id == 0:
        raise RuntimeError("player has zero character UID")
    if (money,cps,force,dexterity,health,soul,added,hp,mana,
            level,profession,rebirth) != (0,0,4,5,6,7,0,192,35,1,10,0):
        raise RuntimeError("real COPS returned incorrect classic character attributes")
    if CHARACTER not in packet[71:]:
        raise RuntimeError("real COPS did not return saved character name")
    return character_id

def receive_saved_character(sock, shared_key, iv):
    ciphertext = bytearray()
    while len(ciphertext) < MAX_STREAM:
        chunk = sock.recv(min(4096, MAX_STREAM-len(ciphertext)))
        if not chunk:
            raise RuntimeError("COPS disconnected before character loaded")
        ciphertext.extend(chunk)
        plaintext = transform(bytes(ciphertext),key=shared_key,iv=iv,encrypt=False)
        frames, _ = parse_frames(plaintext)
        if frames and frames[0][0] != MSG_TALK:
            raise RuntimeError("expected first login reply from COPS")
        for typ,packet in frames:
            if typ == MSG_USERINFO:
                return check_userinfo(packet)
    raise RuntimeError("COPS did not emit MsgUserInfo within bounded data")

def probe():
    with socket.create_connection((HOST,GAME_PORT),timeout=4) as sock:
        sock.settimeout(12)
        params = read_challenge(sock)
        public_b, shared = select_dh_response(params)
        if not 16<=len(shared)<=72:
            raise RuntimeError("invalid shared session key length")
        length,typ,uid,ticket,ip,port=request_response(PASSWORD)
        if (length,typ,uid,port)!=(32,1055,ACCOUNT_ID,GAME_PORT) or ticket<10000:
            raise RuntimeError("account auth did not issue relog ticket")
        if ip.split(b"\0",1)[0]!=HOST.encode("ascii"):
            raise RuntimeError("nonlocal game redirect")
        dh=transform(make_dh_response(public_b),encrypt=True)
        connect=transform(make_connect(uid,ticket),key=shared,
                          iv=params["decrypt_iv"],encrypt=True)
        # Upstream has not yet implemented fragmented game login reassembly.
        sock.sendall(dh+connect)
        character_id=receive_saved_character(sock,shared,params["encrypt_iv"])
    print("PASS: COPS accepted second authenticated game login and loaded persisted character",flush=True)
    print("PASS: encrypted MsgUserInfo decoded saved level-1 Trojan with zero CP/rebirth",flush=True)
    print("PASS: existing character had a positive UID and expected original stats",flush=True)
    print("The client is a synthetic protocol probe; no retail 5065 graphics, map rendering or movement is asserted.",flush=True)
    return character_id

if __name__=="__main__":
    probe()
