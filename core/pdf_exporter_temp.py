#!/usr/bin/env python3
"""
Script merge slide1_merged.html và slide2_merged.html thành 1 file HTML và convert sang PDF
Requires: playwright
Install: pip install playwright && playwright install chromium
"""
import asyncio
from pathlib import Path
from bs4 import BeautifulSoup


def merge_html_files():
    """Merge tất cả 16 slides thành 1 file HTML"""
    output_dir = Path("output")
    merged_file = output_dir / "merged_slides.html"
    
    # Collect all slide files (slide1_merged.html to slide16_merged.html)
    slide_files = []
    for i in range(1, 17):
        slide_file = output_dir / f"slide{i}_merged.html"
        if slide_file.exists():
            slide_files.append(slide_file)
        else:
            print(f"⚠️  File không tồn tại: slide{i}_merged.html (bỏ qua)")
    
    if not slide_files:
        print("❌ Không tìm thấy file slide nào!")
        return None
    
    print(f"📄 Đang merge {len(slide_files)} slides...")
    
    # HTML template
    html_template = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Merged Report - 16 Slides</title>
<link href="https://fonts.cdnfonts.com/css/product-sans" rel="stylesheet"/>
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
        font-family: 'Product Sans', sans-serif;
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
    
    /* Additional styles from individual slides */
</style>
</head>
<body>
"""
    
    html_content = [html_template]
    scripts = []
    styles = []  # Collect all style tags
    
    # Process all slides
    for idx, slide_file in enumerate(slide_files, 1):
        with open(slide_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract styles using regex BEFORE parsing with BeautifulSoup
        import re
        style_pattern = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
        style_matches = style_pattern.findall(content)
        
        for style_content in style_matches:
            if style_content and style_content.strip():
                # Extract only table-related styles, not body/slide-container
                lines = style_content.split('\n')
                table_styles = []
                in_table_block = False
                current_block = []
                
                for line in lines:
                    trimmed = line.strip()
                    
                    # Start of a CSS block
                    if '{' in trimmed:
                        selector = trimmed.split('{')[0].strip()
                        if (selector.startswith('table') or 
                            selector.startswith('th') or 
                            selector.startswith('td') or 
                            selector.startswith('tr') or
                            '.nsr-' in selector):
                            in_table_block = True
                            current_block = [line]
                    elif in_table_block:
                        current_block.append(line)
                        if '}' in trimmed:
                            table_styles.append('\n'.join(current_block))
                            in_table_block = False
                            current_block = []
                
                if table_styles:
                    print(f"📝 Extracted {len(table_styles)} table style blocks from slide {idx}")
                    styles.append('\n'.join(table_styles))
        
        # Parse HTML
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract slide container
        slide_container = soup.find('div', class_='slide-container')
        
        if slide_container:
            # Add slide ID
            slide_container['id'] = f'slide-{idx}'
            
            # Extract scripts BEFORE removing them
            for script in soup.find_all('script'):
                if script.string and ('chart' in script.string.lower() or 'ctx' in script.string.lower() or 'Chart' in script.string):
                    script_content = script.string
                    
                    # Update canvas IDs in JavaScript for all slides except first
                    if idx > 1:
                        # Replace getElementById calls to add suffix
                        import re
                        script_content = re.sub(
                            r"getElementById\(['\"](\w+)['\"]\)",
                            rf"getElementById('\1_{idx}')",
                            script_content
                        )
                    
                    scripts.append(script_content)
            
            # Update canvas IDs to avoid conflicts (add suffix for all slides except first)
            if idx > 1:
                # Update ALL element IDs in the slide container (not just canvas)
                for elem in slide_container.find_all(id=True):
                    old_id = elem['id']
                    elem['id'] = f"{old_id}_{idx}"
            
            # Remove script tags from slide container (we'll add them separately)
            for script_tag in slide_container.find_all('script'):
                script_tag.decompose()
            
            html_content.append(str(slide_container))
        else:
            print(f"⚠️  Không tìm thấy slide-container trong {slide_file.name}")
    
    # Add all additional styles
    if styles:
        print(f"✅ Adding {len(styles)} style blocks to merged HTML")
        html_content.append('<style>')
        html_content.append('\n'.join(styles))
        html_content.append('</style>')
    else:
        print("⚠️  No additional styles found")
    
    # Add all scripts wrapped in IIFE to avoid variable conflicts
    for script in scripts:
        html_content.append(f'<script>(function() {{ {script} }})();</script>')
    
    # Close HTML
    html_content.append('</body>\n</html>')
    
    # Write merged file
    with open(merged_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
    
    print(f"✅ Đã merge thành công: {merged_file}")
    print(f"📊 Kích thước file: {merged_file.stat().st_size / 1024:.2f} KB")
    return merged_file


async def export_to_pdf(html_file):
    """Export HTML file sang PDF sử dụng Playwright"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright chưa được cài đặt!")
        print("Cài đặt bằng lệnh: pip install playwright && playwright install chromium")
        return False
    
    pdf_file = html_file.with_suffix('.pdf')
    
    print(f"\n📄 Đang load HTML: {html_file}")
    print(f"📦 Đang export sang: {pdf_file}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Load HTML file
        await page.goto(f"file://{html_file.absolute()}")
        
        # Đợi slides load xong
        print("⏳ Đang đợi slides load...")
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)  # Đợi 2 giây cho charts render
        
        # Export to PDF
        print("📄 Đang tạo PDF...")
        await page.pdf(
            path=str(pdf_file),
            width='1280px',
            height='720px',
            print_background=True,
            margin={
                'top': '0',
                'right': '0',
                'bottom': '0',
                'left': '0'
            }
        )
        
        await browser.close()
    
    print(f"✅ Đã export PDF thành công: {pdf_file}")
    print(f"📊 Kích thước file: {pdf_file.stat().st_size / 1024:.2f} KB")
    return True


async def main():
    """Main function"""
    print("=" * 60)
    print("🚀 MERGE & CONVERT HTML TO PDF")
    print("=" * 60)
    
    # Step 1: Merge HTML files
    merged_file = merge_html_files()
    
    if not merged_file:
        print("\n❌ Merge thất bại!")
        return
    
    # Step 2: Export to PDF
    print("\n" + "=" * 60)
    print("📄 CONVERTING TO PDF")
    print("=" * 60)
    
    success = await export_to_pdf(merged_file)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ HOÀN THÀNH!")
        print("=" * 60)
        print(f"📁 HTML: {merged_file}")
        print(f"📁 PDF: {merged_file.with_suffix('.pdf')}")
    else:
        print("\n❌ Export PDF thất bại!")


if __name__ == "__main__":
    asyncio.run(main())
