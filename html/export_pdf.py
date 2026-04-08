#!/usr/bin/env python3
"""
Script to export complete HTML report to PDF
Requires: playwright
Install: pip install playwright && playwright install chromium
"""
import asyncio
import os
from pathlib import Path


async def export_to_pdf():
    """Export complete_report.html to PDF using Playwright"""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright not installed!")
        print("Install with: pip install playwright && playwright install chromium")
        return False
    
    html_dir = Path(__file__).parent
    html_file = html_dir / "complete_report.html"
    pdf_file = html_dir / "complete_report.pdf"
    
    if not html_file.exists():
        print(f"❌ File not found: {html_file}")
        return False
    
    print(f"📄 Loading HTML: {html_file}")
    print(f"📦 Exporting to: {pdf_file}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Load the HTML file
        await page.goto(f"file://{html_file.absolute()}")
        
        # Wait for all slides to load
        print("⏳ Waiting for slides to load...")
        await page.wait_for_timeout(5000)  # Wait 5 seconds for dynamic content
        
        # Check if slides loaded
        slide_count = await page.locator('.slide').count()
        print(f"✅ Found {slide_count} slides")
        
        # Export to PDF
        print("📄 Generating PDF...")
        await page.pdf(
            path=str(pdf_file),
            format='A4',
            landscape=True,
            print_background=True,
            margin={
                'top': '0',
                'right': '0',
                'bottom': '0',
                'left': '0'
            }
        )
        
        await browser.close()
    
    print(f"✅ PDF exported successfully: {pdf_file}")
    print(f"📊 File size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
    return True


if __name__ == "__main__":
    success = asyncio.run(export_to_pdf())
    exit(0 if success else 1)
