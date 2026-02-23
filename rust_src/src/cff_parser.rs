use std::collections::HashMap;
use std::fs::File;
use std::io::{Read, Seek, SeekFrom};
use std::path::PathBuf;

use crate::entities::*;

pub struct CFFParser {
    file: File,
    english_localization: HashMap<u32, String>,
    table_offsets: HashMap<String, u64>,
}

impl CFFParser {
    pub fn new(path: &PathBuf) -> Result<Self, String> {
        let mut file = File::open(path).map_err(|e| format!("Failed to open file: {}", e))?;
        let file_size = file
            .metadata()
            .map_err(|e| format!("Failed to get file size: {}", e))?
            .len();

        let mut header = [0u8; 20];
        file.read_exact(&mut header)
            .map_err(|e| format!("Failed to read header: {}", e))?;

        let mut parser = Self {
            file,
            english_localization: HashMap::new(),
            table_offsets: HashMap::new(),
        };

        parser.build_table_offsets()?;

        Ok(parser)
    }

    fn build_table_offsets(&mut self) -> Result<(), String> {
        let table_names = [
            "spells",
            "spell_names",
            "unknown3",
            "creature_stats",
            "creature_skills",
            "hero_spells",
            "items",
            "armor",
            "item_installs",
            "weapons",
            "item_requirements",
            "item_effects",
            "item_ui",
            "spell_effects",
            "localisation",
            "races",
            "heads",
            "creatures",
            "creature_equipment",
            "creature_spells",
            "creature_resources",
            "drops",
            "unit_building_requirements",
            "buildings",
            "building_graphics",
            "building_requirements",
            "skills",
            "skill_requirements",
            "merchant_inventories",
            "merchant_inventory_items",
            "merchant_price_multipliers",
            "resource_names",
            "levels",
            "objects",
            "object_graphics",
            "object_loot",
            "npc_names",
            "maps",
            "portals",
            "unknown40",
            "descriptions",
            "advanced_descriptions",
            "quests",
            "weapon_type_names",
            "weapon_material_names",
            "terrain",
            "unknown47",
            "upgrades",
            "item_sets",
        ];

        let mut offset: u64 = 20;

        for table_name in table_names {
            self.file
                .seek(SeekFrom::Start(offset))
                .map_err(|e| e.to_string())?;
            let mut header = [0u8; 12];
            self.file
                .read_exact(&mut header)
                .map_err(|e| e.to_string())?;

            let table_size =
                u32::from_le_bytes([header[6], header[7], header[8], header[9]]) as u64;
            offset += 12;
            self.table_offsets.insert(table_name.to_string(), offset);
            offset += table_size;
        }

        println!("Parsed {} table offsets", self.table_offsets.len());
        Ok(())
    }

    pub fn get_creatures(&mut self) -> Vec<Creature> {
        let localization = self.get_localization();

        let offset = match self.table_offsets.get("creatures") {
            Some(o) => *o,
            None => return Vec::new(),
        };

        if self.file.seek(SeekFrom::Start(offset - 12)).is_err() {
            return Vec::new();
        }

        let mut header = [0u8; 12];
        if self.file.read_exact(&mut header).is_err() {
            return Vec::new();
        }

        let table_size = u32::from_le_bytes([header[6], header[7], header[8], header[9]]) as usize;
        let record_size = 64usize;
        let num_creatures = table_size / record_size;

        println!(
            "Found {} creatures (table size: {})",
            num_creatures, table_size
        );

        let mut data = vec![0u8; table_size];
        if self.file.read_exact(&mut data).is_err() {
            return Vec::new();
        }

        let mut creatures = Vec::new();
        for i in 0..num_creatures {
            let off = i * record_size;
            if off + record_size > data.len() {
                break;
            }
            if let Some(creature) = parse_creature(&data[off..off + record_size], &localization) {
                creatures.push(creature);
            }
        }

        creatures
    }

    pub fn get_items(&mut self) -> Vec<Item> {
        let localization = self.get_localization();

        let offset = match self.table_offsets.get("items") {
            Some(o) => *o,
            None => return Vec::new(),
        };

        if self.file.seek(SeekFrom::Start(offset - 12)).is_err() {
            return Vec::new();
        }

        let mut header = [0u8; 12];
        if self.file.read_exact(&mut header).is_err() {
            return Vec::new();
        }

        let table_size = u32::from_le_bytes([header[6], header[7], header[8], header[9]]) as usize;
        let record_size = 22usize;
        let num_items = table_size / record_size;

        println!("Found {} items (table size: {})", num_items, table_size);

        let mut data = vec![0u8; table_size];
        if self.file.read_exact(&mut data).is_err() {
            return Vec::new();
        }

        let mut items = Vec::new();
        for i in 0..num_items {
            let off = i * record_size;
            if off + record_size > data.len() {
                break;
            }
            if let Some(item) = parse_item(&data[off..off + record_size], &localization) {
                items.push(item);
            }
        }

        items
    }

    pub fn get_weapons(&mut self) -> Vec<Weapon> {
        let localization = self.get_localization();

        let offset = match self.table_offsets.get("weapons") {
            Some(o) => *o,
            None => return Vec::new(),
        };

        if self.file.seek(SeekFrom::Start(offset - 12)).is_err() {
            return Vec::new();
        }

        let mut header = [0u8; 12];
        if self.file.read_exact(&mut header).is_err() {
            return Vec::new();
        }

        let table_size = u32::from_le_bytes([header[6], header[7], header[8], header[9]]) as usize;
        let record_size = 16usize;
        let num_weapons = table_size / record_size;

        println!("Found {} weapons (table size: {})", num_weapons, table_size);

        let mut data = vec![0u8; table_size];
        if self.file.read_exact(&mut data).is_err() {
            return Vec::new();
        }

        let mut weapons = Vec::new();
        for i in 0..num_weapons {
            let off = i * record_size;
            if off + record_size > data.len() {
                break;
            }
            if let Some(weapon) = parse_weapon(&data[off..off + record_size], &localization) {
                weapons.push(weapon);
            }
        }

        weapons
    }

    pub fn get_armor(&mut self) -> Vec<Armor> {
        let localization = self.get_localization();

        let offset = match self.table_offsets.get("armor") {
            Some(o) => *o,
            None => return Vec::new(),
        };

        if self.file.seek(SeekFrom::Start(offset - 12)).is_err() {
            return Vec::new();
        }

        let mut header = [0u8; 12];
        if self.file.read_exact(&mut header).is_err() {
            return Vec::new();
        }

        let table_size = u32::from_le_bytes([header[6], header[7], header[8], header[9]]) as usize;
        let record_size = 36usize;
        let num_armor = table_size / record_size;

        println!("Found {} armor (table size: {})", num_armor, table_size);

        let mut data = vec![0u8; table_size];
        if self.file.read_exact(&mut data).is_err() {
            return Vec::new();
        }

        let mut armor_list = Vec::new();
        for i in 0..num_armor {
            let off = i * record_size;
            if off + record_size > data.len() {
                break;
            }
            if let Some(armor_item) = parse_armor(&data[off..off + record_size], &localization) {
                armor_list.push(armor_item);
            }
        }

        armor_list
    }

    pub fn get_localization(&mut self) -> HashMap<u32, String> {
        if !self.english_localization.is_empty() {
            return self.english_localization.clone();
        }

        let offset = match self.table_offsets.get("localisation") {
            Some(o) => *o,
            None => return HashMap::new(),
        };

        if self.file.seek(SeekFrom::Start(offset - 12)).is_err() {
            return HashMap::new();
        }

        let mut header = [0u8; 12];
        if self.file.read_exact(&mut header).is_err() {
            return HashMap::new();
        }

        let table_size = u32::from_le_bytes([header[6], header[7], header[8], header[9]]) as usize;

        println!("Localization table size: {} bytes", table_size);

        let mut data = vec![0u8; table_size];
        if self.file.read_exact(&mut data).is_err() {
            return HashMap::new();
        }

        let record_size = 566usize;
        let num_entries = table_size / record_size;

        println!("Parsing {} localization entries", num_entries);

        let mut off = 0;
        let mut count = 0;
        for _ in 0..num_entries {
            if off + record_size > data.len() {
                break;
            }

            let text_id = u16::from_le_bytes([data[off], data[off + 1]]) as u32;
            let language = data[off + 2];

            if language == 1 {
                let text_start = off + 54;
                let text_end = text_start + 512;
                if text_end <= data.len() {
                    let text_bytes = &data[text_start..text_end];
                    let null_pos = text_bytes
                        .iter()
                        .position(|&b| b == 0)
                        .unwrap_or(text_bytes.len());
                    let text_slice = &text_bytes[..null_pos];

                    let text = text_slice
                        .iter()
                        .filter_map(|&b| Some(char::from(b)))
                        .collect::<String>();

                    if !text.is_empty() {
                        self.english_localization.insert(text_id, text);
                        count += 1;
                    }
                }
            }

            off += record_size;
        }

        println!("Loaded {} English localization strings", count);
        self.english_localization.clone()
    }
}

fn parse_creature(data: &[u8], localization: &HashMap<u32, String>) -> Option<Creature> {
    if data.len() < 64 {
        return None;
    }

    let creature_id = u16::from_le_bytes([data[0], data[1]]) as u32;
    if creature_id == 0 || creature_id > 30000 {
        return None;
    }

    let name_id = u16::from_le_bytes([data[2], data[3]]) as u32;

    let name = localization
        .get(&name_id)
        .cloned()
        .unwrap_or_else(|| format!("Creature {}", creature_id));

    Some(Creature {
        creature_id,
        name_id,
        name,
        description_id: 0,
        description: String::new(),
        hero_id: 0,
        faction: 0,
        level: 0,
        health: 0,
        mana: 0,
        experience: 0,
        gold: 0,
    })
}

fn parse_item(data: &[u8], localization: &HashMap<u32, String>) -> Option<Item> {
    if data.len() < 22 {
        return None;
    }

    let item_id = u16::from_le_bytes([data[0], data[1]]) as u32;
    if item_id == 0 {
        return None;
    }

    let name_id = u16::from_le_bytes([data[4], data[5]]) as u32;

    let name = localization
        .get(&name_id)
        .cloned()
        .unwrap_or_else(|| format!("Item {}", item_id));

    Some(Item {
        item_id,
        name_id,
        name,
        item_type: data[2],
        item_subtype: data[3],
        selling_price: u32::from_le_bytes([data[13], data[14], data[15], data[16]]),
        buying_price: u32::from_le_bytes([data[17], data[18], data[19], data[20]]),
        item_set_id: data[21],
        unit_stats_id: u16::from_le_bytes([data[6], data[7]]) as u32,
        army_unit_id: u16::from_le_bytes([data[8], data[9]]) as u32,
        building_id: u16::from_le_bytes([data[10], data[11]]) as u32,
    })
}

fn parse_weapon(data: &[u8], localization: &HashMap<u32, String>) -> Option<Weapon> {
    if data.len() < 16 {
        return None;
    }

    let item_id = u16::from_le_bytes([data[0], data[1]]) as u32;
    if item_id == 0 {
        return None;
    }

    let name = localization
        .get(&item_id)
        .cloned()
        .unwrap_or_else(|| format!("Weapon {}", item_id));

    Some(Weapon {
        item_id,
        min_damage: u16::from_le_bytes([data[2], data[3]]) as u32,
        max_damage: u16::from_le_bytes([data[4], data[5]]) as u32,
        min_range: u16::from_le_bytes([data[6], data[7]]) as u32,
        max_range: u16::from_le_bytes([data[8], data[9]]) as u32,
        speed: u16::from_le_bytes([data[10], data[11]]) as u32,
        weapon_type: u16::from_le_bytes([data[12], data[13]]) as u32,
        material: u16::from_le_bytes([data[14], data[15]]) as u32,
        name,
    })
}

fn parse_armor(data: &[u8], localization: &HashMap<u32, String>) -> Option<Armor> {
    if data.len() < 36 {
        return None;
    }

    let item_id = u16::from_le_bytes([data[0], data[1]]) as u32;
    if item_id == 0 {
        return None;
    }

    let name = localization
        .get(&item_id)
        .cloned()
        .unwrap_or_else(|| format!("Armor {}", item_id));

    Some(Armor {
        item_id,
        strength: i16::from_le_bytes([data[2], data[3]]) as i32,
        stamina: i16::from_le_bytes([data[4], data[5]]) as i32,
        agility: i16::from_le_bytes([data[6], data[7]]) as i32,
        dexterity: i16::from_le_bytes([data[8], data[9]]) as i32,
        health: i16::from_le_bytes([data[10], data[11]]) as i32,
        charisma: i16::from_le_bytes([data[12], data[13]]) as i32,
        intelligence: i16::from_le_bytes([data[14], data[15]]) as i32,
        wisdom: i16::from_le_bytes([data[16], data[17]]) as i32,
        mana: i16::from_le_bytes([data[18], data[19]]) as i32,
        armor_value: u16::from_le_bytes([data[20], data[21]]) as u32,
        resist_fire: i16::from_le_bytes([data[22], data[23]]) as i32,
        resist_ice: i16::from_le_bytes([data[24], data[25]]) as i32,
        resist_black: i16::from_le_bytes([data[26], data[27]]) as i32,
        resist_mind: i16::from_le_bytes([data[28], data[29]]) as i32,
        speed_run: i16::from_le_bytes([data[30], data[31]]) as i32,
        speed_fight: i16::from_le_bytes([data[32], data[33]]) as i32,
        speed_cast: i16::from_le_bytes([data[34], data[35]]) as i32,
        name,
    })
}

pub fn dump_category(_path: &PathBuf, _category_id: u16) -> Option<Vec<u8>> {
    None
}
