#include "economy_ledger.hpp"
#include <cassert>
#include <cstdint>
#include <limits>
using namespace tq;
int main() {
    EconomyLedger db(":memory:");
    assert(db.ready());
    assert(db.provision_wallet(1,100)); assert(db.provision_wallet(2,50));
    assert(db.provision_item(400,2));
    assert(db.transfer("pay-1",1,2,20)==EconomyResult::applied);
    assert(db.balance(1)==80 && db.balance(2)==70);
    assert(db.transfer("pay-1",1,2,20)==EconomyResult::already_applied);
    assert(db.transfer("pay-1",1,2,21)==EconomyResult::conflict);
    assert(db.transfer("bad",1,2,1000)==EconomyResult::insufficient_funds);
    assert(db.transfer("negative",1,2,-1)==EconomyResult::invalid);
    assert(db.transfer("self",1,1,5)==EconomyResult::invalid);
    assert(db.balance(1)==80 && db.balance(2)==70);
    assert(db.purchase_item("sale-1",1,2,400,30)==EconomyResult::applied);
    assert(db.balance(1)==50 && db.balance(2)==100 && db.item_owner(400)==1);
    assert(db.purchase_item("sale-1",1,2,400,30)==EconomyResult::already_applied);
    assert(db.purchase_item("sale-2",1,2,400,30)==EconomyResult::not_owner);
    assert(db.balance(1)==50 && db.balance(2)==100 && db.item_owner(400)==1);
    assert(db.provision_wallet(3,std::numeric_limits<std::int64_t>::max()));
    assert(db.transfer("overflow",1,3,1)==EconomyResult::invalid);
    assert(db.balance(1)==50);
    assert(db.transfer("missing",1,9,1)==EconomyResult::invalid);
    assert(db.balance(1)==50);
}
