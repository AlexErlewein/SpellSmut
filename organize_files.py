
import os
import sys
from collections import defaultdict
from pathlib import Path

def group_and_move_files(directory_path):
    target_path = Path(directory_path)
    
    if not target_path.is_dir():
        print(f"Error: Directory '{directory_path}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        files = [f for f in target_path.iterdir() if f.is_file() and '_' in f.name]
    except Exception as e:
        print(f"Error listing files: {e}", file=sys.stderr)
        return

    grouped_files = defaultdict(list)
    for f in files:
        first_word = f.stem.split('_')[0]
        grouped_files[first_word].append(f)
    
    commands = []
    for first_word, file_list in grouped_files.items():
        if len(file_list) > 0:
            folder_path = target_path / first_word
            commands.append(f'if not exist "{folder_path}" mkdir "{folder_path}"')
            
            for f_to_move in file_list:
                commands.append(f'move "{f_to_move}" "{folder_path}"')
    
    for cmd in commands:
        print(cmd)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python organize_files.py <directory_path>", file=sys.stderr)
        sys.exit(1)
    
    target_directory = sys.argv[1]
    group_and_move_files(target_directory)
