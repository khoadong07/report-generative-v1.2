# Hướng dẫn Export PDF từ 16 Slides HTML

## 📋 Tổng quan

Có 3 cách để merge 16 slides HTML thành 1 file PDF:

1. **Playwright** (Khuyến nghị) - Render charts tốt nhất
2. **WeasyPrint** - Nhanh nhưng charts có thể không đẹp
3. **Manual** - Print từ browser

---

## 🚀 Cách 1: Sử dụng Playwright (Khuyến nghị)

### Cài đặt
```bash
pip install playwright beautifulsoup4
playwright install chromium
```

### Chạy
```bash
cd html
python simple_merge_pdf.py
```

### Kết quả
- `final_report.html` - File HTML đã merge
- `final_report.pdf` - File PDF cuối cùng

---

## 🔧 Cách 2: Sử dụng WeasyPrint

### Cài đặt
```bash
pip install weasyprint beautifulsoup4
```

### Chạy
```bash
cd html
python merge_and_export_pdf.py
```

**Lưu ý:** WeasyPrint có thể không render charts JavaScript tốt.

---

## 🖨️ Cách 3: Manual Export (Không cần cài đặt)

### Bước 1: Merge slides
```bash
cd html
python merge_slides.py
```

### Bước 2: Print to PDF
1. Mở file `merged_report.html` trong Chrome/Firefox
2. Nhấn `Ctrl+P` (Windows) hoặc `Cmd+P` (Mac)
3. Chọn "Save as PDF"
4. Settings:
   - Layout: Landscape
   - Paper size: Custom (1280 x 720 px)
   - Margins: None
   - Background graphics: ✓ Enabled
5. Click "Save"

---

## 📦 Scripts có sẵn

| Script | Mô tả | Yêu cầu |
|--------|-------|---------|
| `simple_merge_pdf.py` | Merge + Export bằng Playwright | playwright |
| `merge_and_export_pdf.py` | Merge + Export (nhiều options) | playwright/weasyprint |
| `merge_slides.py` | Chỉ merge HTML | beautifulsoup4 |
| `export_pdf_weasyprint.py` | Export PDF từ complete_report.html | weasyprint |

---

## 🎯 So sánh các phương pháp

| Phương pháp | Chất lượng Charts | Tốc độ | Dễ sử dụng |
|-------------|-------------------|--------|------------|
| Playwright | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| WeasyPrint | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Manual | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🐛 Troubleshooting

### Playwright không cài được
```bash
# macOS
brew install playwright
playwright install chromium

# Linux
sudo apt-get install -y libgbm1 libnss3 libxss1 libasound2
playwright install chromium
```

### WeasyPrint lỗi
```bash
# macOS
brew install cairo pango gdk-pixbuf libffi

# Ubuntu/Debian
sudo apt-get install -y libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0
```

### Charts không hiển thị
- Đảm bảo có kết nối internet (để load Chart.js từ CDN)
- Tăng thời gian chờ trong script (wait_for_timeout)

---

## 📝 Ví dụ sử dụng

### Quick Start (Playwright)
```bash
# Cài đặt
pip install playwright beautifulsoup4
playwright install chromium

# Chạy
cd html
python simple_merge_pdf.py

# Kết quả: final_report.pdf
```

### Custom Export
```python
from simple_merge_pdf import merge_html_slides, export_pdf_playwright

# Merge
html_file = merge_html_slides()

# Export với custom settings
# ... (xem code trong simple_merge_pdf.py)
```

---

## ✅ Checklist

- [ ] Đã có đủ 16 file slide (slide1.html - slide17.html)
- [ ] Đã cài đặt dependencies (playwright hoặc weasyprint)
- [ ] Đã test mở 1 slide HTML trong browser
- [ ] Charts hiển thị đúng trong browser
- [ ] Chạy script merge + export
- [ ] Kiểm tra file PDF output

---

## 📞 Support

Nếu gặp vấn đề, kiểm tra:
1. Python version >= 3.8
2. Tất cả dependencies đã cài đặt
3. File HTML slides tồn tại và hợp lệ
4. Có kết nối internet (cho CDN)
