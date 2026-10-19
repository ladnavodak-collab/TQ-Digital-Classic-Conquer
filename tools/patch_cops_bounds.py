#!/usr/bin/env python3
"""Apply fail-closed receive bounds fixes to a COPS v7 checkout (source patch, not a deployment)."""
from pathlib import Path
import sys

def replace_exact(path: Path, old: str, new: str):
    data = path.read_text(encoding="utf-8")
    if data.count(old) != 1:
        raise RuntimeError(f"{path}: expected source anchor once, found {data.count(old)}")
    path.write_text(data.replace(old, new), encoding="utf-8")

def patch(root: Path):
    network = root / "src/Network/Sockets/networkclient.cpp"
    old = """    uint8_t buf[NetworkClient::BUFFER_SIZE] = { 0 };
    size_t len = mSocket->read((char*)buf, mSocket->bytesAvailable());

    if (mServer.onReceive != nullptr)
    {
        mServer.onReceive(this, buf, len);
    }"""
    new = """    // Deny oversized queued reads. Never pass bytesAvailable() as the
    // requested length for a smaller, fixed stack buffer.
    const qint64 available = mSocket->bytesAvailable();
    if (available <= 0)
        return;
    if (available > static_cast<qint64>(NetworkClient::BUFFER_SIZE))
    {
        disconnect();
        return;
    }

    uint8_t buf[NetworkClient::BUFFER_SIZE] = { 0 };
    const qint64 received = mSocket->read(reinterpret_cast<char*>(buf),
                                          static_cast<qint64>(sizeof(buf)));
    if (received <= 0)
    {
        disconnect();
        return;
    }
    if (mServer.onReceive != nullptr)
        mServer.onReceive(this, buf, static_cast<size_t>(received));"""
    replace_exact(network, old, new)

    server = root / "src/server.cpp"
    old = """    if (aClient != nullptr && aBuf != nullptr)
    {
        if (aLen < sizeof(Msg::Header))
            return;"""
    new = """    if (aClient != nullptr && aBuf != nullptr)
    {
        if (aLen < sizeof(Msg::Header) || aLen > NetworkClient::BUFFER_SIZE)
        {
            aClient->disconnect();
            return;
        }"""
    replace_exact(server, old, new)
    old = """                    cipher.decrypt(ptr, MsgLoginChallengeS::PADDING_LEN + sizeof(int32_t));
                    ptr += MsgLoginChallengeS::PADDING_LEN; // Padding"""
    new = """                    if (aLen < MsgLoginChallengeS::PADDING_LEN + sizeof(int32_t))
                    {
                        SAFE_DELETE_ARRAY(received);
                        aClient->disconnect();
                        return;
                    }
                    cipher.decrypt(ptr, MsgLoginChallengeS::PADDING_LEN + sizeof(int32_t));
                    ptr += MsgLoginChallengeS::PADDING_LEN; // Padding"""
    replace_exact(server, old, new)
    old = """                    cipher.decrypt(ptr + sizeof(int32_t), size - sizeof(int32_t)); // skip the Size, but decrypt the whole msg

                    size_t len = MsgLoginChallengeS::PADDING_LEN + size;"""
    new = """                    // The key-exchange length is client-controlled and may be
                    // negative or larger than the received data.
                    if (size < sizeof(int32_t) ||
                        size > aLen - MsgLoginChallengeS::PADDING_LEN)
                    {
                        SAFE_DELETE_ARRAY(received);
                        aClient->disconnect();
                        return;
                    }
                    cipher.decrypt(ptr + sizeof(int32_t), size - sizeof(int32_t));

                    size_t len = MsgLoginChallengeS::PADDING_LEN + size;"""
    replace_exact(server, old, new)
    old = """                    for (size_t i = 0; i < aLen; i += size)
                    {
                        #if BYTE_ORDER == BIG_ENDIAN"""
    new = """                    for (size_t i = 0; i < aLen; i += size)
                    {
                        if (aLen - i < sizeof(Msg::Header))
                        {
                            SAFE_DELETE_ARRAY(received);
                            aClient->disconnect();
                            return;
                        }
                        #if BYTE_ORDER == BIG_ENDIAN"""
    replace_exact(server, old, new)
    old = """                            size = SEAL_LEN;

                            continue;"""
    new = """                            if (aLen - i < SEAL_LEN)
                            {
                                SAFE_DELETE_ARRAY(received);
                                aClient->disconnect();
                                return;
                            }
                            size = SEAL_LEN;
                            continue;"""
    replace_exact(server, old, new)
    old = """                        ASSERT(size <= 1024); // invalid msg size...
                        if (size < aLen)"""
    new = """                        if (size < sizeof(Msg::Header) ||
                            size > 1024 || size > aLen - i)
                        {
                            SAFE_DELETE_ARRAY(received);
                            aClient->disconnect();
                            return;
                        }
                        if (size < aLen - i)"""
    replace_exact(server, old, new)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_cops_bounds.py <upstream-source-dir>")
    patch(Path(sys.argv[1]))
    print("Applied defensive receive bounds patch; full TCP reassembly still needed.")
