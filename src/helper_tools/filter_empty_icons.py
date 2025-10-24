#!/usr/bin/env python3
"""
Filter and mark empty icons in the extracted icon database.

Empty icons are those that are completely transparent or have no meaningful content.
This helps the GUI avoid displaying blank placeholders.

Detection methods:
1. Fully transparent (all alpha = 0)
2. Single solid color (no variation)
3. Below minimum pixel variance threshold
4. Perceptual hash comparison (detect duplicates)
"""

from PIL import Image
import numpy as np
from pathlib import Path
import json
from typing import Dict, List, Tuple
import hashlib

def analyze_icon_content(icon_path: Path) -> Dict:
    """
    Analyze icon to determine if it's empty or has content.
    
    Args:
        icon_path: Path to icon PNG file
        
    Returns:
        Dictionary with analysis results
    """
    try:
        img = Image.open(icon_path).convert('RGBA')
        pixels = np.array(img)
        
        # Extract channels
        r, g, b, a = pixels[:,:,0], pixels[:,:,1], pixels[:,:,2], pixels[:,:,3]
        
        # Analysis metrics
        analysis = {
            'path': str(icon_path),
            'is_empty': False,
            'reasons': [],
            'metrics': {}
        }
        
        # 1. Check if fully transparent
        alpha_mean = np.mean(a)
        alpha_max = np.max(a)
        
        if alpha_max == 0:
            analysis['is_empty'] = True
            analysis['reasons'].append('fully_transparent')
            analysis['metrics']['alpha_mean'] = 0.0
            return analysis
        
        analysis['metrics']['alpha_mean'] = float(alpha_mean)
        analysis['metrics']['alpha_max'] = int(alpha_max)
        
        # 2. Check if almost fully transparent (>95% transparent)
        transparent_pixels = np.sum(a < 10)
        total_pixels = a.size
        transparency_ratio = transparent_pixels / total_pixels
        
        analysis['metrics']['transparency_ratio'] = float(transparency_ratio)
        
        if transparency_ratio > 0.95:
            analysis['is_empty'] = True
            analysis['reasons'].append('mostly_transparent')
            return analysis
        
        # 3. Check for single solid color (no variation)
        # Only check non-transparent pixels
        mask = a > 10
        if np.sum(mask) > 0:
            r_var = np.var(r[mask])
            g_var = np.var(g[mask])
            b_var = np.var(b[mask])
            total_var = r_var + g_var + b_var
            
            analysis['metrics']['color_variance'] = float(total_var)
            
            if total_var < 10:  # Very low variance = solid color
                analysis['is_empty'] = True
                analysis['reasons'].append('solid_color')
                return analysis
        
        # 4. Calculate perceptual hash for duplicate detection
        # Resize to 8x8 for hash
        small = img.resize((8, 8), Image.Resampling.LANCZOS).convert('L')
        pixels_small = np.array(small)
        avg = pixels_small.mean()
        diff = pixels_small > avg
        phash = ''.join(['1' if x else '0' for x in diff.flatten()])
        
        analysis['metrics']['perceptual_hash'] = phash
        
        # 5. Calculate edge detection score (meaningful content has edges)
        from scipy import ndimage
        
        # Convert to grayscale weighted by alpha
        gray = 0.299*r + 0.587*g + 0.114*b
        gray_masked = gray * (a / 255.0)
        
        # Sobel edge detection
        edges_x = ndimage.sobel(gray_masked, axis=0)
        edges_y = ndimage.sobel(gray_masked, axis=1)
        edges = np.hypot(edges_x, edges_y)
        
        edge_score = np.sum(edges) / total_pixels
        analysis['metrics']['edge_score'] = float(edge_score)
        
        # Low edge score suggests no meaningful content
        if edge_score < 1.0 and transparency_ratio > 0.5:
            analysis['is_empty'] = True
            analysis['reasons'].append('low_content')
        
        return analysis
        
    except Exception as e:
        return {
            'path': str(icon_path),
            'is_empty': False,
            'error': str(e),
            'reasons': ['analysis_failed'],
            'metrics': {}
        }

def find_duplicate_icons(icon_analyses: List[Dict]) -> Dict[str, List[str]]:
    """
    Find duplicate icons using perceptual hash.
    
    Args:
        icon_analyses: List of icon analysis results
        
    Returns:
        Dictionary mapping hash to list of icon paths
    """
    hash_groups = {}
    
    for analysis in icon_analyses:
        if 'perceptual_hash' in analysis.get('metrics', {}):
            phash = analysis['metrics']['perceptual_hash']
            if phash not in hash_groups:
                hash_groups[phash] = []
            hash_groups[phash].append(analysis['path'])
    
    # Only return groups with duplicates
    duplicates = {h: paths for h, paths in hash_groups.items() if len(paths) > 1}
    
    return duplicates

def create_visual_report(
    output_dir: Path,
    empty_icons: List[Dict],
    sample_size: int = 20
):
    """
    Create HTML report with visual samples of empty icons.
    
    Args:
        output_dir: Directory to save report
        empty_icons: List of empty icon analyses
        sample_size: Number of samples to include
    """
    from datetime import datetime
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Empty Icons Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .icon-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            margin-top: 20px;
        }}
        .icon-card {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            text-align: center;
        }}
        .icon-card img {{
            width: 64px;
            height: 64px;
            image-rendering: pixelated;
            border: 1px solid #ccc;
            background: 
                repeating-conic-gradient(#ccc 0% 25%, white 0% 50%) 
                50% / 8px 8px;
        }}
        .icon-card .info {{
            font-size: 10px;
            color: #666;
            margin-top: 5px;
        }}
        .reason {{
            display: inline-block;
            background: #ff6b6b;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 9px;
            margin: 2px;
        }}
    </style>
</head>
<body>
    <h1>Empty Icons Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total empty icons found:</strong> {len(empty_icons)}</p>
        <p><strong>Samples shown:</strong> {min(sample_size, len(empty_icons))}</p>
    </div>
    
    <h2>Sample Empty Icons</h2>
    <div class="icon-grid">
"""
    
    for analysis in empty_icons[:sample_size]:
        path = Path(analysis['path'])
        rel_path = path.relative_to(path.parent.parent.parent)
        reasons = ', '.join(analysis.get('reasons', []))
        
        html += f"""
        <div class="icon-card">
            <img src="../../../{rel_path}" alt="{path.name}">
            <div class="info">
                <strong>{path.parent.name}/{path.name}</strong><br>
                <span class="reason">{reasons}</span>
            </div>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    report_path = output_dir / "empty_icons_report.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(html)
    
    return report_path

def main():
    """Main filtering process."""
    
    project_root = Path(__file__).parent.parent.parent
    icons_root = project_root / "ExtractedAssets" / "UI" / "icons_extracted"
    index_path = icons_root / "icon_index.json"
    output_path = icons_root / "icon_analysis.json"
    reports_dir = project_root / "ExtractedAssets" / "UI" / "reports"
    
    print("=" * 80)
    print("ICON CONTENT ANALYSIS")
    print("=" * 80)
    print(f"Icons directory: {icons_root}")
    print()
    
    # Load icon index
    with open(index_path, 'r') as f:
        icon_index = json.load(f)
    
    total_icons = len(icon_index['icons'])
    print(f"Total icons to analyze: {total_icons}")
    print()
    
    # Analyze all icons
    print("Analyzing icon content...")
    analyses = []
    empty_count = 0
    
    from tqdm import tqdm
    
    for i, (key, icon_data) in enumerate(tqdm(icon_index['icons'].items(), desc="Processing")):
        icon_path = icons_root / icon_data['path']
        
        if not icon_path.exists():
            continue
        
        analysis = analyze_icon_content(icon_path)
        analysis['key'] = key
        analysis['category'] = icon_data['category']
        analysis['atlas_number'] = icon_data['atlas_number']
        analysis['icon_index'] = icon_data['icon_index']
        
        analyses.append(analysis)
        
        if analysis.get('is_empty'):
            empty_count += 1
    
    print()
    print(f"Analysis complete: {len(analyses)} icons analyzed")
    print(f"Empty icons found: {empty_count} ({empty_count/len(analyses)*100:.1f}%)")
    print()
    
    # Find duplicates
    print("Finding duplicate icons...")
    duplicates = find_duplicate_icons(analyses)
    print(f"Duplicate groups found: {len(duplicates)}")
    
    total_duplicates = sum(len(paths) - 1 for paths in duplicates.values())
    print(f"Total duplicate icons: {total_duplicates}")
    print()
    
    # Categorize empty icons by reason
    empty_by_reason = {}
    for analysis in analyses:
        if analysis.get('is_empty'):
            for reason in analysis.get('reasons', []):
                empty_by_reason.setdefault(reason, []).append(analysis)
    
    print("Empty icons by reason:")
    for reason, icons in sorted(empty_by_reason.items(), key=lambda x: -len(x[1])):
        print(f"  {reason:25s}: {len(icons):5d} icons")
    print()
    
    # Save analysis results
    output_data = {
        'total_icons': len(analyses),
        'empty_count': empty_count,
        'duplicate_groups': len(duplicates),
        'total_duplicates': total_duplicates,
        'empty_by_reason': {k: len(v) for k, v in empty_by_reason.items()},
        'analyses': analyses,
        'duplicates': {k: v for k, v in list(duplicates.items())[:100]}  # First 100 groups
    }
    
    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✓ Analysis saved: {output_path}")
    print()
    
    # Create visual report
    print("Creating visual report...")
    empty_icons = [a for a in analyses if a.get('is_empty')]
    report_path = create_visual_report(reports_dir, empty_icons, sample_size=50)
    print(f"✓ Report saved: {report_path}")
    print()
    
    # Update icon index with empty flags
    print("Updating icon index with empty flags...")
    for analysis in analyses:
        key = analysis.get('key')
        if key and key in icon_index['icons']:
            icon_index['icons'][key]['is_empty'] = analysis.get('is_empty', False)
            icon_index['icons'][key]['empty_reasons'] = analysis.get('reasons', [])
            icon_index['icons'][key]['metrics'] = {
                k: v for k, v in analysis.get('metrics', {}).items()
                if k != 'perceptual_hash'  # Don't store hash in index
            }
    
    # Save updated index
    with open(index_path, 'w') as f:
        json.dump(icon_index, f, indent=2)
    
    print(f"✓ Icon index updated: {index_path}")
    print()
    
    # Summary
    print("=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Total icons:        {len(analyses)}")
    print(f"Empty icons:        {empty_count} ({empty_count/len(analyses)*100:.1f}%)")
    print(f"Valid icons:        {len(analyses) - empty_count} ({(len(analyses)-empty_count)/len(analyses)*100:.1f}%)")
    print(f"Duplicate groups:   {len(duplicates)}")
    print(f"Unique icons:       {len(analyses) - total_duplicates}")
    print()
    print("Files created:")
    print(f"  - Analysis data:  {output_path}")
    print(f"  - Visual report:  {report_path}")
    print(f"  - Updated index:  {index_path}")
    print("=" * 80)

if __name__ == '__main__':
    main()
