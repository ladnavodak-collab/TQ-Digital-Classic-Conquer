#!/usr/bin/env python3
"""Disposable local-only COPS account -> DH -> game transfer-ticket redemption.

This uses historical COPS protocol and synthetic SQL account only; NEVER expose
the legacy client/network listeners to the public internet based on this test.
"""
import secrets
import socket
import struct

from cops_account_success_probe import ACCOUNT_ID, PASSWORD, request_response
from cops_game_dh_proof_probe import decode_proof, transform, MAX_PROOF

HOST="127.0.0.1"
GAME_PORT=5816
MSG_CONNECT=1052
MSG_TALK=1004
SEAL=b"TQClient"

def read_challenge(sock):
    ciphertext=bytearray()
    expected=None
    while expected is None or len(ciphertext)<expected:
        chunk=sock.recv(MAX_PROOF-len(ciphertext))
        if not chunk:
            raise RuntimeError("COPS closed game connection before DH proof")
        ciphertext.extend(chunk)
        if expected is None and len(ciphertext)>=15:
            plain_header=transform(bytes(ciphertext[:15]))
            claimed=struct.unpack_from("<i",plain_header,11)[0]
            expected=11+claimed
            if not 64<=expected<=MAX_PROOF:
                raise RuntimeError("invalid COPS game challenge length")
        if expected is not None and len(ciphertext)>expected:
            raise RuntimeError("game server sent extra data before DH response")
    return decode_proof(bytes(ciphertext))

def select_dh_response(params):
    p=int(params["p"],16)
    g=int(params["g"],16)
    a=int(params["a"],16)
    if p.bit_length()<256 or g!=5 or not 1<a<p-1:
        raise ValueError("invalid DH public parameters")
    for _ in range(32):
        private=secrets.randbits(256) | 3
        b=pow(g,private,p)
        shared=pow(a,private,p)
        shared_hex=format(shared,"X")
        # Upstream COPS expects an even-length hex secret for hex2bin.
        if b>1 and len(shared_hex)%2==0 and len(shared_hex)<=144:
            return format(b,"X").encode("ascii"),bytes.fromhex(shared_hex)
    raise RuntimeError("could not generate even-length legacy DH shared seed")

def make_dh_response(public_b):
    if not public_b or len(public_b)>512:
        raise ValueError("invalid DH public response length")
    payload=struct.pack("<i",12)+bytes(12)+struct.pack("<i",len(public_b))+public_b
    return bytes(7)+struct.pack("<i",len(payload)+4)+payload

def make_connect(account_id,token):
    if account_id<=0 or token<10000:
        raise ValueError("invalid account transfer")
    return struct.pack("<HHii16s",28,MSG_CONNECT,account_id,token,bytes(16))+SEAL

def redeem_transfer_ticket():
    with socket.create_connection((HOST,GAME_PORT),timeout=4) as sock:
        sock.settimeout(8)
        params=read_challenge(sock)
        public_b,shared_key=select_dh_response(params)
        if not 16<=len(shared_key)<=72:
            raise RuntimeError("unexpected legacy Blowfish DH shared-key length")
        size,typ,uid,ticket,ip,port=request_response(PASSWORD)
        if (size,typ,uid,port)!=(32,1055,ACCOUNT_ID,GAME_PORT) or ticket<10000:
            raise RuntimeError("COPS did not issue valid transfer ticket")
        if ip.split(bytes([0]),1)[0]!=HOST.encode("ascii"):
            raise RuntimeError("account redirect is not localhost")
        dh_wire=transform(make_dh_response(public_b),encrypt=True)
        game_wire=transform(make_connect(uid,ticket),key=shared_key,
                            iv=params["decrypt_iv"],encrypt=True)
        # Upstream parser requires the DH response and post-handshake game
        # frame in a *single* receive. This is a known TCP-reassembly blocker.
        sock.sendall(dh_wire+game_wire)
        reply=sock.recv(4096)
        if len(reply)<4:
            raise RuntimeError("No game-server response after DH and transfer ticket")
        plain=transform(reply,key=shared_key,iv=params["encrypt_iv"],encrypt=False)
        length,message_type=struct.unpack_from("<HH",plain)
        if message_type!=MSG_TALK or not 4<=length<=1024:
            raise RuntimeError("Game did not return the expected new-character reply (type=%d)"%message_type)
        if len(plain)<length:
            raise RuntimeError("Incomplete game-server welcome frame")
        print("PASS: real COPS accepted valid DH exchange and redeemed account transfer ticket",flush=True)
        print("PASS: game-server encrypted welcome/character-registration prompt decoded",flush=True)
        print("This is a synthetic protocol client, NOT retail 5065 login, character creation, map entry or gameplay.",flush=True)

if __name__=="__main__":
    redeem_transfer_ticket()
