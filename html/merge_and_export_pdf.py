#!/usr/bin/env python3
"""
Merge 16 HTML slides and export to PDF in one step
Supports multiple PDF engines: WeasyPrint, Playwright, or Selenium
"""
from pathlib import Path
from bs4 import BeautifulSoup
import sys


def merge_slides():
    """Merge all 16 slide HTML files into one complete report"""
    html_dir = Path(__file__).parent
    output_file = html_dir / "final_report.html"
    
    print("=" * 60)
    print("📋 MERGING 16 SLIDES INTO ONE HTML")
    print("=" * 60)
    
    # HTML template with all necessary dependencies
    html_template = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
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
"""
    
    html_content = [html_template]
    slides_processed = 0
    
    # Process each slide (1-17, skipping any missing)
    for i in range(1, 18):
        slide_file = html_dir / f"slide{i}.html"
        
        if not slide_file.exists():
            print(f"⚠️  Slide {i} not found, skipping...")
            continue
        
        print(f"📄 Processing slide{i}.html...")
        
        try:
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
                slides_processed += 1
                
                # Extract and add scripts (for charts)
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and ('chart' in script.string.lower() or 'ctx' in script.string.lower()):
                        html_content.append(f'<script>{script.string}</script>')
            else:
                print(f"⚠️  No slide-container found in slide {i}")
        
        except Exception as e:
            print(f"❌ Error processing slide {i}: {e}")
    
    # Close HTML
    html_content.append('</body>\n</html>')
    
    # Write merged file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
    
    print(f"\n✅ Merged {slides_processed} slides into: {output_file.name}")
    print(f"📊 File size: {output_file.stat().st_size / 1024:.2f} KB")
    
    return output_file


def export_to_pdf_weasyprint(html_file):
    """Export HTML to PDF using WeasyPrint"""
    try:
        from weasyprint import HTML
    except ImportError:
        print("❌ WeasyPrint not installed!")
        print("Install with: pip install weasyprint")
        return None
    
    pdf_file = html_file.parent / "final_report_weasyprint.pdf"
    
    print(f"\n📦 Exporting to PDF using WeasyPrint...")
    print(f"   Output: {pdf_file.name}")
    
    try:
        HTML(filename=str(html_file)).write_pdf(str(pdf_file))
        print(f"✅ PDF exported successfully!")
        print(f"📊 File size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
        return pdf_file
    except Exception as e:
        print(f"❌ Error exporting PDF: {e}")
        return None


def export_to_pdf_playwright(html_file):
    """Export HTML to PDF using Playwright (better chart rendering)"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright not installed!")
        print("Install with: pip install playwright && playwright install chromium")
        return None
    
    pdf_file = html_file.parent / "final_report.pdf"
    
    print(f"\n📦 Exporting to PDF using Playwright...")
    print(f"   Output: {pdf_file.name}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            # Load HTML file
            page.goto(f"file://{html_file.absolute()}")
            
            # Wait for charts to render
            print("⏳ Waiting for charts to render...")
            page.wait_for_timeout(3000)
            
            # Export to PDF
            page.pdf(
                path=str(pdf_file),
                width='1280px',
                height='720px',
                print_background=True,
                prefer_css_page_size=True
            )
            
            browser.close()
        
        print(f"✅ PDF exported successfully!")
        print(f"📊 File size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
        return pdf_file
    
    except Exception as e:
        print(f"❌ Error exporting PDF: {e}")
        return None


def export_to_pdf_selenium(html_file):
    """Export HTML to PDF using Selenium (fallback option)"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import time
    except ImportError:
        print("❌ Selenium not installed!")
        print("Install with: pip install selenium")
        return None
    
    pdf_file = html_file.parent / "final_report_selenium.pdf"
    
    print(f"\n📦 Exporting to PDF using Selenium...")
    print(f"   Output: {pdf_file.name}")
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        
        # PDF settings
        settings = {
            "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": ""
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2,
            "isHeaderFooterEnabled": False,
            "isLandscapeEnabled": True,
            "pageSize": "CUSTOM",
            "customMargins": {"top": 0, "bottom": 0, "left": 0, "right": 0}
        }
        
        prefs = {
            'printing.print_preview_sticky_settings.appState': settings,
            'savefile.default_directory': str(html_file.parent)
        }
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument('--kiosk-printing')
        
        # Launch browser
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(f"file://{html_file.absolute()}")
        
        # Wait for charts to render
        print("⏳ Waiting for charts to render...")
        time.sleep(3)
        
        # Print to PDF
        driver.execute_script('window.print();')
        time.sleep(2)
        
        driver.quit()
        
        print(f"✅ PDF export initiated!")
        return pdf_file
    
    except Exception as e:
        print(f"❌ Error exporting PDF: {e}")
        return None


def main():
    """Main function to merge slides and export to PDF"""
    print("\n" + "=" * 60)
    print("🚀 MERGE 16 SLIDES AND EXPORT TO PDF")
    print("=" * 60 + "\n")
    
    # Step 1: Merge slides
    html_file = merge_slides()
    
    if not html_file or not html_file.exists():
        print("❌ Failed to merge slides!")
        return False
    
    # Step 2: Export to PDF
    print("\n" + "=" * 60)
    print("📄 EXPORTING TO PDF")
    print("=" * 60)
    
    # Try Playwright first (best for charts)
    pdf_file = export_to_pdf_playwright(html_file)
    
    # Fallback to WeasyPrint
    if not pdf_file:
        print("\n⚠️  Trying WeasyPrint as fallback...")
        pdf_file = export_to_pdf_weasyprint(html_file)
    
    # Final fallback to Selenium
    if not pdf_file:
        print("\n⚠️  Trying Selenium as fallback...")
        pdf_file = export_to_pdf_selenium(html_file)
    
    if pdf_file and pdf_file.exists():
        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"📄 HTML: {html_file.name}")
        print(f"📕 PDF:  {pdf_file.name}")
        print(f"📂 Location: {pdf_file.parent}")
        return True
    else:
        print("\n" + "=" * 60)
        print("⚠️  PDF EXPORT FAILED")
        print("=" * 60)
        print(f"📄 HTML file created: {html_file.name}")
        print(f"💡 You can manually print to PDF from browser:")
        print(f"   1. Open {html_file.name} in Chrome/Firefox")
        print(f"   2. Press Ctrl+P (or Cmd+P on Mac)")
        print(f"   3. Select 'Save as PDF'")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
