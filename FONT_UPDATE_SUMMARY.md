# Font Update Summary - SVN Product Sans

## Thay đổi đã thực hiện

Đã cập nhật toàn bộ hệ thống để sử dụng font **SVN Product Sans** thay thế cho Inter và Roboto.

### Files đã cập nhật:

#### HTML Templates (24 files)
- `html/slide1.html` đến `html/slide17.html`
- `html/slide1_interactions.html`
- `html/slide4_interactions.html`
- `html/slide5_interactions.html`
- `html/slide4_template.html`
- `html/merged_report.html`
- `html/final_report.html`
- `html/complete_report.html`

#### Python Files (9 files)
- `merge_slides.py` - Main slide merger
- `core/pdf_exporter.py` - PDF export module
- `core/pdf_exporter_temp.py` - Temporary PDF exporter
- `test_generate.py` - Test generator
- `html/merge_slides.py`
- `html/merge_slides_simple.py`
- `html/merge_final.py`
- `html/simple_merge_pdf.py`
- `html/merge_and_export_pdf.py`

### Thay đổi cụ thể:

1. **Font CDN Link:**
   - Cũ: `https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap`
   - Mới: `https://fonts.cdnfonts.com/css/product-sans`

2. **Font Family:**
   - Cũ: `'Inter', sans-serif` hoặc `'Roboto', sans-serif`
   - Mới: `'Product Sans', sans-serif`

### Files trong output/ folder

Các file HTML đã được tạo trong thư mục `output/` vẫn sử dụng font cũ. 
Những file này sẽ được tạo lại tự động khi bạn:
- Chạy Streamlit app và tạo report mới
- Chạy script merge_slides.py
- Export PDF mới

### Lưu ý quan trọng:

⚠️ **Font SVN Product Sans** hiện đang sử dụng CDN Fonts (https://fonts.cdnfonts.com).

Nếu bạn muốn sử dụng font file local:
1. Download font SVN Product Sans (.ttf hoặc .woff2)
2. Đặt vào thư mục `fonts/` trong project
3. Cập nhật link font trong các file template:
   ```html
   <style>
   @font-face {
       font-family: 'Product Sans';
       src: url('fonts/ProductSans-Regular.woff2') format('woff2');
       font-weight: 400;
   }
   @font-face {
       font-family: 'Product Sans';
       src: url('fonts/ProductSans-Bold.woff2') format('woff2');
       font-weight: 700;
   }
   </style>
   ```

### Kiểm tra thay đổi:

```bash
# Kiểm tra HTML templates
grep -r "Product Sans" html/ --include="*.html" | wc -l

# Kiểm tra Python files
grep -r "Product Sans" *.py core/*.py | wc -l

# Kiểm tra không còn font cũ
grep -r "googleapis.com" html/ --include="*.html" | wc -l
```

### Tạo lại output files:

Để tạo lại các file output với font mới:
```bash
# Chạy Streamlit app
streamlit run app_template_html.py

# Hoặc chạy script merge
python3 merge_slides.py
```

---
**Ngày cập nhật:** $(date)
**Script sử dụng:** `update_fonts.py`
