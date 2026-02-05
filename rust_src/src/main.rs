use clap::{Parser, Subcommand};
use serde_json;
use std::fs;
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "spellsmut-tools")]
#[command(about = "Fast file handling tools for SpellSmut", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// List files in a directory with optional pattern matching
    List {
        /// Directory to scan
        #[arg(short, long)]
        path: PathBuf,

        /// Optional file extension filter (e.g., "lua", "pak")
        #[arg(short, long)]
        extension: Option<String>,

        /// Output as JSON
        #[arg(long, default_value_t = false)]
        json: bool,
    },

    /// Read a file and output its contents
    Read {
        /// File to read
        #[arg(short, long)]
        path: PathBuf,
    },

    /// Example: echo back input (for testing)
    Echo {
        /// Message to echo
        message: String,
    },
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::List { path, extension, json } => {
            let files = list_files(&path, extension.as_deref());
            if json {
                println!("{}", serde_json::to_string(&files).unwrap());
            } else {
                for file in files {
                    println!("{}", file);
                }
            }
        }
        Commands::Read { path } => {
            match fs::read_to_string(&path) {
                Ok(contents) => print!("{}", contents),
                Err(e) => eprintln!("Error reading file: {}", e),
            }
        }
        Commands::Echo { message } => {
            println!("{}", message);
        }
    }
}

fn list_files(dir: &PathBuf, extension: Option<&str>) -> Vec<String> {
    let mut files = Vec::new();

    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_file() {
                if let Some(ext_filter) = extension {
                    if let Some(ext) = path.extension() {
                        if ext.to_string_lossy().to_lowercase() == ext_filter.to_lowercase() {
                            files.push(path.to_string_lossy().to_string());
                        }
                    }
                } else {
                    files.push(path.to_string_lossy().to_string());
                }
            }
        }
    }

    files.sort();
    files
}
