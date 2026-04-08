#!/usr/bin/env python3
"""
Script to export complete HTML report to PDF using WeasyPrint
Requires: weasyprint
Install: pip install weasyprint
"""
from pathlib import Path


def export_to_pdf():
    """Export complete_report.html to PDF using WeasyPrint"""
    try:
        from weasyprint import HTML
    except ImportError:
        print("❌ WeasyPrint not installed!")
        print("Install with: pip install weasyprint")
        return False
    
    html_dir = Path(__file__).parent
    html_file = html_dir / "complete_report.html"
    pdf_file = html_dir / "complete_report_weasyprint.pdf"
    
    if not html_file.exists():
        print(f"❌ File not found: {html_file}")
        return False
    
    print(f"📄 Loading HTML: {html_file}")
    print(f"📦 Exporting to: {pdf_file}")
    
    # Convert HTML to PDF
    HTML(filename=str(html_file)).write_pdf(str(pdf_file))
    
    print(f"✅ PDF exported successfully: {pdf_file}")
    print(f"📊 File size: {pdf_file.stat().st_size / 1024 / 1024:.2f} MB")
    return True


if __name__ == "__main__":
    success = export_to_pdf()
    exit(0 if success else 1)
