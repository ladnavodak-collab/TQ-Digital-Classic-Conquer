#!/usr/bin/env python3
"""Require redeemed account->game ticket for new character registration."""
from pathlib import Path
import sys

def replace_once(path, before, after):
    s=path.read_text(encoding="utf-8")
    if s.count(before)!=1:
        raise RuntimeError("COPS register source drift in %s: %d anchors"%(path,s.count(before)))
    path.write_text(s.replace(before,after),encoding="utf-8")

def patch(root):
    root=Path(root)
    client=root/"src/client.h"
    constructor=root/"src/client.cpp"
    game=root/"src/Network/msgconnect.cpp"
    register=root/"src/Network/msgregister.cpp"

    replace_once(client,
        '''    /** Set the account ID of the client. */''',
        '''    /** Only a game-port ticket redemption may authorize role creation. */
    bool hasVerifiedGameTicket() const { return mVerifiedGameTicket; }
    void markGameTicketVerified() { mVerifiedGameTicket = true; }

    /** Set the account ID of the client. */''')
    replace_once(client,
        '''    int32_t mAccountID; //!< the account ID''',
        '''    int32_t mAccountID; //!< the account ID
    bool mVerifiedGameTicket; //!< set only on valid game-server transfer''')
    replace_once(constructor,
        '''      mAccountID(-1), mAccLvl(0), mFlags(0),''',
        '''      mAccountID(-1), mVerifiedGameTicket(false), mAccLvl(0), mFlags(0),''')
    replace_once(game,
        '''    client.setAccountID(mInfo->AccountUID);

    switch (status)''',
        '''    client.setAccountID(mInfo->AccountUID);
    client.markGameTicketVerified();

    switch (status)''')
    # Login-register messages used to call Database::authenticate again with
    # plaintext password, which is unnecessary and can mutate mAccountID
    # on the game socket. Account identity comes from the redeemed ticket.
    old='''    if (isValidString(mInfo->Account))
    {
        if (isValidString(mInfo->Password))
        {
            if (IS_SUCCESS(db.authenticate(client, mInfo->Account, mInfo->Password)) &&
                client.getAccountID() == mInfo->AccountUID)
            {
                if (isValidNameString(mInfo->Name))'''
    new='''    // Only permit new roles after the game-port transfer ticket was
    // verified, and never trust unbounded fixed-length packet strings.
    if (client.getStatus() != Client::NORMAL ||
        !client.hasVerifiedGameTicket() ||
        client.getAccountID() <= 0 ||
        client.getAccountID() != mInfo->AccountUID ||
        client.getPlayer() != nullptr)
    {
        client.disconnect();
        return;
    }
    if (!memchr(mInfo->Account, 0, sizeof(mInfo->Account)) ||
        !memchr(mInfo->Name, 0, sizeof(mInfo->Name)) ||
        !memchr(mInfo->Password, 0, sizeof(mInfo->Password)))
    {
        client.disconnect();
        return;
    }

    if (isValidString(mInfo->Account))
    {
        if (isValidString(mInfo->Password))
        {
            if (client.hasVerifiedGameTicket() &&
                client.getAccountID() == mInfo->AccountUID)
            {
                if (isValidNameString(mInfo->Name))'''
    replace_once(register,old,new)
    replace_once(register, '#include "msgtalk.h"',
                 '#include "msgtalk.h"\n#include <string.h>')

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: patch_cops_registration_ticket.py <upstream-cops>")
    patch(Path(sys.argv[1]))
    print("Require verified game ticket for new character registration")
