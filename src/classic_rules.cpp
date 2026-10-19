#include "classic_rules.hpp"
namespace tq {
bool ClassicPolicy::allowed_class(CharacterClass cls) {
  switch(cls) {
    case CharacterClass::Trojan:
    case CharacterClass::Warrior:
    case CharacterClass::Archer:
    case CharacterClass::FireTaoist:
    case CharacterClass::WaterTaoist: return true;
    default: return false;
  }
}
bool ClassicPolicy::allowed_rebirth(int completed_rebirths) { return completed_rebirths >= 0 && completed_rebirths < 1; }
bool ClassicPolicy::shopping_mall_enabled() { return false; }
bool ClassicPolicy::conquer_points_enabled() { return false; }
}
