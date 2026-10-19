#!/usr/bin/env python3
"""Reject pre-authenticated COPS MsgWalk and acknowledge only successful moves."""
from pathlib import Path
import sys

def replace_one(path, old, new):
    data=path.read_text(encoding="utf-8")
    if data.count(old)!=1:
        raise RuntimeError("Unexpected COPS walk source anchor (%d): %s"%(data.count(old),path))
    path.write_text(data.replace(old,new),encoding="utf-8")

def patch(root):
    walk=Path(root)/"src/Network/msgwalk.cpp"
    replace_one(walk,
        """    ASSERT(aClient != nullptr);
    ASSERT(aClient->getPlayer() != nullptr);

    Client& client = *aClient;""",
        """    if (aClient == nullptr)
        return;
    // No walking before the account-to-game token was actually redeemed,
    // or when there is no loaded player. Do not ASSERT on untrusted packets.
    if (aClient->getStatus() != Client::NORMAL ||
        !aClient->hasVerifiedGameTicket() ||
        aClient->getPlayer() == nullptr)
    {
        aClient->disconnect();
        return;
    }

    Client& client = *aClient;""")
    replace_one(walk,
        """    player.send(this); // send back...
    if (player.move(newX, newY, dir))
    {
        // broadcast the message to everyone
        player.broadcastRoomMsg(this, false);
    }""",
        """    if (player.move(newX, newY, dir))
    {
        // Only acknowledge a move that passed the actual map tile checks.
        player.send(this);
        player.broadcastRoomMsg(this, false);
    }""")

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: patch_cops_walk_guard.py <cops-upstream>")
    patch(Path(sys.argv[1]))
    print("Hardened real COPS MsgWalk authentication and positive acknowledgement")
