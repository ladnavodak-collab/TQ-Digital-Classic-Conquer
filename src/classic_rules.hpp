#pragma once
#include <cstdint>
#include <string>
#include <unordered_set>

namespace tq {
enum class ClassId { Trojan, Warrior, Archer, FireTaoist, WaterTaoist, Ninja, Monk, Pirate, DragonWarrior, Windwalker, Unknown };
struct Character { ClassId character_class; unsigned rebirths; };
struct DailyClaim { std::uint64_t character_id; std::string quest_id; std::string date_utc; };
struct DailyClaimHash {
    std::size_t operator()(const DailyClaim& c) const noexcept {
        std::size_t h = std::hash<std::uint64_t>{}(c.character_id);
        h ^= std::hash<std::string>{}(c.quest_id) + 0x9e3779b9 + (h<<6) + (h>>2);
        h ^= std::hash<std::string>{}(c.date_utc) + 0x9e3779b9 + (h<<6) + (h>>2);
        return h;
    }
};
inline bool operator==(const DailyClaim& a, const DailyClaim& b) {
    return a.character_id == b.character_id && a.quest_id == b.quest_id && a.date_utc == b.date_utc;
}
class ClassicRules {
public:
    static bool allowed_class(ClassId id) noexcept;
    static bool can_rebirth(const Character& character) noexcept;
    static bool cps_enabled() noexcept { return false; }
    static bool mall_enabled() noexcept { return false; }
};
// In-memory prototype only. Production claims must be enforced atomically by a database unique constraint.
class DailyQuestClaims {
public:
    bool try_claim(const DailyClaim& claim);
private:
    std::unordered_set<DailyClaim, DailyClaimHash> claimed_;
};
}
