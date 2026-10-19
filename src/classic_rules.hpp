#pragma once
namespace tq {
enum class CharacterClass { Trojan, Warrior, Archer, FireTaoist, WaterTaoist, Ninja, Monk };
struct ClassicPolicy {
  static bool allowed_class(CharacterClass cls);
  static bool allowed_rebirth(int completed_rebirths);
  static bool shopping_mall_enabled();
  static bool conquer_points_enabled();
};
}
