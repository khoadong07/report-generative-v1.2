#!/usr/bin/env python3
"""
Script to update all HTML templates and Python files to use SVN Product Sans font
"""
import re
from pathlib import Path

# Font URL for SVN Product Sans (using a CDN or local font)
# Note: SVN Product Sans might need to be hosted locally or use a specific CDN
NEW_FONT_LINK = '<link href="https://fonts.cdnfonts.com/css/product-sans" rel="stylesheet"/>'
NEW_FONT_FAMILY = "'Product Sans', sans-serif"

def update_html_file(file_path: Path):
    """Update a single HTML file to use SVN Product Sans"""
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # Replace Google Fonts link
    content = re.sub(
        r'<link\s+href="https://fonts\.googleapis\.com/css2\?[^"]*"\s+rel="stylesheet"\s*/?>',
        NEW_FONT_LINK,
        content,
        flags=re.IGNORECASE
    )
    
    # Replace font-family: 'Inter' or 'Roboto' with 'Product Sans'
    content = re.sub(
        r"font-family:\s*['\"](?:Inter|Roboto)['\"](?:,\s*sans-serif)?",
        f"font-family: {NEW_FONT_FAMILY}",
        content
    )
    
    # Also handle cases without quotes
    content = re.sub(
        r"font-family:\s*(?:Inter|Roboto)(?:,\s*sans-serif)?(?=[;\s])",
        f"font-family: {NEW_FONT_FAMILY}",
        content
    )
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

def update_python_file(file_path: Path):
    """Update a single Python file that generates HTML"""
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # Replace Google Fonts link in Python strings
    content = re.sub(
        r'https://fonts\.googleapis\.com/css2\?family=Roboto:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap',
        'https://fonts.cdnfonts.com/css/product-sans',
        content
    )
    
    # Replace font-family in Python strings
    content = re.sub(
        r"font-family:\s*['\"](?:Inter|Roboto)['\"](?:,\s*sans-serif)?",
        f"font-family: {NEW_FONT_FAMILY}",
        content
    )
    
    # Replace 'Inter', sans-serif or 'Roboto', sans-serif
    content = re.sub(
        r"['\"](?:Inter|Roboto)['\"],\s*sans-serif",
        NEW_FONT_FAMILY,
        content
    )
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

def main():
    print("🔄 Updating fonts to SVN Product Sans...")
    print("=" * 60)
    
    # Update HTML files
    html_dir = Path("html")
    html_files = list(html_dir.glob("*.html"))
    html_updated = 0
    
    print(f"\n📄 Processing {len(html_files)} HTML files...")
    for html_file in html_files:
        if update_html_file(html_file):
            print(f"   ✅ {html_file.name}")
            html_updated += 1
        else:
            print(f"   ⏭️  {html_file.name} (no changes)")
    
    # Update Python files that generate HTML
    python_files = [
        Path("merge_slides.py"),
        Path("core/pdf_exporter.py"),
        Path("test_generate.py"),
        Path("html/merge_slides.py"),
        Path("html/merge_slides_simple.py"),
        Path("html/merge_final.py"),
        Path("html/simple_merge_pdf.py"),
        Path("html/merge_and_export_pdf.py"),
    ]
    
    python_updated = 0
    print(f"\n🐍 Processing Python files...")
    for py_file in python_files:
        if py_file.exists():
            if update_python_file(py_file):
                print(f"   ✅ {py_file}")
                python_updated += 1
            else:
                print(f"   ⏭️  {py_file} (no changes)")
        else:
            print(f"   ⚠️  {py_file} (not found)")
    
    print("\n" + "=" * 60)
    print(f"✅ Updated {html_updated} HTML files and {python_updated} Python files")
    print("=" * 60)
    print("\n📝 Note: SVN Product Sans font link uses CDN Fonts.")
    print("   If you need to use a local font file, update the font link manually.")

if __name__ == "__main__":
    main()
