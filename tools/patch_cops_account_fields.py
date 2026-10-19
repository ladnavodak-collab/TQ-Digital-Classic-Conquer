#!/usr/bin/env python3
"""Validate fixed-size account fields and login state in upstream COPS."""
from pathlib import Path
import sys

def patch(root):
    p=Path(root)/"src/Network/msgaccount.cpp"
    s=p.read_text(encoding="utf-8")
    old="""    Client& client = *aClient;
    client.setAccount(mInfo->Account);

    uint8_t seed[RC5::KEY_SIZE] ="""
    new="""    Client& client = *aClient;
    // All three fields arrive as fixed-size bytes, not guaranteed C strings.
    // Never copy Account or print Server until termination is established.
    if (client.getStatus() != Client::NOT_AUTHENTICATED ||
        !memchr(mInfo->Account, '\\0', sizeof(mInfo->Account)) ||
        !memchr(mInfo->Server, '\\0', sizeof(mInfo->Server)))
    {
        client.disconnect();
        return;
    }

    uint8_t seed[RC5::KEY_SIZE] ="""
    if s.count(old)!=1:raise RuntimeError("Account pre-decrypt source anchor mismatch")
    s=s.replace(old,new)
    old2="""    cipher.decrypt((uint8_t*)mInfo->Password, sizeof(mInfo->Password));

    if (isValidString(mInfo->Account) && isValidString(mInfo->Password))"""
    new2="""    cipher.decrypt((uint8_t*)mInfo->Password, sizeof(mInfo->Password));

    // The decrypted 16/32-byte password may lack a terminator too.
    if (!memchr(mInfo->Password, '\\0', sizeof(mInfo->Password)))
    {
        client.disconnect();
        return;
    }

    if (isValidString(mInfo->Account) && isValidString(mInfo->Password))"""
    if s.count(old2)!=1:raise RuntimeError("Account post-decrypt source anchor mismatch")
    s=s.replace(old2,new2)
    old3="""        if (IS_SUCCESS(db.authenticate(client, mInfo->Account, mInfo->Password)))
        {
            fprintf(stdout, "Connection of %s on %s...\\n","""
    new3="""        if (IS_SUCCESS(db.authenticate(client, mInfo->Account, mInfo->Password)))
        {
            client.setAccount(mInfo->Account);
            fprintf(stdout, "Connection of %s on %s...\\n","""
    if s.count(old3)!=1:raise RuntimeError("Account authenticated state anchor mismatch")
    s=s.replace(old3,new3)
    p.write_text(s,encoding="utf-8")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: patch_cops_account_fields.py <upstream-source>")
    patch(Path(sys.argv[1]))
    print("Applied account packet bounds and state validation")
