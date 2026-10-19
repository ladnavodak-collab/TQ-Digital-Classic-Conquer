#!/usr/bin/env python3
"""Make COPS startup fail closed on data load errors and failed local listeners."""
from pathlib import Path
import sys

def replace_one(path, old, new):
    data = path.read_text(encoding="utf-8")
    if data.count(old) != 1:
        raise RuntimeError(f"upstream anchor mismatch in {path}: {data.count(old)}")
    path.write_text(data.replace(old, new), encoding="utf-8")

def patch(root: Path):
    server = root / "src/server.cpp"
    replace_one(server,
        '''    DOIF(err, db.loadAllMagics());

    fprintf(stdout, "\\n");''',
        '''    DOIF(err, db.loadAllMagics());

    // DOIF stores an error but does not return. Never announce ready
    // or bind sockets after a failed SQL/world data load.
    if (err != ERROR_SUCCESS)
    {
        fprintf(stderr, "COPS startup aborted: world data is incomplete.\\n");
        LOG(ERROR, "COPS startup aborted: world data is incomplete.");
        return err;
    }

    fprintf(stdout, "\\n");''')
    # The SQL loader can successfully return zero rows; a server without map
    # 1002 is not ready for classic game-client world entry.
    replace_one(server,
        '''    fprintf(stdout, "\\n");

    mAccServer.listen(Server::ACCSERVER_PORT);''',
        '''    // A successful query does not mean the starter city exists.
    // Require both SQL map registration and its associated loaded DMap.
    if (mgr.getMap(1002) == nullptr)
    {
        fprintf(stderr, "COPS startup aborted: Twin City map 1002 is not loaded.\\n");
        LOG(ERROR, "COPS startup aborted: Twin City map 1002 is not loaded.");
        return ERROR_NOT_FOUND;
    }

    fprintf(stdout, "\\n");

    mAccServer.listen(Server::ACCSERVER_PORT);''')
    replace_one(server,
        '''    mAccServer.listen(Server::ACCSERVER_PORT);''',
        '''    if (!mAccServer.listen(Server::ACCSERVER_PORT))
        return ERROR_NETWORK_ERROR;''')
    replace_one(server,
        '''    mMsgServer.listen(Server::MSGSERVER_PORT);''',
        '''    if (!mMsgServer.listen(Server::MSGSERVER_PORT))
        return ERROR_NETWORK_ERROR;''')

    header = root / "src/Network/Sockets/tcpserver.h"
    replace_one(header, "    void listen(uint16_t aPort);", "    bool listen(uint16_t aPort);")
    implementation = root / "src/Network/Sockets/tcpserver.cpp"
    replace_one(implementation,
        '''void
TcpServer :: listen(uint16_t aPort)
{
    if (!mIsListening)
    {
        mServer.listen(QHostAddress::Any, aPort);
        mPort = aPort;
        mIsListening = true;
    }
}''',
        '''bool
TcpServer :: listen(uint16_t aPort)
{
    if (mIsListening)
        return true;

    // Fail closed and restrict the current alpha to loopback.
    // External bind permissions require a separate security review.
    if (!mServer.listen(QHostAddress::LocalHost, aPort))
        return false;
    mPort = aPort;
    mIsListening = true;
    return true;
}''')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_cops_startup_gate.py <upstream-source-dir>")
    patch(Path(sys.argv[1]))
    print("Added SQL/world startup gate and verified loopback listener binding.")
