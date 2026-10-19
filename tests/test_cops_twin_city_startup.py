"""Regression tests for the COPS startup source transformation."""
import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_startup_gate import patch

SERVER = """#include <stdio.h>
void boot() {
    DOIF(err, db.loadAllMagics());

    fprintf(stdout, "\\n");

    mAccServer.listen(Server::ACCSERVER_PORT);
    mMsgServer.listen(Server::MSGSERVER_PORT);
}
"""
TCP_H = "    void listen(uint16_t aPort);"
TCP_CPP = """void
TcpServer :: listen(uint16_t aPort)
{
    if (!mIsListening)
    {
        mServer.listen(QHostAddress::Any, aPort);
        mPort = aPort;
        mIsListening = true;
    }
}"""

class TwinCityStartupGuardTests(unittest.TestCase):
    def test_requires_twin_city_before_any_socket(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"src/Network/Sockets").mkdir(parents=True)
            (root/"src/server.cpp").write_text(SERVER)
            (root/"src/Network/Sockets/tcpserver.h").write_text(TCP_H)
            (root/"src/Network/Sockets/tcpserver.cpp").write_text(TCP_CPP)
            patch(root)
            source=(root/"src/server.cpp").read_text()
            self.assertIn("mgr.getMap(1002) == nullptr", source)
            self.assertIn("return ERROR_NOT_FOUND;", source)
            self.assertLess(source.index("mgr.getMap(1002)"),source.index("mAccServer.listen"))
            self.assertLess(source.index("mgr.getMap(1002)"),source.index("mMsgServer.listen"))
            self.assertIn("QHostAddress::LocalHost",(root/"src/Network/Sockets/tcpserver.cpp").read_text())
    def test_source_anchor_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"src").mkdir()
            (root/"src/server.cpp").write_text("wrong upstream source")
            with self.assertRaises(RuntimeError):
                patch(root)

if __name__=="__main__":
    unittest.main()
