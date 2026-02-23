use std::path::PathBuf;

mod cff_parser;
mod entities;

use cff_parser::CFFParser;
use entities::*;

fn main() {
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 3 {
        println!("Usage: cff-tool <cff_path> <command> [options]");
        println!("Commands:");
        println!("  items              - Extract all items");
        println!("  creatures          - Extract all creatures/NPCs");
        println!("  weapons            - Extract all weapons");
        println!("  armor              - Extract all armor");
        println!("  localization       - Extract all localized strings");
        println!("  dump <category>   - Dump specific category");
        println!("  all                - Extract everything to JSON");
        println!("  search <query>     - Search items by name");
        return;
    }

    let cff_path = PathBuf::from(&args[1]);
    let command = &args[2];

    match command.as_str() {
        "items" => cmd_items(&cff_path),
        "creatures" => cmd_creatures(&cff_path),
        "weapons" => cmd_weapons(&cff_path),
        "armor" => cmd_armor(&cff_path),
        "localization" => cmd_localization(&cff_path),
        "all" => cmd_all(&cff_path),
        "search" => {
            let query = args.get(3).map(|s| s.as_str()).unwrap_or("");
            cmd_search(&cff_path, query);
        }
        "dump" => {
            let category: u16 = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(0);
            cmd_dump(&cff_path, category);
        }
        _ => println!("Unknown command: {}", command),
    }
}

fn cmd_items(cff_path: &PathBuf) {
    println!("Loading items from {:?}", cff_path);
    let mut parser = CFFParser::new(cff_path).expect("Failed to open CFF");
    let items = parser.get_items();

    let result = ItemList {
        items: items.clone(),
        count: items.len(),
    };
    println!("{}", serde_json::to_string_pretty(&result).unwrap());
}

fn cmd_creatures(cff_path: &PathBuf) {
    println!("Loading creatures from {:?}", cff_path);
    let mut parser = CFFParser::new(cff_path).expect("Failed to open CFF");
    let creatures = parser.get_creatures();

    let result = CreatureList {
        creatures: creatures.clone(),
        count: creatures.len(),
    };
    println!("{}", serde_json::to_string_pretty(&result).unwrap());
}

fn cmd_weapons(cff_path: &PathBuf) {
    println!("Loading weapons from {:?}", cff_path);
    let mut parser = CFFParser::new(cff_path).expect("Failed to open CFF");
    let weapons = parser.get_weapons();

    let result = WeaponList {
        weapons: weapons.clone(),
        count: weapons.len(),
    };
    println!("{}", serde_json::to_string_pretty(&result).unwrap());
}

fn cmd_armor(cff_path: &PathBuf) {
    println!("Loading armor from {:?}", cff_path);
    let mut parser = CFFParser::new(cff_path).expect("Failed to open CFF");
    let armor = parser.get_armor();

    let result = ArmorList {
        armor: armor.clone(),
        count: armor.len(),
    };
    println!("{}", serde_json::to_string_pretty(&result).unwrap());
}

fn cmd_localization(cff_path: &PathBuf) {
    println!("Loading localization from {:?}", cff_path);
    let mut parser = CFFParser::new(cff_path).expect("Failed to open CFF");
    let strings = parser.get_localization();

    let result = LocalizationData {
        strings: strings.clone(),
        count: strings.len(),
    };
    println!("{}", serde_json::to_string_pretty(&result).unwrap());
}

fn cmd_all(cff_path: &PathBuf) {
    println!("Loading all data from {:?}", cff_path);
    let mut parser = CFFParser::new(cff_path).expect("Failed to open CFF");

    let items = parser.get_items();
    let creatures = parser.get_creatures();
    let weapons = parser.get_weapons();
    let armor = parser.get_armor();
    let strings = parser.get_localization();

    let result = CFFDump {
        items: items.clone(),
        creatures: creatures.clone(),
        weapons: weapons.clone(),
        armor: armor.clone(),
        localization: strings.clone(),
        item_count: items.len(),
        creature_count: creatures.len(),
        weapon_count: weapons.len(),
        armor_count: armor.len(),
        localization_count: strings.len(),
    };

    println!("{}", serde_json::to_string_pretty(&result).unwrap());
}

fn cmd_search(cff_path: &PathBuf, query: &str) {
    let mut parser = CFFParser::new(cff_path).expect("Failed to open CFF");
    let items = parser.get_items();

    let query_lower = query.to_lowercase();
    let results: Vec<Item> = items
        .iter()
        .filter(|i| i.name.to_lowercase().contains(&query_lower))
        .take(100)
        .cloned()
        .collect();

    let result = SearchResult {
        query: query.to_string(),
        total: results.len(),
        items: results,
    };

    println!("{}", serde_json::to_string_pretty(&result).unwrap());
}

fn cmd_dump(cff_path: &PathBuf, category: u16) {
    let data = cff_parser::dump_category(cff_path, category);

    if let Some(hex) = data {
        println!("Category {}: {} bytes", category, hex.len());
        for (i, chunk) in hex.chunks(16).enumerate() {
            print!("{:04x}: ", i * 16);
            for b in chunk {
                print!("{:02x} ", b);
            }
            println!();
        }
    } else {
        println!("Category {} not found", category);
    }
}
