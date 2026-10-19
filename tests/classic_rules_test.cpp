#include "classic_rules.hpp"
#include <cassert>
#include <iostream>
int main() {
    using namespace tq;
    for (auto id : {ClassId::Trojan, ClassId::Warrior, ClassId::Archer, ClassId::FireTaoist, ClassId::WaterTaoist}) {
        assert(ClassicRules::allowed_class(id));
        assert(ClassicRules::can_rebirth({id, 0}));
        assert(!ClassicRules::can_rebirth({id, 1}));
        assert(!ClassicRules::can_rebirth({id, 2}));
    }
    for (auto id : {ClassId::Ninja, ClassId::Monk, ClassId::Pirate, ClassId::DragonWarrior, ClassId::Windwalker, ClassId::Unknown}) {
        assert(!ClassicRules::allowed_class(id));
        assert(!ClassicRules::can_rebirth({id, 0}));
    }
    assert(!ClassicRules::cps_enabled());
    assert(!ClassicRules::mall_enabled());
    DailyQuestClaims claims;
    assert(claims.try_claim({42, "daily_hunt", "2026-10-19"}));
    assert(!claims.try_claim({42, "daily_hunt", "2026-10-19"}));
    assert(claims.try_claim({42, "daily_hunt", "2026-10-20"}));
    assert(claims.try_claim({43, "daily_hunt", "2026-10-19"}));
    assert(claims.try_claim({42, "daily_delivery", "2026-10-19"}));
    assert(!claims.try_claim({0, "daily_hunt", "2026-10-19"}));
    std::cout << "Classic rules tests passed\n";
}
