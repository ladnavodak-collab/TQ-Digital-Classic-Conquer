#include "classic_rules.hpp"
namespace tq {
bool ClassicRules::allowed_class(ClassId id) noexcept {
    switch (id) {
    case ClassId::Trojan:
    case ClassId::Warrior:
    case ClassId::Archer:
    case ClassId::FireTaoist:
    case ClassId::WaterTaoist:
        return true;
    default:
        return false;
    }
}
bool ClassicRules::can_rebirth(const Character& character) noexcept {
    return allowed_class(character.character_class) && character.rebirths == 0;
}
bool DailyQuestClaims::try_claim(const DailyClaim& claim) {
    if (claim.character_id == 0 || claim.quest_id.empty() || claim.date_utc.empty()) return false;
    return claimed_.insert(claim).second;
}
}
