import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_transfer_tickets import patch

ACCOUNT='''#include "msgconnectex.h"
            int32_t token = random(10000, INT32_MAX);
'''
CONNECT='''#include "msgdate.h"
    // set the account UID
    client.setAccountID(mInfo->AccountUID);

    switch (status)'''
class TransferTicketPatchTests(unittest.TestCase):
    def test_client_uid_requires_consumed_ticket(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            base=root/"src/Network"
            base.mkdir(parents=True)
            (base/"msgaccount.cpp").write_text(ACCOUNT)
            (base/"msgconnect.cpp").write_text(CONNECT)
            patch(root)
            acc=(base/"msgaccount.cpp").read_text()
            game=(base/"msgconnect.cpp").read_text()
            header=(base/"transfer_tickets.h").read_text()
            self.assertLess(game.index("consume(mInfo->AccountUID, mInfo->Data)"),
                            game.index("client.setAccountID(mInfo->AccountUID)"))
            self.assertIn("TransferTickets::instance().issue",acc)
            self.assertIn("QRandomGenerator::system()->generate()",header)
            self.assertIn("mTickets.erase(it); // strictly single-use",header)
            self.assertIn("TTL_MS = 30000",header)
            self.assertIn("MAX_PENDING = 4096",header)
    def test_unknown_upstream_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)/"src/Network"
            base.mkdir(parents=True)
            (base/"msgaccount.cpp").write_text("unexpected account")
            (base/"msgconnect.cpp").write_text(CONNECT)
            with self.assertRaises(RuntimeError):patch(Path(d))
            self.assertFalse((base/"transfer_tickets.h").exists())
if __name__=="__main__":unittest.main()
