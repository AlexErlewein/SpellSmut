//! SpellForce Icon Extractor
//!
//! Extracts icons from atlas PNG files and parses MSB files for mapping.
//! Supports both spell icons (4x4 grid, 64px) and item icons (16x16 grid, 16px).

use clap::{Parser, Subcommand, ValueEnum};
use image::{GenericImageView, ImageBuffer, Rgba, RgbaImage};
use rayon::prelude::*;
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

#[derive(Parser)]
#[command(name = "icon-extractor")]
#[command(about = "Extract SpellForce icons from atlas files", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Extract icons from atlas PNG files
    Extract {
        /// Input directory containing atlas PNG files
        #[arg(short, long)]
        input: PathBuf,

        /// Output directory for extracted icons
        #[arg(short, long)]
        output: PathBuf,

        /// Icon type (spell or item)
        #[arg(short = 't', long, value_enum, default_value = "item")]
        icon_type: IconType,

        /// Apply 180-degree rotation (for SpellForce's inverted Y-axis)
        #[arg(long, default_value_t = true)]
        rotate: bool,

        /// Include empty icons (mostly transparent) - by default empty icons are skipped
        #[arg(long, default_value_t = false)]
        include_empty: bool,
    },

    /// Parse MSB files to extract handle-to-atlas mapping
    ParseMsb {
        /// Directory containing MSB files
        #[arg(short, long)]
        input: PathBuf,

        /// Output JSON file for mapping
        #[arg(short, long)]
        output: PathBuf,

        /// Icon type (spell or item)
        #[arg(short = 't', long, value_enum, default_value = "item")]
        icon_type: IconType,
    },

    /// Full extraction: parse MSB + extract icons + generate mapping
    Full {
        /// Directory containing raw extracted assets (with mesh/ and texture/ subdirs)
        #[arg(short, long)]
        input: PathBuf,

        /// Output directory for icons and mapping
        #[arg(short, long)]
        output: PathBuf,

        /// Icon type (spell or item)
        #[arg(short = 't', long, value_enum, default_value = "item")]
        icon_type: IconType,
    },

    /// Extract icons using MSB mapping (proper dimensions for multi-cell icons)
    ExtractMapped {
        /// Directory containing atlas PNG files
        #[arg(short = 'a', long)]
        atlases: PathBuf,

        /// Directory containing MSB files
        #[arg(short, long)]
        msb_dir: PathBuf,

        /// Output directory for extracted icons
        #[arg(short, long)]
        output: PathBuf,

        /// Icon type (spell or item)
        #[arg(short = 't', long, value_enum, default_value = "item")]
        icon_type: IconType,

        /// Also generate mapping JSON
        #[arg(long, default_value_t = true)]
        generate_mapping: bool,
    },
}

#[derive(Clone, Copy, ValueEnum)]
enum IconType {
    Spell,
    Item,
}

impl IconType {
    fn grid_size(&self) -> u32 {
        match self {
            IconType::Spell => 4,
            IconType::Item => 16,
        }
    }

    fn icon_size(&self) -> u32 {
        match self {
            IconType::Spell => 64,
            IconType::Item => 16,
        }
    }

    fn atlas_pattern(&self) -> &'static str {
        match self {
            IconType::Spell => r"(?:ui_spell|_atlas_)(\d+)",
            IconType::Item => r"(?:ui_item|_atlas_)(\d+)",
        }
    }

    fn prefix(&self) -> &'static str {
        match self {
            IconType::Spell => "spell",
            IconType::Item => "itm",
        }
    }

    fn msb_pattern(&self) -> &'static str {
        match self {
            IconType::Spell => "ui_spell_*.msb",
            IconType::Item => "ui_item_*.msb",
        }
    }
}

#[derive(Serialize, Deserialize, Clone)]
struct IconMapping {
    handle: String,
    atlas_number: u32,
    grid_row: u32,
    grid_col: u32,
    icon_index: u32,
    icon_path: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    category: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    subcategory: Option<String>,
    /// Width in grid cells (1 = 16px for items, 64px for spells)
    #[serde(default = "default_one")]
    width_cells: u32,
    /// Height in grid cells
    #[serde(default = "default_one")]
    height_cells: u32,
    /// Pixel coordinates in atlas (for precise extraction)
    #[serde(skip_serializing_if = "Option::is_none")]
    pixel_x: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pixel_y: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pixel_width: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pixel_height: Option<u32>,
}

fn default_one() -> u32 {
    1
}

#[derive(Serialize)]
struct MappingOutput {
    description: String,
    total_mappings: usize,
    atlases_used: Vec<u32>,
    handle_to_path: HashMap<String, String>,
    mappings: HashMap<String, IconMapping>,
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Extract {
            input,
            output,
            icon_type,
            rotate,
            include_empty,
        } => {
            extract_icons(&input, &output, icon_type, rotate, !include_empty);
        }
        Commands::ParseMsb {
            input,
            output,
            icon_type,
        } => {
            parse_msb_files(&input, &output, icon_type);
        }
        Commands::Full {
            input,
            output,
            icon_type,
        } => {
            full_extraction(&input, &output, icon_type);
        }
        Commands::ExtractMapped {
            atlases,
            msb_dir,
            output,
            icon_type,
            generate_mapping,
        } => {
            extract_mapped_icons(&atlases, &msb_dir, &output, icon_type, generate_mapping);
        }
    }
}

fn extract_icons(input: &Path, output: &Path, icon_type: IconType, rotate: bool, skip_empty: bool) {
    let grid_size = icon_type.grid_size();
    let icon_size = icon_type.icon_size();
    let pattern = Regex::new(icon_type.atlas_pattern()).unwrap();
    let prefix = icon_type.prefix();

    println!("Icon Extractor - {} mode", prefix);
    println!("================================");
    println!("Grid: {}x{}, Icon size: {}px", grid_size, grid_size, icon_size);
    println!("Input: {}", input.display());
    println!("Output: {}", output.display());
    println!();

    // Find all PNG files
    let png_files: Vec<PathBuf> = WalkDir::new(input)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| {
            e.path().extension().map_or(false, |ext| ext == "png")
                && pattern.is_match(&e.path().file_stem().unwrap_or_default().to_string_lossy())
        })
        .map(|e| e.path().to_path_buf())
        .collect();

    println!("Found {} atlas files", png_files.len());

    let mut total_icons = 0u32;
    let mut total_skipped = 0u32;

    for atlas_path in &png_files {
        let filename = atlas_path.file_stem().unwrap().to_string_lossy();

        if let Some(caps) = pattern.captures(&filename) {
            let atlas_num: u32 = caps.get(1).unwrap().as_str().parse().unwrap_or(0);

            let atlas_output_dir = output.join(format!("atlas_{}", atlas_num));
            fs::create_dir_all(&atlas_output_dir).ok();

            match image::open(atlas_path) {
                Ok(img) => {
                    let (width, height) = img.dimensions();
                    let rgba_img = img.to_rgba8();

                    let mut extracted = 0u32;
                    let mut skipped = 0u32;

                    for row in 0..grid_size {
                        for col in 0..grid_size {
                            let x = col * icon_size;
                            let y = row * icon_size;

                            if x + icon_size > width || y + icon_size > height {
                                continue;
                            }

                            let mut icon: RgbaImage = ImageBuffer::new(icon_size, icon_size);

                            for iy in 0..icon_size {
                                for ix in 0..icon_size {
                                    let pixel = rgba_img.get_pixel(x + ix, y + iy);
                                    icon.put_pixel(ix, iy, *pixel);
                                }
                            }

                            // Check if icon is empty (mostly transparent)
                            if skip_empty && is_icon_empty(&icon) {
                                skipped += 1;
                                continue;
                            }

                            // Apply 180-degree rotation if needed
                            let final_icon = if rotate {
                                image::imageops::rotate180(&icon)
                            } else {
                                icon
                            };

                            // Calculate icon index (row-major order)
                            let icon_index = row * grid_size + col;
                            let icon_path = atlas_output_dir.join(format!("icon_{:03}.png", icon_index));

                            if let Err(e) = final_icon.save(&icon_path) {
                                eprintln!("Error saving {}: {}", icon_path.display(), e);
                            } else {
                                extracted += 1;
                            }
                        }
                    }

                    total_icons += extracted;
                    total_skipped += skipped;
                    println!(
                        "  Atlas {:3}: extracted {} icons, skipped {} empty",
                        atlas_num, extracted, skipped
                    );
                }
                Err(e) => {
                    eprintln!("Error opening {}: {}", atlas_path.display(), e);
                }
            }
        }
    }

    println!();
    println!("Complete: {} icons extracted, {} empty skipped", total_icons, total_skipped);
}

fn is_icon_empty(img: &RgbaImage) -> bool {
    let mut total_alpha: u64 = 0;
    let pixel_count = (img.width() * img.height()) as u64;

    for pixel in img.pixels() {
        total_alpha += pixel[3] as u64;
    }

    // Consider empty if average alpha is < 10
    (total_alpha / pixel_count) < 10
}

fn parse_msb_files(input: &Path, output: &Path, icon_type: IconType) {
    let grid_size = icon_type.grid_size();
    let atlas_pattern = Regex::new(icon_type.atlas_pattern()).unwrap();
    let prefix = icon_type.prefix();

    println!("MSB Parser - {} mode", prefix);
    println!("================================");

    // Find MSB files
    let msb_pattern = match icon_type {
        IconType::Spell => "ui_spell_",
        IconType::Item => "ui_item_",
    };

    let msb_files: Vec<PathBuf> = WalkDir::new(input)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| {
            let name = e.path().file_name().unwrap_or_default().to_string_lossy();
            name.starts_with(msb_pattern) && name.ends_with(".msb")
        })
        .map(|e| e.path().to_path_buf())
        .collect();

    println!("Found {} MSB files", msb_files.len());

    let mappings: Vec<IconMapping> = msb_files
        .par_iter()
        .filter_map(|msb_path| parse_single_msb(msb_path, &atlas_pattern, grid_size, prefix))
        .collect();

    println!("Parsed {} mappings", mappings.len());

    // Build output structure
    let mut atlases_used: Vec<u32> = mappings.iter().map(|m| m.atlas_number).collect();
    atlases_used.sort();
    atlases_used.dedup();

    let handle_to_path: HashMap<String, String> = mappings
        .iter()
        .map(|m| (m.handle.clone(), m.icon_path.clone()))
        .collect();

    let mappings_map: HashMap<String, IconMapping> = mappings
        .into_iter()
        .map(|m| (m.handle.clone(), m))
        .collect();

    let output_data = MappingOutput {
        description: format!(
            "{} handle to icon mapping extracted from MSB files",
            prefix
        ),
        total_mappings: mappings_map.len(),
        atlases_used,
        handle_to_path,
        mappings: mappings_map,
    };

    // Write JSON
    if let Some(parent) = output.parent() {
        fs::create_dir_all(parent).ok();
    }

    let json = serde_json::to_string_pretty(&output_data).unwrap();
    let mut file = File::create(output).expect("Failed to create output file");
    file.write_all(json.as_bytes()).expect("Failed to write mapping");

    println!("Saved mapping to {}", output.display());
}

fn parse_single_msb(
    msb_path: &Path,
    atlas_pattern: &Regex,
    grid_size: u32,
    prefix: &str,
) -> Option<IconMapping> {
    let mut file = File::open(msb_path).ok()?;
    let mut data = Vec::new();
    file.read_to_end(&mut data).ok()?;

    // Extract handle from filename
    let handle = msb_path.file_stem()?.to_string_lossy().to_string();

    // Find atlas reference in file content
    let content = String::from_utf8_lossy(&data);
    let atlas_num = atlas_pattern
        .captures(&content)?
        .get(1)?
        .as_str()
        .parse::<u32>()
        .ok()?;

    // Extract UV coordinates from known offsets
    // UV offset pairs based on SpellForce MSB structure
    let uv_offsets: [(usize, usize); 4] = [
        (0x2C, 0x30),
        (0x54, 0x58),
        (0x7C, 0x80),
        (0xA4, 0xA8),
    ];

    let mut uvs: Vec<(f32, f32)> = Vec::new();

    for (u_off, v_off) in uv_offsets {
        if v_off + 4 <= data.len() {
            let u = read_f32_le(&data, u_off);
            let v = read_f32_le(&data, v_off);

            if (0.0..=1.0).contains(&u) && (0.0..=1.0).contains(&v) {
                uvs.push((u, v));
            }
        }
    }

    // Calculate grid position and dimensions from UVs
    let (row, col, width_cells, height_cells, pixel_x, pixel_y, pixel_width, pixel_height) = if !uvs.is_empty() {
        let min_u = uvs.iter().map(|(u, _)| *u).fold(f32::MAX, f32::min);
        let min_v = uvs.iter().map(|(_, v)| *v).fold(f32::MAX, f32::min);
        let max_u = uvs.iter().map(|(u, _)| *u).fold(f32::MIN, f32::max);
        let max_v = uvs.iter().map(|(_, v)| *v).fold(f32::MIN, f32::max);

        let col = ((min_u * grid_size as f32) as u32).min(grid_size - 1);
        let row = ((min_v * grid_size as f32) as u32).min(grid_size - 1);

        // Calculate width and height in cells
        let width = ((max_u - min_u) * grid_size as f32).round().max(1.0) as u32;
        let height = ((max_v - min_v) * grid_size as f32).round().max(1.0) as u32;

        // Atlas size is typically 256x256 pixels
        let atlas_size = 256u32;
        let px = (min_u * atlas_size as f32) as u32;
        let py = (min_v * atlas_size as f32) as u32;
        let pw = ((max_u - min_u) * atlas_size as f32) as u32;
        let ph = ((max_v - min_v) * atlas_size as f32) as u32;

        (row, col, width, height, Some(px), Some(py), Some(pw.max(1)), Some(ph.max(1)))
    } else {
        (0, 0, 1, 1, None, None, None, None)
    };

    let icon_index = row * grid_size + col;
    let icon_path = format!("{}/atlas_{}/icon_{:03}.png", prefix, atlas_num, icon_index);

    // Classify item type (for items only)
    let (category, subcategory) = if prefix == "itm" {
        classify_item(&handle)
    } else {
        (None, None)
    };

    Some(IconMapping {
        handle,
        atlas_number: atlas_num,
        grid_row: row,
        grid_col: col,
        icon_index,
        icon_path,
        category,
        subcategory,
        width_cells,
        height_cells,
        pixel_x,
        pixel_y,
        pixel_width,
        pixel_height,
    })
}

fn read_f32_le(data: &[u8], offset: usize) -> f32 {
    if offset + 4 > data.len() {
        return 0.0;
    }
    let bytes: [u8; 4] = [data[offset], data[offset + 1], data[offset + 2], data[offset + 3]];
    f32::from_le_bytes(bytes)
}

fn classify_item(handle: &str) -> (Option<String>, Option<String>) {
    let h = handle.to_lowercase();

    if h.contains("weapon") || h.contains("sword") || h.contains("axe") || h.contains("mace")
        || h.contains("bow") || h.contains("staff") || h.contains("dagger") {
        let sub = if h.contains("sword") {
            "sword"
        } else if h.contains("axe") {
            "axe"
        } else if h.contains("mace") || h.contains("hammer") {
            "mace"
        } else if h.contains("bow") {
            "bow"
        } else if h.contains("crossbow") {
            "crossbow"
        } else if h.contains("staff") {
            "staff"
        } else if h.contains("dagger") {
            "dagger"
        } else {
            "other"
        };
        return (Some("weapon".to_string()), Some(sub.to_string()));
    }

    if h.contains("chest") || h.contains("breastplate") {
        return (Some("armor".to_string()), Some("chest".to_string()));
    }
    if h.contains("helmet") || h.contains("head") {
        return (Some("armor".to_string()), Some("helmet".to_string()));
    }
    if h.contains("leg") || h.contains("pants") {
        return (Some("armor".to_string()), Some("legs".to_string()));
    }
    if h.contains("shield") {
        return (Some("armor".to_string()), Some("shield".to_string()));
    }
    if h.contains("ring") {
        return (Some("accessory".to_string()), Some("ring".to_string()));
    }
    if h.contains("amulet") {
        return (Some("accessory".to_string()), Some("amulet".to_string()));
    }
    if h.contains("rune") {
        return (Some("rune".to_string()), None);
    }
    if h.contains("potion") {
        return (Some("consumable".to_string()), Some("potion".to_string()));
    }
    if h.contains("scroll") {
        return (Some("consumable".to_string()), Some("scroll".to_string()));
    }

    (None, None)
}

fn full_extraction(input: &Path, output: &Path, icon_type: IconType) {
    let prefix = icon_type.prefix();

    println!("Full Extraction - {} mode", prefix);
    println!("================================");
    println!("Input: {}", input.display());
    println!("Output: {}", output.display());
    println!();

    // Find texture directory (for atlas PNGs)
    let texture_dir = find_subdir(input, "texture");

    // Find mesh directory (for MSB files)
    let mesh_dir = find_subdir(input, "mesh");

    if texture_dir.is_none() && mesh_dir.is_none() {
        eprintln!("Error: Could not find texture/ or mesh/ subdirectories");
        eprintln!("Expected structure: input/texture/*.png and input/mesh/*.msb");
        return;
    }

    // Create output directories
    let icons_output = output.join(prefix);
    fs::create_dir_all(&icons_output).ok();

    // Step 1: Extract icons from atlases
    if let Some(tex_dir) = &texture_dir {
        println!("Step 1: Extracting icons from atlases...");
        extract_icons(tex_dir, &icons_output, icon_type, true, true);
        println!();
    } else {
        println!("Warning: No texture directory found, skipping icon extraction");
    }

    // Step 2: Parse MSB files for mapping
    if let Some(msb_dir) = &mesh_dir {
        println!("Step 2: Parsing MSB files for mapping...");
        let mapping_output = output.join(format!("{}_icon_mapping.json", prefix));
        parse_msb_files(msb_dir, &mapping_output, icon_type);
        println!();
    } else {
        println!("Warning: No mesh directory found, skipping MSB parsing");
    }

    println!("Full extraction complete!");
}

fn extract_mapped_icons(
    atlases_dir: &Path,
    msb_dir: &Path,
    output: &Path,
    icon_type: IconType,
    generate_mapping: bool,
) {
    let prefix = icon_type.prefix();
    let atlas_pattern = Regex::new(icon_type.atlas_pattern()).unwrap();
    let grid_size = icon_type.grid_size();

    println!("Mapped Icon Extraction - {} mode", prefix);
    println!("================================");
    println!("Atlases: {}", atlases_dir.display());
    println!("MSB files: {}", msb_dir.display());
    println!("Output: {}", output.display());
    println!();

    // Step 1: Parse all MSB files
    println!("Step 1: Parsing MSB files...");
    let msb_pattern = match icon_type {
        IconType::Spell => "ui_spell_",
        IconType::Item => "ui_item_",
    };

    let msb_files: Vec<PathBuf> = WalkDir::new(msb_dir)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| {
            let name = e.path().file_name().unwrap_or_default().to_string_lossy();
            name.starts_with(msb_pattern) && name.ends_with(".msb")
        })
        .map(|e| e.path().to_path_buf())
        .collect();

    println!("Found {} MSB files", msb_files.len());

    let mappings: Vec<IconMapping> = msb_files
        .par_iter()
        .filter_map(|msb_path| parse_single_msb(msb_path, &atlas_pattern, grid_size, prefix))
        .collect();

    println!("Parsed {} mappings", mappings.len());

    // Step 2: Find all atlas files
    println!("\nStep 2: Loading atlases and extracting icons...");
    // Match various atlas naming patterns: _atlas_X.png, ui_itemX.png, etc.
    let atlas_file_pattern = Regex::new(r"(?:_atlas_|ui_item|ui_spell)(\d+)").unwrap();

    let atlas_files: HashMap<u32, PathBuf> = WalkDir::new(atlases_dir)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.path().extension().map_or(false, |ext| ext == "png"))
        .filter_map(|e| {
            let filename = e.path().file_stem()?.to_string_lossy();
            let caps = atlas_file_pattern.captures(&filename)?;
            let num: u32 = caps.get(1)?.as_str().parse().ok()?;
            Some((num, e.path().to_path_buf()))
        })
        .collect();

    println!("Found {} atlas files", atlas_files.len());

    // Step 3: Extract icons based on mappings
    let icons_output = output.join(prefix);
    fs::create_dir_all(&icons_output).ok();

    let mut extracted = 0u32;
    let mut failed = 0u32;

    // Group mappings by atlas for efficiency
    let mut by_atlas: HashMap<u32, Vec<&IconMapping>> = HashMap::new();
    for mapping in &mappings {
        by_atlas
            .entry(mapping.atlas_number)
            .or_default()
            .push(mapping);
    }

    for (atlas_num, atlas_mappings) in &by_atlas {
        let Some(atlas_path) = atlas_files.get(atlas_num) else {
            eprintln!("Warning: Atlas {} not found", atlas_num);
            failed += atlas_mappings.len() as u32;
            continue;
        };

        let Ok(atlas_img) = image::open(atlas_path) else {
            eprintln!("Error opening atlas {}", atlas_path.display());
            failed += atlas_mappings.len() as u32;
            continue;
        };

        let rgba_atlas = atlas_img.to_rgba8();
        let (atlas_width, atlas_height) = rgba_atlas.dimensions();

        // Create output directory for this atlas
        let atlas_output = icons_output.join(format!("atlas_{}", atlas_num));
        fs::create_dir_all(&atlas_output).ok();

        for mapping in atlas_mappings {
            // Get pixel coordinates (or calculate from grid position)
            let (px, py, pw, ph) = match (
                mapping.pixel_x,
                mapping.pixel_y,
                mapping.pixel_width,
                mapping.pixel_height,
            ) {
                (Some(x), Some(y), Some(w), Some(h)) => (x, y, w, h),
                _ => {
                    // Fallback to grid-based calculation
                    let cell_size = icon_type.icon_size();
                    (
                        mapping.grid_col * cell_size,
                        mapping.grid_row * cell_size,
                        cell_size * mapping.width_cells,
                        cell_size * mapping.height_cells,
                    )
                }
            };

            // Bounds check
            if px + pw > atlas_width || py + ph > atlas_height {
                eprintln!(
                    "Warning: {} out of bounds ({},{} {}x{}) in {}x{} atlas",
                    mapping.handle, px, py, pw, ph, atlas_width, atlas_height
                );
                failed += 1;
                continue;
            }

            // Extract the icon region
            let mut icon: RgbaImage = ImageBuffer::new(pw, ph);
            for iy in 0..ph {
                for ix in 0..pw {
                    let pixel = rgba_atlas.get_pixel(px + ix, py + iy);
                    icon.put_pixel(ix, iy, *pixel);
                }
            }

            // Apply 180-degree rotation (SpellForce icons are stored upside down)
            let rotated = image::imageops::rotate180(&icon);

            // Save with handle-based naming (sanitized)
            let safe_name = mapping
                .handle
                .replace("ui_item_", "")
                .replace("ui_spell_", "");
            let icon_path = atlas_output.join(format!("{}.png", safe_name));

            if let Err(e) = rotated.save(&icon_path) {
                eprintln!("Error saving {}: {}", icon_path.display(), e);
                failed += 1;
            } else {
                extracted += 1;
            }
        }

        println!(
            "  Atlas {:3}: extracted {} icons",
            atlas_num,
            atlas_mappings.len()
        );
    }

    println!("\nExtracted {} icons, {} failed", extracted, failed);

    // Step 4: Generate mapping JSON if requested
    if generate_mapping {
        println!("\nStep 3: Generating mapping JSON...");

        let mut atlases_used: Vec<u32> = mappings.iter().map(|m| m.atlas_number).collect();
        atlases_used.sort();
        atlases_used.dedup();

        // Update paths to use handle-based naming
        let updated_mappings: Vec<IconMapping> = mappings
            .into_iter()
            .map(|mut m| {
                let safe_name = m.handle.replace("ui_item_", "").replace("ui_spell_", "");
                m.icon_path = format!("{}/atlas_{}/{}.png", prefix, m.atlas_number, safe_name);
                m
            })
            .collect();

        let handle_to_path: HashMap<String, String> = updated_mappings
            .iter()
            .map(|m| (m.handle.clone(), m.icon_path.clone()))
            .collect();

        let mappings_map: HashMap<String, IconMapping> = updated_mappings
            .into_iter()
            .map(|m| (m.handle.clone(), m))
            .collect();

        let output_data = MappingOutput {
            description: format!(
                "{} handle to icon mapping with proper dimensions from MSB files",
                prefix
            ),
            total_mappings: mappings_map.len(),
            atlases_used,
            handle_to_path,
            mappings: mappings_map,
        };

        let mapping_path = output.join(format!("{}_icon_mapping.json", prefix));
        let json = serde_json::to_string_pretty(&output_data).unwrap();
        if let Err(e) = fs::write(&mapping_path, json) {
            eprintln!("Error writing mapping: {}", e);
        } else {
            println!("Saved mapping to {}", mapping_path.display());
        }
    }

    println!("\nMapped extraction complete!");
}

fn find_subdir(base: &Path, name: &str) -> Option<PathBuf> {
    // Check direct subdirectory
    let direct = base.join(name);
    if direct.is_dir() {
        return Some(direct);
    }

    // Search in subdirectories (e.g., sf35/texture/)
    for entry in WalkDir::new(base).max_depth(2) {
        if let Ok(e) = entry {
            if e.file_type().is_dir() && e.file_name() == name {
                return Some(e.path().to_path_buf());
            }
        }
    }

    None
}
