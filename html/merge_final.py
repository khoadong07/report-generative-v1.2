#!/usr/bin/env python3
"""
Final merge script - Extract and reorganize HTML properly
"""
from pathlib import Path
import re


def main():
    html_dir = Path(__file__).parent
    output_file = html_dir / "final_report.html"
    
    print("=" * 70)
    print("📋 MERGING 17 SLIDES")
    print("=" * 70)
    
    # Start HTML
    html = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Báo cáo Tuần - Final Report</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
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
    font-family: 'Inter', sans-serif;
    background-color: #e5e7eb;
    padding: 20px 0;
    margin: 0;
}

.page-wrapper {
    width: 1280px;
    height: 720px;
    margin: 0 auto 30px auto;
    background-color: #ffffff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    page-break-after: always;
    page-break-inside: avoid;
    position: relative;
}

.slide-container {
    position: absolute;
    top: 0;
    left: 0;
    width: 1280px;
    height: 720px;
    background-color: #f5f7fa;
    overflow: hidden;
}

@media print {
    body {
        background-color: #ffffff;
        padding: 0;
    }
    
    .page-wrapper {
        margin: 0;
        box-shadow: none;
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

"""
    
    slides_content = []
    all_scripts = []
    
    # Process each slide
    for i in range(1, 18):
        slide_file = html_dir / f"slide{i}.html"
        
        if not slide_file.exists():
            continue
        
        print(f"📄 Processing slide{i}.html...")
        
        with open(slide_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract body content (everything between <body> and </body>)
        body_match = re.search(r'<body>(.*?)</body>', content, re.DOTALL)
        if not body_match:
            print(f"   ⚠️  No body found")
            continue
        
        body_content = body_match.group(1)
        
        # Split into slide container and scripts
        # Find where scripts start
        script_start = body_content.find('<script')
        
        if script_start != -1:
            slide_html = body_content[:script_start]
            scripts_html = body_content[script_start:]
            
            # Extract all scripts
            script_matches = re.findall(r'<script[^>]*>(.*?)</script>', scripts_html, re.DOTALL)
            all_scripts.extend(script_matches)
        else:
            slide_html = body_content
        
        # Add ID to slide container
        slide_html = slide_html.replace(
            'class="slide-container"',
            f'class="slide-container" id="slide-{i}"',
            1
        )
        
        # Wrap in page wrapper
        wrapped_slide = f'<div class="page-wrapper">\n{slide_html.strip()}\n</div>'
        
        slides_content.append(wrapped_slide)
        print(f"   ✓ Extracted")
    
    # Combine everything
    html += '\n\n'.join(slides_content)
    
    # Add all scripts at the end
    if all_scripts:
        html += '\n\n<!-- Chart Scripts -->\n'
        for script in all_scripts:
            html += f'<script>{script}</script>\n'
    
    html += '\n</body>\n</html>'
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n{'=' * 70}")
    print(f"✅ SUCCESS!")
    print(f"{'=' * 70}")
    print(f"📊 Merged {len(slides_content)} slides")
    print(f"📜 Extracted {len(all_scripts)} scripts")
    print(f"📄 Output: {output_file.name}")
    print(f"💾 Size: {output_file.stat().st_size / 1024:.2f} KB")
    
    print(f"\n{'=' * 70}")
    print("📝 TO EXPORT PDF:")
    print(f"{'=' * 70}")
    print("1. Open final_report.html in Chrome")
    print("2. Press Ctrl+P (Cmd+P on Mac)")
    print("3. Settings:")
    print("   - Destination: Save as PDF")
    print("   - Layout: Landscape")
    print("   - Paper: Custom (1280 x 720)")
    print("   - Margins: None")
    print("   - Background graphics: ✓")
    print("4. Save")


if __name__ == "__main__":
    main()
