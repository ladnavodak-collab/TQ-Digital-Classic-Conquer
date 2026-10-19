#pragma once
#include <cstdint>

namespace tq {
// These are server-configured limits, not verified patch-5065 movement figures.
struct Position { std::uint32_t map_id; std::int32_t x; std::int32_t y; };
struct MovementPolicy {
    std::int32_t map_width = 1024;
    std::int32_t map_height = 1024;
    std::uint32_t max_units_per_second = 12;
    std::uint32_t burst_allowance_units = 1;
    std::uint64_t max_interval_ms = 1000;
};
enum class MoveResult { Allowed, NotInitialized, InvalidCoordinates, WrongMap, ClockRollback, TooFast, InvalidPolicy };
// Diagnostic primitive: collision checks, terrain, pathfinding, jump legality,
// authoritative map transitions and packet authentication remain integration tasks.
class MovementGuard {
public:
    MoveResult initialize(Position spawn, std::uint64_t server_monotonic_ms, const MovementPolicy& policy);
    MoveResult move(Position requested, std::uint64_t server_monotonic_ms, const MovementPolicy& policy);
    // This can ONLY be called from a trusted server-side teleport/portal handler.
    MoveResult authorized_teleport(Position destination, std::uint64_t server_monotonic_ms, const MovementPolicy& policy);
    bool initialized() const { return initialized_; }
    Position position() const { return position_; }
    void reset();
private:
    bool initialized_ = false;
    Position position_{};
    std::uint64_t timestamp_ms_ = 0;
};
} // namespace tq
