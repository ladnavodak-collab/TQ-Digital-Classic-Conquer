#include "movement_guard.hpp"
#include <algorithm>
#include <cstdint>

namespace tq {
namespace {
bool valid_policy(const MovementPolicy& p) {
    return p.map_width > 0 && p.map_height > 0 && p.max_units_per_second > 0 &&
           p.max_interval_ms > 0 && p.max_interval_ms <= 60000 &&
           p.max_units_per_second <= 1000000u && p.burst_allowance_units <= 1000000u;
}
bool within_bounds(Position pos, const MovementPolicy& p) {
    return pos.map_id != 0 && pos.x >= 0 && pos.y >= 0 &&
           pos.x < p.map_width && pos.y < p.map_height;
}
// Distance squared calculated in 64-bit; int32 coordinates can span more than int32.
std::uint64_t squared_distance(Position a, Position b) {
    const std::int64_t dx = static_cast<std::int64_t>(a.x) - b.x;
    const std::int64_t dy = static_cast<std::int64_t>(a.y) - b.y;
    return static_cast<std::uint64_t>(dx*dx + dy*dy);
}
}
MoveResult MovementGuard::initialize(Position spawn, std::uint64_t now, const MovementPolicy& p) {
    // A failed reinitialization must not retain a previous character session.
    reset();
    if (!valid_policy(p)) return MoveResult::InvalidPolicy;
    if (!within_bounds(spawn, p)) return MoveResult::InvalidCoordinates;
    position_ = spawn;
    timestamp_ms_ = now;
    initialized_ = true;
    return MoveResult::Allowed;
}
MoveResult MovementGuard::move(Position target, std::uint64_t now, const MovementPolicy& p) {
    if (!initialized_) return MoveResult::NotInitialized;
    if (!valid_policy(p)) return MoveResult::InvalidPolicy;
    if (!within_bounds(target, p)) return MoveResult::InvalidCoordinates;
    if (target.map_id != position_.map_id) return MoveResult::WrongMap;
    if (now < timestamp_ms_) return MoveResult::ClockRollback;
    const std::uint64_t elapsed = std::min(now-timestamp_ms_, p.max_interval_ms);
    // Cap elapsed and use integer arithmetic; policy was validated above.
    const std::uint64_t allowed = (static_cast<std::uint64_t>(p.max_units_per_second) * elapsed) / 1000u
        + p.burst_allowance_units;
    if (squared_distance(position_,target) > allowed*allowed) return MoveResult::TooFast;
    position_ = target;
    timestamp_ms_ = now;
    return MoveResult::Allowed;
}
MoveResult MovementGuard::authorized_teleport(Position destination, std::uint64_t now, const MovementPolicy& p) {
    if (!initialized_) return MoveResult::NotInitialized;
    if (!valid_policy(p)) return MoveResult::InvalidPolicy;
    if (!within_bounds(destination,p)) return MoveResult::InvalidCoordinates;
    if (now < timestamp_ms_) return MoveResult::ClockRollback;
    position_ = destination;
    timestamp_ms_ = now;
    return MoveResult::Allowed;
}
void MovementGuard::reset() { initialized_ = false; position_ = {}; timestamp_ms_ = 0; }
}
