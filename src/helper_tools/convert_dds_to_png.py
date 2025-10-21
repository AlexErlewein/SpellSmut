#!/usr/bin/env python3
"""
DDS to PNG Converter for SpellForce Texture Files

Converts DirectDraw Surface (.dds) texture files to PNG format for easier viewing and editing.
Supports both individual file conversion and batch processing of entire directories.

Usage:
    python convert_dds_to_png.py <input_path> [output_path]

    input_path:  Path to a .dds file or directory containing .dds files
    output_path: Optional output directory (defaults to same location with _png suffix)

Examples:
    # Convert single file
    python convert_dds_to_png.py texture.dds

    # Convert entire directory
    python convert_dds_to_png.py ExtractedAssets/Textures

    # Convert to specific output directory
    python convert_dds_to_png.py ExtractedAssets/Textures ConvertedTextures
"""

import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
import argparse

# Try to import PIL/Pillow
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("WARNING: Pillow not installed. Install with: pip install Pillow")


class DDSConverter:
    """Converts DDS files to PNG format"""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

    def log(self, message: str, level: str = 'INFO'):
        """Print log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[{level}] {message}")

    def convert_file(self, dds_path: Path, output_path: Path, overwrite: bool = False) -> bool:
        """
        Convert a single DDS file to PNG

        Args:
            dds_path: Path to input DDS file
            output_path: Path to output PNG file
            overwrite: Whether to overwrite existing files

        Returns:
            True if conversion successful, False otherwise
        """
        if not PIL_AVAILABLE:
            self.log("Pillow library not available", "ERROR")
            return False

        if not dds_path.exists():
            self.log(f"File not found: {dds_path}", "ERROR")
            return False

        if output_path.exists() and not overwrite:
            self.log(f"Skipping existing file: {output_path}", "SKIP")
            self.stats['skipped'] += 1
            return True

        try:
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Open and convert DDS file
            with Image.open(dds_path) as img:
                # Convert to RGB/RGBA if needed
                if img.mode not in ('RGB', 'RGBA', 'L', 'LA'):
                    if 'A' in img.mode or img.mode == 'RGBA':
                        img = img.convert('RGBA')
                    else:
                        img = img.convert('RGB')

                # Save as PNG
                img.save(output_path, 'PNG', optimize=True)

            self.log(f"Converted: {dds_path.name} -> {output_path.name}", "SUCCESS")
            self.stats['success'] += 1
            return True

        except Exception as e:
            self.log(f"Failed to convert {dds_path.name}: {str(e)}", "ERROR")
            self.stats['failed'] += 1
            return False

    def convert_directory(self, input_dir: Path, output_dir: Path,
                         recursive: bool = True, overwrite: bool = False) -> None:
        """
        Convert all DDS files in a directory

        Args:
            input_dir: Input directory containing DDS files
            output_dir: Output directory for PNG files
            recursive: Whether to process subdirectories
            overwrite: Whether to overwrite existing files
        """
        if not input_dir.exists() or not input_dir.is_dir():
            self.log(f"Directory not found: {input_dir}", "ERROR")
            return

        # Find all DDS files
        pattern = '**/*.dds' if recursive else '*.dds'
        dds_files = list(input_dir.glob(pattern))

        if not dds_files:
            self.log(f"No DDS files found in {input_dir}", "WARNING")
            return

        self.log(f"Found {len(dds_files)} DDS files to convert", "INFO")
        self.stats['total'] = len(dds_files)

        # Convert each file
        for i, dds_path in enumerate(dds_files, 1):
            # Calculate relative path to preserve directory structure
            rel_path = dds_path.relative_to(input_dir)
            output_path = output_dir / rel_path.with_suffix('.png')

            if self.verbose:
                print(f"\n[{i}/{len(dds_files)}] Processing: {rel_path}")

            self.convert_file(dds_path, output_path, overwrite)

    def print_summary(self):
        """Print conversion statistics"""
        print("\n" + "="*60)
        print("CONVERSION SUMMARY")
        print("="*60)
        print(f"Total files:     {self.stats['total']}")
        print(f"Successful:      {self.stats['success']} ✓")
        print(f"Failed:          {self.stats['failed']} ✗")
        print(f"Skipped:         {self.stats['skipped']} -")
        print("="*60)


def main():
    parser = argparse.ArgumentParser(
        description='Convert DDS texture files to PNG format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s texture.dds
  %(prog)s ExtractedAssets/Textures
  %(prog)s ExtractedAssets/Textures ConvertedTextures
  %(prog)s input.dds -o output.png --overwrite
        """
    )

    parser.add_argument('input', type=str,
                       help='Input DDS file or directory')
    parser.add_argument('output', type=str, nargs='?',
                       help='Output PNG file or directory (optional)')
    parser.add_argument('-o', '--output-path', type=str, dest='output_alt',
                       help='Alternative way to specify output path')
    parser.add_argument('-r', '--recursive', action='store_true', default=True,
                       help='Process subdirectories (default: True)')
    parser.add_argument('--no-recursive', action='store_false', dest='recursive',
                       help='Do not process subdirectories')
    parser.add_argument('--overwrite', action='store_true',
                       help='Overwrite existing PNG files')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Quiet mode (minimal output)')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    args = parser.parse_args()

    # Check if PIL is available
    if not PIL_AVAILABLE:
        print("ERROR: Pillow library is required for DDS conversion")
        print("Install it with: pip install Pillow")
        sys.exit(1)

    # Determine input path
    input_path = Path(args.input)

    if not input_path.exists():
        print(f"ERROR: Input path does not exist: {input_path}")
        sys.exit(1)

    # Determine output path
    output_path = args.output or args.output_alt

    if output_path:
        output_path = Path(output_path)
    else:
        # Auto-generate output path
        if input_path.is_file():
            output_path = input_path.with_suffix('.png')
        else:
            output_path = input_path.parent / f"{input_path.name}_png"

    # Create converter instance
    converter = DDSConverter(verbose=not args.quiet)

    # Convert files
    try:
        if input_path.is_file():
            # Single file conversion
            converter.stats['total'] = 1
            converter.log(f"Converting single file: {input_path.name}", "INFO")
            converter.convert_file(input_path, output_path, args.overwrite)
        else:
            # Directory conversion
            converter.log(f"Converting directory: {input_path}", "INFO")
            converter.log(f"Output directory: {output_path}", "INFO")
            converter.convert_directory(input_path, output_path,
                                       args.recursive, args.overwrite)

        # Print summary
        if not args.quiet:
            converter.print_summary()

    except KeyboardInterrupt:
        print("\n\nConversion interrupted by user")
        converter.print_summary()
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
