use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Item {
    pub item_id: u32,
    pub name_id: u32,
    pub name: String,
    pub item_type: u8,
    pub item_subtype: u8,
    pub selling_price: u32,
    pub buying_price: u32,
    pub item_set_id: u8,
    pub unit_stats_id: u32,
    pub army_unit_id: u32,
    pub building_id: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Creature {
    pub creature_id: u32,
    pub name_id: u32,
    pub name: String,
    pub description_id: u32,
    pub description: String,
    pub hero_id: u32,
    pub faction: u8,
    pub level: u8,
    pub health: u32,
    pub mana: u32,
    pub experience: u32,
    pub gold: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Weapon {
    pub item_id: u32,
    pub min_damage: u32,
    pub max_damage: u32,
    pub min_range: u32,
    pub max_range: u32,
    pub speed: u32,
    pub weapon_type: u32,
    pub material: u32,
    pub name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Armor {
    pub item_id: u32,
    pub strength: i32,
    pub stamina: i32,
    pub agility: i32,
    pub dexterity: i32,
    pub health: i32,
    pub charisma: i32,
    pub intelligence: i32,
    pub wisdom: i32,
    pub mana: i32,
    pub armor_value: u32,
    pub resist_fire: i32,
    pub resist_ice: i32,
    pub resist_black: i32,
    pub resist_mind: i32,
    pub speed_run: i32,
    pub speed_fight: i32,
    pub speed_cast: i32,
    pub name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemList {
    pub items: Vec<Item>,
    pub count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreatureList {
    pub creatures: Vec<Creature>,
    pub count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WeaponList {
    pub weapons: Vec<Weapon>,
    pub count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ArmorList {
    pub armor: Vec<Armor>,
    pub count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LocalizationData {
    pub strings: std::collections::HashMap<u32, String>,
    pub count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CFFDump {
    pub items: Vec<Item>,
    pub creatures: Vec<Creature>,
    pub weapons: Vec<Weapon>,
    pub armor: Vec<Armor>,
    pub localization: std::collections::HashMap<u32, String>,
    pub item_count: usize,
    pub creature_count: usize,
    pub weapon_count: usize,
    pub armor_count: usize,
    pub localization_count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub query: String,
    pub total: usize,
    pub items: Vec<Item>,
}
