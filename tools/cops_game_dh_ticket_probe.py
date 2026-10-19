#!/usr/bin/env python3
"""Authenticated, loopback-only COPS account -> DH -> game ticket smoke.

Only original test-world geometry and disposable CI credentials are used.
Blowfish is supplied by a tiny executable compiled against COPS upstream itself.
"""
import argparse
import secrets
import socket
import struct
import subprocess

from cops_account_cipher_probe import ACCOUNT_PORT, to_server
from cops_account_success_probe import ACCOUNT_ID, request_packet, decode_response

GAME_PORT = 5816
FIRST_KEY = b"DR654dt34trg4UI6"
ZERO_IV = bytes(8)
SERVER_SEAL = b"TQServer"
CLIENT_SEAL = b"TQClient"
MAX_CHALLENGE = 2048

def exact(sock, count):
    result=bytearray()
    while len(result)<count:
        fragment=sock.recv(count-len(result))
        if not fragment:
            raise RuntimeError("COPS closed during the game handshake")
        result.extend(fragment)
    return bytes(result)

def bridge(executable, operation, key, iv, payload):
    if not (key and payload and len(iv)==8):
        raise ValueError("invalid cipher parameters")
    cmd=[executable,operation,key.hex(),iv.hex(),payload.hex()]
    result=subprocess.run(cmd,text=True,capture_output=True,timeout=4,check=False)
    if result.returncode:
        raise RuntimeError("Original COPS Blowfish test bridge failed")
    decoded=bytes.fromhex(result.stdout.strip())
    if len(decoded)!=len(payload):
        raise RuntimeError("Cipher adapter returned the wrong length")
    return decoded

def unpack_text(buf, at):
    if at+4>len(buf):raise ValueError("Truncated DH text size")
    length=struct.unpack_from("<i",buf,at)[0]
    at+=4
    if not (1<=length<=512) or at+length>len(buf):
        raise ValueError("Invalid DH text field length")
    value=buf[at:at+length].decode("ascii")
    if not all(c in "0123456789abcdefABCDEF" for c in value):
        raise ValueError("DH key is not hexadecimal")
    return value,at+length

def parse_proof(payload):
    """Decode exactly upstream MsgLoginProofA's dynamic nonstandard layout."""
    if len(payload)<60 or payload[-8:]!=SERVER_SEAL:
        raise ValueError("Missing COPS server seal")
    declared=struct.unpack_from("<i",payload,11)[0]
    if declared!=len(payload)-11 or declared>MAX_CHALLENGE:
        raise ValueError("Bad DH proof size")
    at=15
    junk_size=struct.unpack_from("<i",payload,at)[0]
    at+=4
    if not (0<=junk_size<=32) or at+junk_size>len(payload)-8:
        raise ValueError("Bad DH junk length")
    at+=junk_size
    ivs=[]
    for _ in range(2):
        if at+4>len(payload)-8:
            raise ValueError("Missing IV size")
        length=struct.unpack_from("<i",payload,at)[0]
        at+=4
        if length!=8 or at+length>len(payload)-8:
            raise ValueError("Unexpected Blowfish IV size")
        ivs.append(payload[at:at+length])
        at+=length
    p,at=unpack_text(payload,at)
    g,at=unpack_text(payload,at)
    a,at=unpack_text(payload,at)
    if at!=len(payload)-8:
        raise ValueError("Trailing DH key material")
    modulus=int(p,16)
    generator=int(g,16)
    public=int(a,16)
    if not (modulus>10000 and 1<generator<modulus and 1<public<modulus):
        raise ValueError("Invalid DH public parameters")
    return modulus,generator,public,ivs[0],ivs[1]

def build_exchange(modulus,generator,public):
    # Retry until the shared secret's hexadecimal representation has even
    # length; the hardened COPS DH reader explicitly requires even hex.
    for _ in range(24):
        private=secrets.randbits(256) | 1
        b=format(pow(generator,private,modulus),"X").encode("ascii")
        shared=format(pow(public,private,modulus),"X")
        if len(shared)%2==0 and 4<=len(shared)<=144 and 2<=len(b)<=512:
            secret=bytes.fromhex(shared)
            junk=bytes(12)
            frame=bytes(7)+struct.pack("<i",4+4+len(junk)+4+len(b))
            frame+=struct.pack("<i",len(junk))+junk+struct.pack("<i",len(b))+b
            return frame,secret
    raise RuntimeError("Could not generate even-length DH shared secret")

def connect_packet(account,ticket):
    body=struct.pack("<HHii16s",28,1052,account,ticket,
                     b"127.0.0.1".ljust(16,b"\0"))
    return body+CLIENT_SEAL

def get_transfer_ticket():
    with socket.create_connection(("127.0.0.1",ACCOUNT_PORT),timeout=3) as sock:
        sock.settimeout(5)
        sock.sendall(to_server(request_packet()))
        wire=exact(sock,40)
    plain=decode_response(wire)
    length,kind,account,ticket,ip,port=struct.unpack_from("<HHii16sI",plain)
    if (length,kind,account,port)!=(32,1055,ACCOUNT_ID,GAME_PORT):
        raise RuntimeError("Account server did not authenticate the disposable account")
    if ip.split(b"\0",1)[0]!=b"127.0.0.1" or ticket<10000:
        raise RuntimeError("Invalid issued game transfer ticket")
    return account,ticket

def probe(helper):
    account,ticket=get_transfer_ticket()
    with socket.create_connection(("127.0.0.1",GAME_PORT),timeout=3) as sock:
        sock.settimeout(6)
        encrypted=exact(sock,15)
        head=bridge(helper,"decrypt",FIRST_KEY,ZERO_IV,encrypted)
        size=struct.unpack_from("<i",head,11)[0]
        if not 60<=size<=MAX_CHALLENGE:
            raise RuntimeError("COPS game-port key proof length invalid")
        encrypted+=exact(sock,11+size-15)
        proof=bridge(helper,"decrypt",FIRST_KEY,ZERO_IV,encrypted)
        prime,base,server_pub,en_iv,de_iv=parse_proof(proof)
        exchange,shared=build_exchange(prime,base,server_pub)
        sock.sendall(bridge(helper,"encrypt",FIRST_KEY,ZERO_IV,exchange))
        # The server switches to DH-derived Blowfish upon processing this
        # standalone response, and must NOT disconnect on a zero-byte tail.
        data=connect_packet(account,ticket)
        sock.sendall(bridge(helper,"encrypt",shared,de_iv,data))
        answer=sock.recv(4096)
        if len(answer)<8:
            raise RuntimeError("No game-port role-entry response after ticket redemption")
        decrypted=bridge(helper,"decrypt",shared,en_iv,answer)
        length,kind=struct.unpack_from("<HH",decrypted)
        if kind!=1004 or not (4<=length<=len(decrypted)):
            raise RuntimeError("Invalid COPS game-port entry response frame")
    print("PASS: real COPS account ticket redeemed after client/server DH exchange",flush=True)
    print("PASS: encrypted game-port MsgConnect returned a MsgTalk role-entry response",flush=True)
    print("This is an ORIGINAL Python/C++ test client, not the proprietary 5065 game executable.",flush=True)
    print("No real map rendering, character creation or movement is asserted.",flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("blowfish_helper",help="Test-only bridge built from upstream Blowfish")
    args=parser.parse_args()
    probe(args.blowfish_helper)
