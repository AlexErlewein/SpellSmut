use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufReader, Read, Seek, SeekFrom};
use std::path::PathBuf;

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
pub struct ItemList {
    pub items: Vec<Item>,
    pub count: usize,
}

fn read_u16<R: Read>(reader: &mut R) -> u16 {
    let mut buf = [0u8; 2];
    reader.read_exact(&mut buf).unwrap();
    u16::from_le_bytes(buf)
}

fn read_u32<R: Read>(reader: &mut R) -> u32 {
    let mut buf = [0u8; 4];
    reader.read_exact(&mut buf).unwrap();
    u32::from_le_bytes(buf)
}

fn read_u8<R: Read>(reader: &mut R) -> u8 {
    let mut buf = [0u8; 1];
    reader.read_exact(&mut buf).unwrap();
    buf[0]
}

// Offsets from Python GameData structure (GameData154)
// These are for the table bodies, not the category chunks
const OFFSET_ITEMS: u64 = 0x6359e + 12; // +12 for table header
const OFFSET_LOCALIZATION: u64 = 0x12d177 + 12; // +12 for table header

// More accurate - try to find by searching for item patterns
fn find_items_offset(cff_path: &PathBuf) -> Option<u64> {
    let mut file = match File::open(cff_path) {
        Ok(f) => f,
        Err(_) => return None,
    };

    let file_size = file.metadata().unwrap().len();
    let mut buffer = vec![0u8; 1024 * 1024]; // 1MB buffer

    // Search for category header pattern: 0xC3 0x07 (2003 in little endian) followed by type
    // Search in chunks
    let mut pos: u64 = 0;
    while pos < file_size - 100 {
        let read_size = std::cmp::min(buffer.len(), (file_size - pos) as usize);
        use std::io::Read;
        match file.read(&mut buffer[..read_size]) {
            Ok(0) => break,
            Ok(n) => {
                for i in 0..n - 10 {
                    // Look for category 2003 (0xC3 0x07 in little endian)
                    if buffer[i] == 0xC3 && buffer[i + 1] == 0x07 {
                        // Check if this looks like a category header
                        let cat_type = u16::from_le_bytes([buffer[i + 2], buffer[i + 3]]);
                        if cat_type == 4 {
                            // category type 4
                            let item_count = u32::from_le_bytes([
                                buffer[i + 4],
                                buffer[i + 5],
                                buffer[i + 6],
                                buffer[i + 7],
                            ]);
                            if item_count > 100 && item_count < 100000 {
                                println!(
                                    "Found potential items category at offset {}, count: {}",
                                    pos + i as u64,
                                    item_count
                                );
                                return Some(pos + i as u64);
                            }
                        }
                    }
                }
                pos += n as u64 - 10;
                use std::io::Seek;
                let _ = file.seek(std::io::SeekFrom::Current(-10));
            }
            Err(_) => break,
        }
    }

    None
}

fn load_items_at_offset(cff_path: &PathBuf, offset: u64) -> Vec<Item> {
    let file = match File::open(cff_path) {
        Ok(f) => f,
        Err(e) => {
            println!("Failed to open file: {}", e);
            return vec![];
        }
    };
    let mut reader = BufReader::new(file);

    if reader.seek(SeekFrom::Start(offset)).is_err() {
        println!("Failed to seek to items offset {:x}", offset);
        return vec![];
    }

    // Skip 12-byte header
    let _header = read_u32(&mut reader); // category id
    let _type = read_u16(&mut reader); // category type
    let _reserved = read_u16(&mut reader); // reserved
    let table_size = read_u32(&mut reader); // size in bytes

    // Each item record is 26 bytes
    let record_size: u32 = 26;
    let item_count = table_size / record_size;

    println!(
        "Found {} items (table size: {} bytes) at offset {:x}",
        item_count, table_size, offset
    );

    let mut items = Vec::new();

    for _ in 0..item_count {
        let item_id = read_u16(&mut reader) as u32;
        let item_type1 = read_u8(&mut reader);
        let item_type2 = read_u8(&mut reader);
        let name_id = read_u16(&mut reader) as u32;
        let unit_stats_id = read_u16(&mut reader) as u32;
        let army_unit_id = read_u16(&mut reader) as u32;
        let building_id = read_u16(&mut reader) as u32;
        let _option = read_u8(&mut reader);
        let _padding = read_u8(&mut reader);
        let sell_value = read_u32(&mut reader);
        let buy_value = read_u32(&mut reader);
        let item_set_id = read_u8(&mut reader);

        items.push(Item {
            item_id,
            name_id,
            name: format!("Item {}", item_id),
            item_type: item_type1,
            item_subtype: item_type2,
            selling_price: sell_value,
            buying_price: buy_value,
            item_set_id,
            unit_stats_id,
            army_unit_id,
            building_id,
        });
    }

    items
}

fn load_localization_at_offset(cff_path: &PathBuf, offset: u64) -> HashMap<u32, String> {
    let file = match File::open(cff_path) {
        Ok(f) => f,
        Err(_) => return HashMap::new(),
    };
    let mut reader = BufReader::new(file);

    if reader.seek(SeekFrom::Start(offset)).is_err() {
        println!("Failed to seek to localization offset {:x}", offset);
        return HashMap::new();
    }

    let item_count = read_u32(&mut reader);
    println!("Loading {} text strings", item_count);

    let mut strings = HashMap::new();

    for _ in 0..item_count.min(100000) {
        let text_id = read_u32(&mut reader);
        let text_len = read_u16(&mut reader) as usize;

        if text_len == 0 || text_len > 1000 {
            continue;
        }

        let mut text_buf = vec![0u8; text_len * 2];
        if reader.read_exact(&mut text_buf).is_err() {
            break;
        }

        let text: String = text_buf
            .chunks(2)
            .filter_map(|c| {
                if c.len() == 2 {
                    Some(u16::from_le_bytes([c[0], c[1]]))
                } else {
                    None
                }
            })
            .take(text_len)
            .filter_map(|c| char::from_u32(c as u32))
            .collect();

        if !text.is_empty() {
            strings.insert(text_id, text);
        }
    }

    strings
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub items: Vec<Item>,
    pub total: usize,
    pub query: String,
}

fn main() {
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        println!("Usage: item-loader <cff_path> [search_query]");
        return;
    }

    let cff_path = PathBuf::from(&args[1]);

    println!("Loading items from {:?}", cff_path);

    // Try to find items offset dynamically
    let items_offset = find_items_offset(&cff_path);
    let actual_offset = items_offset.unwrap_or(OFFSET_ITEMS);

    println!("Using items offset: {:x}", actual_offset);

    let items = load_items_at_offset(&cff_path, actual_offset);
    let localization = load_localization_at_offset(&cff_path, OFFSET_LOCALIZATION);

    let mut named_items = items;
    for item in &mut named_items {
        if let Some(name) = localization.get(&item.name_id) {
            if !name.is_empty() {
                item.name = name.clone();
            }
        }
    }

    if args.len() >= 3 {
        let query = args[2].to_lowercase();
        let filtered: Vec<Item> = named_items
            .iter()
            .filter(|i| {
                i.name.to_lowercase().contains(&query) || i.item_id.to_string().contains(&query)
            })
            .take(100)
            .cloned()
            .collect();

        let result = SearchResult {
            total: filtered.len(),
            query: query.clone(),
            items: filtered,
        };

        println!("{}", serde_json::to_string(&result).unwrap());
    } else {
        let result = ItemList {
            count: named_items.len(),
            items: named_items,
        };

        println!("{}", serde_json::to_string(&result).unwrap());
    }
}
