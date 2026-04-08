#!/usr/bin/env python3
"""
Simple script to merge 16 HTML slides and export to PDF
Uses Playwright for best chart rendering quality
"""
from pathlib import Path
import time


def merge_html_slides():
    """Merge all slide HTML files into one"""
    html_dir = Path(__file__).parent
    
    print("📋 Merging HTML slides...")
    
    slides_html = []
    
    # Read each slide
    for i in range(1, 18):
        slide_file = html_dir / f"slide{i}.html"
        if slide_file.exists():
            print(f"  ✓ slide{i}.html")
            with open(slide_file, 'r', encoding='utf-8') as f:
                slides_html.append(f.read())
    
    # Create merged HTML
    merged_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<title>Final Report - 16 Slides</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@2"></script>
<style>
body {{ margin: 0; padding: 0; background: #fff; }}
.slide-container {{ 
    width: 1280px; 
    height: 720px; 
    margin: 0 auto;
    page-break-after: always;
    page-break-inside: avoid;
}}
@page {{ size: 1280px 720px; margin: 0; }}
</style>
</head>
<body>
{''.join([html.split('<body>')[1].split('</body>')[0] if '<body>' in html else '' for html in slides_html])}
</body>
</html>"""
    
    output_file = html_dir / "final_report.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(merged_html)
    
    print(f"✅ Merged HTML: {output_file.name}")
    return output_file


def export_pdf_playwright(html_file):
    """Export to PDF using Playwright"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n❌ Playwright not installed!")
        print("Install: pip install playwright")
        print("Then run: playwright install chromium")
        return None
    
    pdf_file = html_file.parent / "final_report.pdf"
    
    print(f"\n📦 Exporting to PDF...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        
        # Load HTML
        page.goto(f"file://{html_file.absolute()}")
        
        # Wait for all charts to render
        print("⏳ Rendering charts (5 seconds)...")
        page.wait_for_timeout(5000)
        
        # Export to PDF
        page.pdf(
            path=str(pdf_file),
            width='1280px',
            height='720px',
            print_background=True,
            prefer_css_page_size=True,
            margin={'top': '0', 'bottom': '0', 'left': '0', 'right': '0'}
        )
        
        browser.close()
    
    print(f"✅ PDF created: {pdf_file.name}")
    print(f"📊 Size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
    return pdf_file


def main():
    print("\n" + "="*60)
    print("🚀 MERGE 16 SLIDES TO PDF")
    print("="*60 + "\n")
    
    # Merge HTML
    html_file = merge_html_slides()
    
    # Export PDF
    pdf_file = export_pdf_playwright(html_file)
    
    if pdf_file:
        print("\n" + "="*60)
        print("✅ SUCCESS!")
        print("="*60)
        print(f"📄 {html_file.name}")
        print(f"📕 {pdf_file.name}")
        print(f"📂 {pdf_file.parent}")
    else:
        print("\n💡 Manual export:")
        print(f"   Open {html_file.name} in browser and print to PDF")


if __name__ == "__main__":
    main()
