#!/usr/bin/env python3
"""Patch COPS v7 for bounded, single-use account->game transfer tickets."""
from pathlib import Path
import sys

HEADER = r'''// Temporary single-process alpha transfer tickets.
// Account and game listeners MUST be in the same COPS process.
#ifndef TQ_CLASSIC_TRANSFER_TICKETS_H
#define TQ_CLASSIC_TRANSFER_TICKETS_H

#include <QDateTime>
#include <QMutex>
#include <QMutexLocker>
#include <QRandomGenerator>
#include <map>
#include <stdint.h>

class TransferTickets
{
public:
    static TransferTickets& instance()
    {
        static TransferTickets tickets;
        return tickets;
    }

    // The legacy MsgConnect wire field is a signed 32-bit integer.
    bool issue(int32_t account, int32_t& ticket)
    {
        if (account <= 0)
            return false;
        QMutexLocker guard(&mMutex);
        const qint64 now = QDateTime::currentMSecsSinceEpoch();
        expire(now);
        if (mTickets.size() >= MAX_PENDING)
            return false; // fail closed rather than grow without limit

        // System CSPRNG; never use rand() or legacy random() for auth tokens.
        for (unsigned int attempt = 0; attempt < 32; ++attempt)
        {
            const uint32_t candidate =
                QRandomGenerator::system()->generate() & 0x7fffffffU;
            if (candidate < 10000 || mTickets.count((int32_t)candidate))
                continue;
            ticket = (int32_t)candidate;
            // New login invalidates other unused tickets for this account.
            for (auto it = mTickets.begin(); it != mTickets.end(); )
                if (it->second.account == account)
                    it = mTickets.erase(it);
                else
                    ++it;
            mTickets[ticket] = Entry{account, now + TTL_MS};
            return true;
        }
        return false;
    }

    bool consume(int32_t account, int32_t ticket)
    {
        if (account <= 0 || ticket < 10000)
            return false;
        QMutexLocker guard(&mMutex);
        const qint64 now = QDateTime::currentMSecsSinceEpoch();
        expire(now);
        const auto it = mTickets.find(ticket);
        if (it == mTickets.end() || it->second.account != account)
            return false;
        mTickets.erase(it); // strictly single-use
        return true;
    }

private:
    struct Entry { int32_t account; qint64 expires; };
    enum { MAX_PENDING = 4096 };
    static const qint64 TTL_MS = 30000;

    void expire(qint64 now)
    {
        for (auto it = mTickets.begin(); it != mTickets.end(); )
            if (it->second.expires <= now)
                it = mTickets.erase(it);
            else
                ++it;
    }

    TransferTickets() {}
    TransferTickets(const TransferTickets&) = delete;
    TransferTickets& operator=(const TransferTickets&) = delete;
    QMutex mMutex;
    std::map<int32_t, Entry> mTickets;
};

#endif
'''

def replace_once(path, old, new):
    s=path.read_text(encoding="utf-8")
    if s.count(old) != 1:
        raise RuntimeError("unexpected COPS source version: %s (%d matches)" % (path,s.count(old)))
    path.write_text(s.replace(old,new),encoding="utf-8")

def patch(root):
    root=Path(root)
    account=root/"src/Network/msgaccount.cpp"
    connect=root/"src/Network/msgconnect.cpp"
    header=root/"src/Network/transfer_tickets.h"
    if header.exists():
        raise RuntimeError("transfer ticket header already exists")
    # Validate both anchors before modifying any files.
    ac=account.read_text(encoding="utf-8")
    co=connect.read_text(encoding="utf-8")
    if ac.count("            int32_t token = random(10000, INT32_MAX);") != 1 or \
       co.count("    client.setAccountID(mInfo->AccountUID);") != 1:
        raise RuntimeError("account/game login anchors changed")
    header.write_text(HEADER,encoding="utf-8")
    replace_once(account, '#include "msgconnectex.h"',
                 '#include "msgconnectex.h"\n#include "transfer_tickets.h"')
    replace_once(account,
        "            int32_t token = random(10000, INT32_MAX);",
        """            // Only hand off an account after its database authentication.
            int32_t token = 0;
            if (!TransferTickets::instance().issue(client.getAccountID(), token))
            {
                client.disconnect();
                return;
            }""")
    replace_once(connect, '#include "msgdate.h"',
                 '#include "msgdate.h"\n#include "transfer_tickets.h"')
    replace_once(connect,
        """    // set the account UID
    client.setAccountID(mInfo->AccountUID);

    switch (status)""",
        """    // Never trust the account UID from a game-port packet. The transfer
    // ticket was issued only after successful account-port authentication.
    // This check consumes the ticket even if subsequent DB load fails.
    if (status != Client::NORMAL ||
        !TransferTickets::instance().consume(mInfo->AccountUID, mInfo->Data))
    {
        client.disconnect();
        return;
    }
    client.setAccountID(mInfo->AccountUID);

    switch (status)""")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: patch_cops_transfer_tickets.py <cops-checkout>")
    patch(Path(sys.argv[1]))
    print("Installed single-use 30-second account/game tickets (same-process only)")
