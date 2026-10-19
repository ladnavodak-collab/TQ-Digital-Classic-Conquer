// Standalone QtCore behavioral test for COPS single-process login-transfer tokens.
#include "transfer_tickets.h"
#include <assert.h>
#include <stdio.h>

int main()
{
    TransferTickets& t = TransferTickets::instance();
    int32_t token = 0;
    assert(!t.issue(0, token));
    assert(t.issue(123, token));
    assert(token >= 10000);
    assert(!t.consume(456, token)); // mismatch cannot steal ticket
    assert(t.consume(123, token));
    assert(!t.consume(123, token)); // replay denied

    int32_t oldToken=0, newToken=0;
    assert(t.issue(77,oldToken));
    assert(t.issue(77,newToken));
    assert(oldToken != newToken);
    assert(!t.consume(77,oldToken)); // newer login revokes old ticket
    assert(t.consume(77,newToken));
    assert(!t.consume(77,newToken));
    assert(!t.consume(-1,newToken));
    puts("PASS: ticket issuance, UID binding, revoke and single-use replay rejection");
}
