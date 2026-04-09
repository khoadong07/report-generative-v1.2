#!/usr/bin/env python3
"""
Simple merge script - NO external dependencies required
Just merge HTML files using standard Python library
"""
from pathlib import Path
import re


def extract_slide_content(html_content):
    """Extract slide container (without scripts) and scripts separately"""
    # Find the opening tag of slide-container
    start_match = re.search(r'<div[^>]*class="slide-container"[^>]*>', html_content)
    if not start_match:
        return None, []
    
    start_pos = start_match.start()
    
    # Find the matching closing </div> by counting nested divs
    # But stop before any <script> tag
    pos = start_match.end()
    depth = 1
    container_end = None
    
    while pos < len(html_content) and depth > 0:
        # Look for next <div, </div>, or <script
        next_open = html_content.find('<div', pos)
        next_close = html_content.find('</div>', pos)
        next_script = html_content.find('<script', pos)
        
        if next_close == -1:
            break
        
        # If we hit a script tag before closing the container, stop there
        if next_script != -1 and next_script < next_close and depth == 1:
            container_end = next_close + 6
            break
        
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            pos = next_close + 6
            if depth == 0:
                container_end = pos
                break
    
    if not container_end:
        return None, []
    
    container = html_content[start_pos:container_end]
    
    # Find all script tags in the original HTML (after the container)
    script_matches = re.findall(
        r'<script[^>]*>(.*?)</script>',
        html_content[container_end:],
        re.DOTALL
    )
    
    # Filter scripts that contain chart code
    chart_scripts = [
        script for script in script_matches
        if 'chart' in script.lower() or 'ctx' in script.lower() or 'new Chart' in script
    ]
    
    return container, chart_scripts


def merge_slides():
    """Merge all slide HTML files into one"""
    html_dir = Path(__file__).parent
    output_file = html_dir / "final_report.html"
    
    print("=" * 70)
    print("📋 MERGING HTML SLIDES")
    print("=" * 70)
    
    # HTML header
    html_parts = ["""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Báo cáo Tuần - Final Report</title>
<link href="https://fonts.cdnfonts.com/css/product-sans" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2"></script>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Product Sans', sans-serif;
    background-color: #ffffff;
    padding: 0;
}

.slide-container {
    position: relative;
    width: 1280px;
    height: 720px;
    background-color: #f5f7fa;
    overflow: hidden;
    margin: 0 auto;
    page-break-after: always;
    page-break-inside: avoid;
}

@media print {
    body {
        background-color: #ffffff;
    }
    
    .slide-container {
        page-break-after: always;
        page-break-inside: avoid;
    }
    
    @page {
        size: 1280px 720px;
        margin: 0;
    }
}
</style>
</head>
<body>
"""]
    
    slides_processed = 0
    all_scripts = []
    
    # Process each slide
    for i in range(1, 18):
        slide_file = html_dir / f"slide{i}.html"
        
        if not slide_file.exists():
            continue
        
        print(f"📄 Processing slide{i}.html...")
        
        try:
            with open(slide_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract content
            container, scripts = extract_slide_content(content)
            
            if container:
                # Add ID to container
                container = container.replace(
                    'class="slide-container"',
                    f'class="slide-container" id="slide-{i}"',
                    1
                )
                html_parts.append(container)
                html_parts.append("")  # Add blank line between slides
                all_scripts.extend(scripts)
                slides_processed += 1
                print(f"   ✓ Extracted slide content and {len(scripts)} scripts")
            else:
                print(f"   ⚠️  Could not extract slide container")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Add all scripts at the end (outside slide containers)
    if all_scripts:
        html_parts.append("\n<!-- Chart Scripts -->")
        for idx, script in enumerate(all_scripts, 1):
            html_parts.append(f"<script>\n// Script for slide {idx}\n{script}\n</script>")
    
    # Close HTML
    html_parts.append("</body>\n</html>")
    
    # Write output
    final_html = '\n'.join(html_parts)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"\n{'=' * 70}")
    print(f"✅ SUCCESS!")
    print(f"{'=' * 70}")
    print(f"📊 Merged {slides_processed} slides")
    print(f"📄 Output: {output_file.name}")
    print(f"💾 Size: {output_file.stat().st_size / 1024:.2f} KB")
    print(f"📂 Location: {output_file.absolute()}")
    
    print(f"\n{'=' * 70}")
    print("📝 NEXT STEPS:")
    print(f"{'=' * 70}")
    print("1. Open final_report.html in Chrome or Firefox")
    print("2. Press Ctrl+P (Windows) or Cmd+P (Mac)")
    print("3. Select 'Save as PDF'")
    print("4. Settings:")
    print("   - Layout: Landscape")
    print("   - Paper size: Custom (1280 x 720)")
    print("   - Margins: None")
    print("   - Background graphics: Enabled")
    print("5. Click Save")
    
    print(f"\n💡 Or install Playwright for automatic PDF export:")
    print("   pip install playwright beautifulsoup4")
    print("   playwright install chromium")
    print("   python simple_merge_pdf.py")
    
    return output_file


if __name__ == "__main__":
    merge_slides()
