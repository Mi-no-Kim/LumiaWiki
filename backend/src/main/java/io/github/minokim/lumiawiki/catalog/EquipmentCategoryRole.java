package io.github.minokim.lumiawiki.catalog;

enum EquipmentCategoryRole {
  ROOT,
  WEAPON,
  CHEST,
  HEAD,
  ACCESSORY,
  LEG;

  static EquipmentCategoryRole forEquipmentBranch(String name, ItemCategory parent) {
    if (parent == null || parent.getEquipmentRole() != ROOT) return null;
    return switch (name) {
      case "무기" -> WEAPON;
      case "옷" -> CHEST;
      case "머리" -> HEAD;
      case "장식", "팔" -> ACCESSORY;
      case "다리" -> LEG;
      default -> null;
    };
  }

  EquipmentSlot slot() {
    return this == ROOT ? null : EquipmentSlot.valueOf(name());
  }
}
