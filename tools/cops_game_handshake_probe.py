#!/usr/bin/env python3
"""Local-only COPS game-port Blowfish-CFB64/DH compatibility probe.

No retail client, copyrighted assets or user accounts are involved.
"""
import argparse
import ctypes
import ctypes.util
import secrets
import socket
import struct

GAME_PORT=5816
ACCOUNT_PORT=9958
INITIAL_KEY=b"DR654dt34trg4UI6"
SERVER_SEAL=b"TQServer"
CLIENT_SEAL=b"TQClient"
MSG_CONNECT=1052
MSG_TALK=1004
PADDING_LEN=11
MAX_HANDSHAKE=2048

class BFKey(ctypes.Structure):
    _fields_=[("P",ctypes.c_uint32*18),("S",ctypes.c_uint32*1024)]

class BlowfishCFB:
    """Bind OpenSSL's original BF_CFB64, including variable-sized DH seed keys."""
    def __init__(self,key,iv,encrypt):
        if not (1<=len(key)<=72) or len(iv)!=8:
            raise ValueError("invalid Blowfish key or IV")
        name=ctypes.util.find_library("crypto")
        if not name:raise RuntimeError("libcrypto is required in Linux CI")
        self.lib=ctypes.CDLL(name)
        self.lib.BF_set_key.argtypes=[ctypes.POINTER(BFKey),ctypes.c_int,ctypes.c_void_p]
        self.lib.BF_set_key.restype=None
        self.lib.BF_cfb64_encrypt.argtypes=[
            ctypes.c_void_p,ctypes.c_void_p,ctypes.c_long,ctypes.POINTER(BFKey),
            ctypes.c_void_p,ctypes.POINTER(ctypes.c_int),ctypes.c_int]
        self.lib.BF_cfb64_encrypt.restype=None
        self.key=BFKey()
        seed=ctypes.create_string_buffer(key)
        self.lib.BF_set_key(ctypes.byref(self.key),len(key),seed)
        self.iv=(ctypes.c_ubyte*8).from_buffer_copy(iv)
        self.n=ctypes.c_int(0)
        self.encrypt=int(encrypt)

    def process(self,data):
        if not data:return b""
        source=ctypes.create_string_buffer(data)
        output=ctypes.create_string_buffer(len(data))
        self.lib.BF_cfb64_encrypt(source,output,len(data),ctypes.byref(self.key),
                                 self.iv,ctypes.byref(self.n),self.encrypt)
        return output.raw

def read_exact(sock,n):
    if not (0<=n<=MAX_HANDSHAKE):
        raise ValueError("out-of-bounds game handshake request")
    output=bytearray()
    while len(output)<n:
        chunk=sock.recv(n-len(output))
        if not chunk:
            raise RuntimeError("Game socket closed in middle of handshake")
        output.extend(chunk)
    return bytes(output)

def parse_request(clear):
    if len(clear)<PADDING_LEN+4:
        raise ValueError("short Blowfish login proof")
    size=struct.unpack_from("<i",clear,PADDING_LEN)[0]
    if size<=40 or size>MAX_HANDSHAKE-PADDING_LEN or len(clear)!=PADDING_LEN+size:
        raise ValueError("invalid COPS proof size")
    cursor=PADDING_LEN+4
    def sized_blob(maxlen):
        nonlocal cursor
        if cursor+4>len(clear):raise ValueError("truncated proof field length")
        n=struct.unpack_from("<i",clear,cursor)[0]
        cursor+=4
        if not (0<=n<=maxlen) or cursor+n>len(clear):
            raise ValueError("invalid proof field size")
        value=clear[cursor:cursor+n]
        cursor+=n
        return value
    junk=sized_blob(64)
    en_iv=sized_blob(8)
    de_iv=sized_blob(8)
    p_text=sized_blob(512)
    g_text=sized_blob(16)
    a_text=sized_blob(512)
    if cursor+len(SERVER_SEAL)!=len(clear) or clear[cursor:]!=SERVER_SEAL:
        raise ValueError("COPS challenge seal invalid")
    if len(en_iv)!=8 or len(de_iv)!=8:
        raise ValueError("bad IV size")
    if not (80<=len(p_text)<=256 and 1<=len(g_text)<=8 and 1<=len(a_text)<=256):
        raise ValueError("unexpected DH encoding sizes")
    for item in (p_text,g_text,a_text):
        if not all(ch in b"0123456789abcdefABCDEF" for ch in item):
            raise ValueError("non-hex DH public value")
    p,g,a=(int(v,16) for v in (p_text,g_text,a_text))
    if p.bit_length()<500 or not (2<=g<p) or not (2<=a<p-1):
        raise ValueError("invalid DH parameters")
    return {"p":p,"g":g,"a":a,"en_iv":en_iv,"de_iv":de_iv,"junk_size":len(junk)}

def read_challenge(sock):
    cipher=BlowfishCFB(INITIAL_KEY,bytes(8),False)
    prefix=cipher.process(read_exact(sock,PADDING_LEN+4))
    advertised=struct.unpack_from("<i",prefix,PADDING_LEN)[0]
    if not (40<advertised<MAX_HANDSHAKE-PADDING_LEN):
        raise ValueError("unreasonable COPS pre-login challenge")
    tail=cipher.process(read_exact(sock,advertised-4))
    return parse_request(prefix+tail)

def build_exchange(params):
    """Calculate an ephemeral B and S without emitting secrets to logs."""
    p,g,a=params["p"],params["g"],params["a"]
    for _ in range(64):
        exponent=secrets.randbelow(p-3)+2
        b_value=pow(g,exponent,p)
        shared=pow(a,exponent,p)
        s_hex=format(shared,"X")
        if (2<=b_value<p-1 and len(s_hex)%2==0 and len(s_hex)<=144):
            b_hex=format(b_value,"X").encode("ascii")
            seed=bytes.fromhex(s_hex)
            return b_hex,seed
    raise RuntimeError("Could not derive an even-length classic DH seed")

def exchange_body(b_hex):
    if len(b_hex)>512:raise ValueError("DH response too large")
    junk=bytes(12)
    size=4+4+len(junk)+4+len(b_hex)
    return bytes(7)+struct.pack("<ii",size,len(junk))+junk+struct.pack("<i",len(b_hex))+b_hex

def game_connect(account_id,ticket):
    if not (0<account_id<2**31 and 10000<=ticket<2**31):
        raise ValueError("invalid disposable game handoff")
    return struct.pack("<HHii16s",24,MSG_CONNECT,account_id,ticket,bytes(16))+CLIENT_SEAL

def probe_challenge():
    with socket.create_connection(("127.0.0.1",GAME_PORT),timeout=4) as sock:
        sock.settimeout(8)
        params=read_challenge(sock)
    print("PASS: real COPS game listener emitted a decryptable Blowfish-CFB64 DH challenge",flush=True)
    print("PASS: DH prime, generator, public key, symmetric IVs, payload lengths and TQServer seal verified",flush=True)
    return params

def redeem_ticket():
    from cops_account_success_probe import request_response, PASSWORD, ACCOUNT_ID
    response=request_response(PASSWORD)
    _len,typ,uid,ticket,_ip,_port=response
    if typ!=1055 or uid!=ACCOUNT_ID or ticket<10000:
        raise RuntimeError("Account-port login did not issue test ticket")

    with socket.create_connection(("127.0.0.1",GAME_PORT),timeout=4) as sock:
        sock.settimeout(8)
        params=read_challenge(sock)
        public_b,shared_key=build_exchange(params)
        first=BlowfishCFB(INITIAL_KEY,bytes(8),True).process(exchange_body(public_b))
        # Game server's DeIV encrypts the client's MsgConnect after DH.
        subsequent=BlowfishCFB(shared_key,params["de_iv"],True).process(
            game_connect(ACCOUNT_ID,ticket))
        sock.sendall(first+subsequent)  # one receive call: original COPS lacks TCP reassembly
        reader=BlowfishCFB(shared_key,params["en_iv"],False)
        head=reader.process(read_exact(sock,4))
        frame_len,frame_type=struct.unpack("<HH",head)
        if not (4<=frame_len<=1024 and frame_type==MSG_TALK):
            raise RuntimeError("No authorized character registration response")
        remaining=reader.process(read_exact(sock,frame_len+len(SERVER_SEAL)-4))
        if not remaining.endswith(SERVER_SEAL):
            raise RuntimeError("Post-DH first game response had incorrect seal")
    print("PASS: real COPS accepted DH exchange and a valid single-use game ticket",flush=True)
    print("PASS: game listener sent encrypted new-character response (MSG_TALK)",flush=True)
    print("No real client rendering, movement, or world entry is asserted.",flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("challenge","redeem"))
    args=parser.parse_args()
    if args.action=="challenge":
        probe_challenge()
    else:
        redeem_ticket()
