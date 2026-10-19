#include "session_guard.hpp"
#include <limits>

namespace tq {
GuardResult SessionGuard::check(std::uint64_t sequence, std::uint32_t action_type,
                                std::uint64_t now, std::uint64_t cooldown) {
    if (sequence == 0 || action_type == 0) return GuardResult::InvalidAction;
    if (has_clock_ && now < last_clock_) return GuardResult::ClockRollback;
    // Do not consume sequence for rejected actions: caller may choose to retry
    // with a later sequence. This guard is not an authenticated wire protocol.
    if (sequence <= last_sequence_) return GuardResult::Replay;
    has_clock_ = true;
    last_clock_ = now;
    last_sequence_ = sequence;
    const auto found = next_allowed_.find(action_type);
    if (found != next_allowed_.end() && now < found->second)
        return GuardResult::RateLimited;
    // Saturating addition avoids overflow bypass near UINT64_MAX.
    auto allowed = (cooldown > std::numeric_limits<std::uint64_t>::max() - now)
        ? std::numeric_limits<std::uint64_t>::max() : now + cooldown;
    next_allowed_[action_type] = allowed;
    return GuardResult::Allowed;
}
void SessionGuard::reset() { last_sequence_ = 0; last_clock_ = 0; has_clock_ = false; next_allowed_.clear(); }
}
