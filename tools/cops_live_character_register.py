#!/usr/bin/env python3
"""End-to-end synthetic COPS protocol client: create a classic character.

This is a localhost-only disposable CI test, not a retail 5065 client.
"""
import argparse
import socket
import struct
import subprocess

from cops_account_success_probe import ACCOUNT_ID,PASSWORD,ACCOUNT_NAME,field,request_response
from cops_game_ticket_redemption_probe import (
    GAME_PORT,HOST,MSG_TALK,read_challenge,select_dh_response,
    make_dh_response,make_connect
)
from cops_game_dh_proof_probe import transform

CHARACTER="AlphaTester"
PROFESSION=10
MSG_REGISTER=1001
SEAL=b"TQClient"
SERVER_SEAL=b"TQServer"

def register_packet(account_id=ACCOUNT_ID,character=CHARACTER):
    if account_id<=0:
        raise ValueError("account UID must be positive")
    return struct.pack("<HH16s16s16sHHi",60,MSG_REGISTER,
                       field(ACCOUNT_NAME),field(character),field(PASSWORD),
                       1003,PROFESSION,account_id)+SEAL

def recv_one_talk(sock,key,iv):
    encrypted=bytearray()
    size=None
    while size is None or len(encrypted)<size+len(SERVER_SEAL):
        chunk=sock.recv(4096-len(encrypted))
        if not chunk:
            raise RuntimeError("game server closed before replying to login")
        encrypted.extend(chunk)
        clear=transform(bytes(encrypted),key=key,iv=iv,encrypt=False)
        if size is None and len(clear)>=4:
            size,typ=struct.unpack_from("<HH",clear)
            if not 4<=size<=1024 or typ!=MSG_TALK:
                raise RuntimeError("expected encrypted game registration prompt")
        if len(encrypted)>4096:
            raise RuntimeError("game reply oversized")
    clear=transform(bytes(encrypted),key=key,iv=iv,encrypt=False)
    if clear[size:size+8]!=SERVER_SEAL:
        raise RuntimeError("missing encrypted game reply seal")
    return bytes(encrypted)

def register_character():
    with socket.create_connection((HOST,GAME_PORT),timeout=4) as sock:
        sock.settimeout(8)
        params=read_challenge(sock)
        public_b,shared=select_dh_response(params)
        if not 16<=len(shared)<=72:
            raise RuntimeError("unexpected COPS shared Blowfish key")
        size,typ,uid,ticket,ip,port=request_response(PASSWORD)
        if (size,typ,uid,port)!=(32,1055,ACCOUNT_ID,GAME_PORT) or ticket<10000:
            raise RuntimeError("account server did not authorize game transfer")
        if ip.split(bytes([0]),1)[0]!=HOST.encode():
            raise RuntimeError("account server attempted nonlocal redirection")
        connect=make_connect(uid,ticket)
        dh_cipher=transform(make_dh_response(public_b),encrypt=True)
        game_cipher=transform(connect,key=shared,iv=params["decrypt_iv"],encrypt=True)
        # COPS currently requires DH response and first post-DH frame together.
        sock.sendall(dh_cipher+game_cipher)
        welcome=recv_one_talk(sock,shared,params["encrypt_iv"])
        # Continue CFB64 stream after the original MsgConnect bytes, rather
        # than restarting the cipher for a subsequent MsgRegister packet.
        subsequent=transform(connect+register_packet(uid),key=shared,
                             iv=params["decrypt_iv"],encrypt=True)[len(connect):]
        sock.sendall(subsequent)
        ack=sock.recv(4096)
        if len(ack)<4:
            raise RuntimeError("COPS did not acknowledge in-game character creation")
        all_plain=transform(welcome+ack,key=shared,iv=params["encrypt_iv"],encrypt=False)
        new_plain=all_plain[len(welcome):]
        length,kind=struct.unpack_from("<HH",new_plain)
        if kind!=MSG_TALK or length<4 or length>1024:
            raise RuntimeError("unexpected character-registration response")
        print("PASS: actual COPS decrypted MsgRegister after authenticated game transfer",flush=True)
        print("PASS: COPS issued an encrypted character-registration response",flush=True)

def check_database(cli):
    sql=("SELECT `account_id`,`name`,`profession`,`force`,`dexterity`,"
         "`health`,`soul`,`life`,`mana`,`record_map`,`record_x`,`record_y`,"
         "`cps`,`metempsychosis` FROM `user` WHERE `account_id`=78")
    result=subprocess.run(cli+["--batch","--skip-column-names","--execute",sql],
                          text=True,capture_output=True)
    if result.returncode:
        raise RuntimeError("failed querying character registration SQL: "+result.stderr[-200:])
    expected="78\tAlphaTester\t10\t4\t5\t6\t7\t192\t35\t1002\t8\t8\t0\t0"
    if result.stdout.strip()!=expected:
        raise RuntimeError("character was not persisted by COPS with expected classic stats: "+repr(result.stdout.strip()))
    print("PASS: real server-created classic Trojan character persisted in MariaDB with original starting stats",flush=True)
    print("PASS: new character is on synthetic map 1002 with 0 CP and 0 rebirth",flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("register","check-db"))
    parser.add_argument("mysql_cli",nargs="*")
    args=parser.parse_args()
    if args.action=="register":
        register_character()
    else:
        if not args.mysql_cli:parser.error("check-db requires mariadb client command")
        check_database(args.mysql_cli)
