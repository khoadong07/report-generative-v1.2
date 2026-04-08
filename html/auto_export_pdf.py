#!/usr/bin/env python3
"""
Automatic HTML to PDF export
Tries multiple methods in order of preference
"""
from pathlib import Path
import subprocess
import sys
import os


def check_command(cmd):
    """Check if a command is available"""
    try:
        subprocess.run([cmd, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def merge_html():
    """Merge HTML slides first"""
    print("=" * 70)
    print("📋 STEP 1: MERGING HTML SLIDES")
    print("=" * 70)
    
    result = subprocess.run(['python3', 'merge_final.py'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Failed to merge HTML")
        print(result.stderr)
        return None
    
    print(result.stdout)
    return Path(__file__).parent / "final_report.html"


def export_with_playwright(html_file):
    """Export using Playwright (best quality)"""
    print("\n" + "=" * 70)
    print("📦 STEP 2: EXPORTING TO PDF (Playwright)")
    print("=" * 70)
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright not installed")
        return None
    
    pdf_file = html_file.parent / "final_report.pdf"
    
    try:
        with sync_playwright() as p:
            print("🌐 Launching browser...")
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1280, 'height': 720})
            
            print(f"📄 Loading {html_file.name}...")
            page.goto(f"file://{html_file.absolute()}")
            
            print("⏳ Waiting for charts to render (5 seconds)...")
            page.wait_for_timeout(5000)
            
            print("💾 Generating PDF...")
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
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def export_with_wkhtmltopdf(html_file):
    """Export using wkhtmltopdf"""
    print("\n" + "=" * 70)
    print("📦 STEP 2: EXPORTING TO PDF (wkhtmltopdf)")
    print("=" * 70)
    
    if not check_command('wkhtmltopdf'):
        print("❌ wkhtmltopdf not installed")
        print("Install: brew install wkhtmltopdf")
        return None
    
    pdf_file = html_file.parent / "final_report.pdf"
    
    cmd = [
        'wkhtmltopdf',
        '--page-width', '1280px',
        '--page-height', '720px',
        '--margin-top', '0',
        '--margin-bottom', '0',
        '--margin-left', '0',
        '--margin-right', '0',
        '--enable-javascript',
        '--javascript-delay', '3000',
        '--no-stop-slow-scripts',
        str(html_file),
        str(pdf_file)
    ]
    
    try:
        print("💾 Generating PDF...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and pdf_file.exists():
            print(f"✅ PDF created: {pdf_file.name}")
            print(f"📊 Size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
            return pdf_file
        else:
            print(f"❌ Failed: {result.stderr}")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def export_with_chrome_headless(html_file):
    """Export using Chrome headless"""
    print("\n" + "=" * 70)
    print("📦 STEP 2: EXPORTING TO PDF (Chrome Headless)")
    print("=" * 70)
    
    # Find Chrome binary
    chrome_paths = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        'google-chrome',
        'chromium'
    ]
    
    chrome_bin = None
    for path in chrome_paths:
        if os.path.exists(path) or check_command(path):
            chrome_bin = path
            break
    
    if not chrome_bin:
        print("❌ Chrome/Chromium not found")
        return None
    
    pdf_file = html_file.parent / "final_report.pdf"
    
    cmd = [
        chrome_bin,
        '--headless',
        '--disable-gpu',
        '--print-to-pdf=' + str(pdf_file),
        '--print-to-pdf-no-header',
        '--no-margins',
        f'file://{html_file.absolute()}'
    ]
    
    try:
        print("💾 Generating PDF with Chrome...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if pdf_file.exists():
            print(f"✅ PDF created: {pdf_file.name}")
            print(f"📊 Size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
            return pdf_file
        else:
            print(f"❌ Failed to create PDF")
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def manual_instructions(html_file):
    """Show manual export instructions"""
    print("\n" + "=" * 70)
    print("📝 MANUAL EXPORT INSTRUCTIONS")
    print("=" * 70)
    print(f"\n✅ HTML file ready: {html_file.name}")
    print(f"📂 Location: {html_file.absolute()}")
    print("\n🖨️  To export to PDF manually:")
    print("1. Open final_report.html in Chrome or Firefox")
    print("2. Press Ctrl+P (Windows) or Cmd+P (Mac)")
    print("3. Settings:")
    print("   - Destination: Save as PDF")
    print("   - Layout: Landscape")
    print("   - Paper size: Custom (1280 x 720)")
    print("   - Margins: None")
    print("   - Background graphics: ✓ Enabled")
    print("4. Click Save")
    print("\n💡 Or install Playwright for automatic export:")
    print("   pip install playwright")
    print("   playwright install chromium")
    print("   python3 auto_export_pdf.py")


def main():
    print("\n" + "=" * 70)
    print("🚀 AUTO MERGE & EXPORT TO PDF")
    print("=" * 70)
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Step 1: Merge HTML
    html_file = merge_html()
    if not html_file or not html_file.exists():
        print("\n❌ Failed to merge HTML slides")
        return 1
    
    # Step 2: Try to export PDF (multiple methods)
    pdf_file = None
    
    # Method 1: Playwright (best)
    pdf_file = export_with_playwright(html_file)
    
    # Method 2: wkhtmltopdf
    if not pdf_file:
        pdf_file = export_with_wkhtmltopdf(html_file)
    
    # Method 3: Chrome headless
    if not pdf_file:
        pdf_file = export_with_chrome_headless(html_file)
    
    # If all methods failed, show manual instructions
    if not pdf_file:
        manual_instructions(html_file)
        return 1
    
    # Success!
    print("\n" + "=" * 70)
    print("✅ SUCCESS!")
    print("=" * 70)
    print(f"📄 HTML: {html_file.name}")
    print(f"📕 PDF:  {pdf_file.name}")
    print(f"📂 Location: {pdf_file.parent}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
