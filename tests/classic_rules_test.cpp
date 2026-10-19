#include "classic_rules.hpp"
#include <cassert>
int main() {
  using namespace tq;
  assert(ClassicPolicy::allowed_class(CharacterClass::Trojan));
  assert(ClassicPolicy::allowed_class(CharacterClass::Warrior));
  assert(ClassicPolicy::allowed_class(CharacterClass::Archer));
  assert(ClassicPolicy::allowed_class(CharacterClass::FireTaoist));
  assert(ClassicPolicy::allowed_class(CharacterClass::WaterTaoist));
  assert(!ClassicPolicy::allowed_class(CharacterClass::Ninja));
  assert(!ClassicPolicy::allowed_class(CharacterClass::Monk));
  assert(ClassicPolicy::allowed_rebirth(0));
  assert(!ClassicPolicy::allowed_rebirth(1));
  assert(!ClassicPolicy::allowed_rebirth(-1));
  assert(!ClassicPolicy::shopping_mall_enabled());
  assert(!ClassicPolicy::conquer_points_enabled());
}
