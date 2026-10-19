#pragma once
#include <cstdint>
#include <unordered_map>

namespace tq {
// Protocol independent, per-connection guard. Server supplies monotonic time.
// Not a complete anti-cheat system; checks sequence replay and action cooldowns.
enum class GuardResult { Allowed, Replay, RateLimited, ClockRollback, InvalidAction };
class SessionGuard {
public:
    // action_type and cooldown_ms must come from a trusted server-side policy.
    // Sequence 0 is invalid. Each guard belongs to one authenticated session.
    GuardResult check(std::uint64_t sequence, std::uint32_t action_type,
                      std::uint64_t server_monotonic_ms, std::uint64_t cooldown_ms);
    void reset();
private:
    std::uint64_t last_sequence_ = 0;
    std::uint64_t last_clock_ = 0;
    bool has_clock_ = false;
    std::unordered_map<std::uint32_t, std::uint64_t> next_allowed_;
};
}
