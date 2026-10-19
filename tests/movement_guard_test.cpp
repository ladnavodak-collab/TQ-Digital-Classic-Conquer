#include "movement_guard.hpp"
#include <cassert>
#include <cstdint>
#include <iostream>
using namespace tq;
int main() {
    const MovementPolicy p{200,200,10,1,1000};
    MovementGuard g;
    assert(g.move({1002,1,1},100,p)==MoveResult::NotInitialized);
    assert(g.initialize({1002,20,20},1000,p)==MoveResult::Allowed);
    assert(g.move({1002,25,20},1500,p)==MoveResult::Allowed);
    assert(g.move({1002,45,20},1600,p)==MoveResult::TooFast);
    assert(g.position().x == 25);
    assert(g.move({1003,25,20},1600,p)==MoveResult::WrongMap);
    assert(g.move({1002,-1,20},1600,p)==MoveResult::InvalidCoordinates);
    assert(g.move({1002,25,20},1499,p)==MoveResult::ClockRollback);
    assert(g.authorized_teleport({1003,100,100},2000,p)==MoveResult::Allowed);
    assert(g.move({1003,101,100},2000,p)==MoveResult::Allowed);
    assert(g.move({1003,199,199},3000,p)==MoveResult::TooFast);
    assert(g.move({1003,200,199},3000,p)==MoveResult::InvalidCoordinates);
    assert(g.initialize({0,1,1},3000,p)==MoveResult::InvalidCoordinates);
    assert(g.position().map_id == 1003);
    MovementPolicy invalid=p; invalid.max_units_per_second=1000001;
    assert(g.move({1003,101,100},3001,invalid)==MoveResult::InvalidPolicy);
    // Clock windows are capped; cannot move huge distances after being AFK.
    assert(g.move({1003,130,100},999999999999ULL,p)==MoveResult::TooFast);
    // Invalid policies are rejected consistently by all entry points.
    MovementPolicy enormous=p; enormous.burst_allowance_units=1000001;
    assert(g.authorized_teleport({1003,101,100},999999999999ULL,enormous)==MoveResult::InvalidPolicy);
    assert(g.position().x==101);
    // Failed spawn validation must invalidate an earlier character's movement
    // session, rather than silently keeping that earlier trusted position.
    assert(g.initialize({1002,-1,8},999999999999ULL,p)==MoveResult::InvalidCoordinates);
    assert(!g.initialized());
    assert(g.move({1003,101,100},999999999999ULL,p)==MoveResult::NotInitialized);
    assert(g.initialize({1002,8,8},1000,enormous)==MoveResult::InvalidPolicy);
    assert(!g.initialized());
    assert(g.initialize({1002,8,8},1000,p)==MoveResult::Allowed);
    assert(g.position().map_id==1002 && g.position().x==8 && g.position().y==8);
    g.reset();
    assert(!g.initialized());
    std::cout << "movement guard tests passed\n";
}
