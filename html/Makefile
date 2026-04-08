.PHONY: help merge pdf pdf-playwright pdf-weasyprint install-playwright install-weasyprint serve clean final

help:
	@echo "📊 HTML Report Tools"
	@echo ""
	@echo "Available commands:"
	@echo "  make final              - Merge 17 slides into final_report.html (NO dependencies)"
	@echo "  make merge              - Merge all 16 slides into one HTML file (old)"
	@echo "  make pdf                - Merge slides and export to PDF (using Playwright)"
	@echo "  make pdf-playwright     - Export to PDF using Playwright (requires install)"
	@echo "  make pdf-weasyprint     - Export to PDF using WeasyPrint (requires install)"
	@echo "  make serve              - Start local web server to view slides"
	@echo "  make install-playwright - Install Playwright for PDF export"
	@echo "  make install-weasyprint - Install WeasyPrint for PDF export"
	@echo "  make clean              - Remove generated files"

final:
	@echo "🚀 Merging 17 slides into final_report.html..."
	python3 merge_slides_simple.py

merge:
	@echo "🔄 Merging slides..."
	python3 merge_slides.py

pdf: merge pdf-playwright

pdf-playwright:
	@echo "📄 Exporting to PDF with Playwright..."
	python3 export_pdf.py

pdf-weasyprint:
	@echo "📄 Exporting to PDF with WeasyPrint..."
	python3 export_pdf_weasyprint.py

install-playwright:
	@echo "📦 Installing Playwright..."
	pip install playwright
	playwright install chromium

install-weasyprint:
	@echo "📦 Installing WeasyPrint..."
	pip install weasyprint

serve:
	@echo "🌐 Starting web server at http://localhost:8000"
	@echo "   Open http://localhost:8000/complete_report.html"
	@echo "   Or http://localhost:8000/merged_report.html"
	@echo "   Or http://localhost:8000/final_report.html"
	python3 serve.py

clean:
	@echo "🧹 Cleaning generated files..."
	rm -f merged_report.html
	rm -f complete_report.pdf
	rm -f complete_report_weasyprint.pdf
	rm -f final_report.html
	rm -f final_report.pdf
	rm -f *.bak
	@echo "✅ Done"
