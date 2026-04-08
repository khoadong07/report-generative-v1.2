#!/usr/bin/env python3
"""
Merge all 16 slides into a single HTML file for easy PDF export
"""
from pathlib import Path
from bs4 import BeautifulSoup


def merge_slides():
    """Merge all slide HTML files into one complete report"""
    html_dir = Path(__file__).parent
    output_file = html_dir / "merged_report.html"
    
    # HTML template
    html_template = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Báo cáo Tuần - 16 Slides</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2.1.0"></script>
<style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Inter', sans-serif;
        background-color: #e5e7eb;
        padding: 0;
    }
    
    .slide-container {
        position: relative;
        width: 1280px;
        height: 720px;
        background-color: #f5f7fa;
        overflow: hidden;
        margin: 20px auto;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        page-break-after: always;
    }
    
    @media print {
        body {
            background-color: #ffffff;
            padding: 0;
        }
        
        .slide-container {
            margin: 0;
            box-shadow: none;
            page-break-after: always;
        }
    }
</style>
</head>
<body>
"""
    
    html_content = [html_template]
    
    # Process each slide
    for i in range(1, 17):
        slide_file = html_dir / f"slide{i}.html"
        
        if not slide_file.exists():
            print(f"⚠️  Slide {i} not found: {slide_file}")
            continue
        
        print(f"📄 Processing slide {i}...")
        
        with open(slide_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract slide container
        slide_container = soup.find('div', class_='slide-container')
        
        if slide_container:
            # Add slide number as ID
            slide_container['id'] = f'slide-{i}'
            html_content.append(str(slide_container))
            
            # Extract and add scripts
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'chart' in script.string.lower():
                    html_content.append(f'<script>{script.string}</script>')
        else:
            print(f"⚠️  No slide-container found in slide {i}")
    
    # Close HTML
    html_content.append('</body>\n</html>')
    
    # Write merged file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
    
    print(f"\n✅ Merged {16} slides into: {output_file}")
    print(f"📊 File size: {output_file.stat().st_size / 1024:.2f} KB")
    return output_file


if __name__ == "__main__":
    output = merge_slides()
    print(f"\n📌 Next steps:")
    print(f"   1. Open {output.name} in browser")
    print(f"   2. Print to PDF (Ctrl+P / Cmd+P)")
    print(f"   Or run: python export_pdf.py")
