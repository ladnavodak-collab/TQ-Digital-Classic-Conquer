#include "session_guard.hpp"
#include <cassert>
#include <cstdint>
#include <limits>
int main() {
    using tq::GuardResult;
    tq::SessionGuard g;
    assert(g.check(1,1,1000,500) == GuardResult::Allowed);
    assert(g.check(1,1,1100,500) == GuardResult::Replay);
    assert(g.check(2,1,1100,500) == GuardResult::RateLimited);
    assert(g.check(3,1,1499,500) == GuardResult::RateLimited);
    assert(g.check(4,1,1500,500) == GuardResult::Allowed);
    assert(g.check(5,2,1500,100) == GuardResult::Allowed); // other action
    assert(g.check(6,2,1499,100) == GuardResult::ClockRollback);
    assert(g.check(0,2,1700,100) == GuardResult::InvalidAction);
    assert(g.check(7,0,1700,100) == GuardResult::InvalidAction);
    assert(g.check(7,2,1700,100) == GuardResult::Allowed);
    assert(g.check(8,2,1700,100) == GuardResult::RateLimited);
    g.reset();
    assert(g.check(1,1,0,0) == GuardResult::Allowed);
    assert(g.check(2,1,0,0) == GuardResult::Allowed);
    g.reset();
    const auto max = std::numeric_limits<std::uint64_t>::max();
    assert(g.check(1,1,max-2,100) == GuardResult::Allowed);
    assert(g.check(2,1,max-1,100) == GuardResult::RateLimited);
    assert(g.check(3,1,max,100) == GuardResult::Allowed);
}
