import tempfile
import unittest
from pathlib import Path
from tools.patch_cops_registration_ticket import patch

CLIENT='''    /** Set the account ID of the client. */
    int32_t mAccountID; //!< the account ID'''
CONSTRUCTOR='''      mAccountID(-1), mAccLvl(0), mFlags(0),'''
GAME='''    client.setAccountID(mInfo->AccountUID);

    switch (status)'''
REGISTER='''#include "msgtalk.h"
    if (isValidString(mInfo->Account))
    {
        if (isValidString(mInfo->Password))
        {
            if (IS_SUCCESS(db.authenticate(client, mInfo->Account, mInfo->Password)) &&
                client.getAccountID() == mInfo->AccountUID)
            {
                if (isValidNameString(mInfo->Name))'''
class RegistrationAuthorizationTests(unittest.TestCase):
    def test_ticket_authorizes_registration_before_database_creation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name,src in [('src/client.h',CLIENT),
                             ('src/client.cpp',CONSTRUCTOR),
                             ('src/Network/msgconnect.cpp',GAME),
                             ('src/Network/msgregister.cpp',REGISTER)]:
                p=root/name
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(src)
            patch(root)
            s=(root/'src/Network/msgregister.cpp').read_text()
            self.assertLess(s.index('hasVerifiedGameTicket()'),s.index('isValidNameString(mInfo->Name)'))
            self.assertNotIn('db.authenticate(',s)
            self.assertIn('client.getPlayer() != nullptr',s)
            self.assertIn('memchr(mInfo->Name, 0',s)
            self.assertIn('memchr(mInfo->Account, 0',s)
            client=(root/'src/client.cpp').read_text()
            self.assertIn('mVerifiedGameTicket(false)',client)
            self.assertIn('client.markGameTicketVerified()', (root/'src/Network/msgconnect.cpp').read_text())
    def test_upstream_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name,src in [('src/client.h','changed'),
                             ('src/client.cpp',CONSTRUCTOR),
                             ('src/Network/msgconnect.cpp',GAME),
                             ('src/Network/msgregister.cpp',REGISTER)]:
                p=root/name
                p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text(src)
            with self.assertRaises(RuntimeError):patch(root)
if __name__=="__main__":unittest.main()
