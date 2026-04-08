# Hướng dẫn xem báo cáo HTML & Xuất PDF

## 📊 Xem báo cáo

### Vấn đề CORS

Khi mở file `complete_report.html` trực tiếp từ trình duyệt (file://), bạn sẽ gặp lỗi CORS vì trình duyệt không cho phép fetch các file local khác.

### Giải pháp

Sử dụng một trong các cách sau để xem báo cáo:

#### Cách 1: Sử dụng Python HTTP Server (Khuyến nghị)

```bash
# Từ thư mục html, chạy:
python serve.py

# Hoặc sử dụng Python built-in server:
python -m http.server 8000

# Sau đó mở trình duyệt tại:
# http://localhost:8000/complete_report.html
```

#### Cách 2: Sử dụng Node.js http-server

```bash
# Cài đặt (nếu chưa có):
npm install -g http-server

# Chạy từ thư mục html:
http-server -p 8000

# Mở: http://localhost:8000/complete_report.html
```

#### Cách 3: Sử dụng VS Code Live Server

1. Cài extension "Live Server" trong VS Code
2. Click chuột phải vào file `complete_report.html`
3. Chọn "Open with Live Server"

#### Cách 4: Xem từng slide riêng lẻ

Nếu không muốn chạy server, bạn có thể mở từng file slide riêng lẻ:
- `slide1.html`
- `slide2.html`
- ...
- `slide16.html`

Các file này có thể mở trực tiếp từ trình duyệt mà không gặp lỗi CORS.

## 📄 Xuất PDF

### Bước 1: Merge tất cả slides thành 1 file HTML

```bash
cd html
python merge_slides.py
# Tạo file merged_report.html
```

Hoặc sử dụng Makefile:

```bash
cd html
make merge
```

### Bước 2: Xuất PDF

#### Option 1: Sử dụng Playwright (Khuyến nghị - chất lượng tốt nhất)

```bash
# Cài đặt
pip install playwright
playwright install chromium

# Xuất PDF
python export_pdf.py
# Tạo file complete_report.pdf
```

Hoặc:

```bash
make install-playwright
make pdf
```

#### Option 2: Sử dụng WeasyPrint (Đơn giản hơn)

```bash
# Cài đặt
pip install weasyprint

# Xuất PDF
python export_pdf_weasyprint.py
# Tạo file complete_report_weasyprint.pdf
```

Hoặc:

```bash
make install-weasyprint
make pdf-weasyprint
```

#### Option 3: In từ trình duyệt (Thủ công)

1. Chạy `python merge_slides.py` để tạo `merged_report.html`
2. Mở `merged_report.html` trong Chrome/Firefox
3. Nhấn `Ctrl+P` (Windows/Linux) hoặc `Cmd+P` (Mac)
4. Chọn "Save as PDF"
5. Cài đặt:
   - Layout: **Landscape** (Ngang)
   - Margins: **None** (Không lề)
   - Background graphics: **On** (Bật)
   - Scale: **100%**

## 🛠️ Makefile Commands

```bash
make help                # Hiển thị tất cả lệnh
make merge               # Merge tất cả slides thành 1 HTML
make pdf                 # Merge và xuất PDF (Playwright)
make pdf-playwright      # Xuất PDF bằng Playwright
make pdf-weasyprint      # Xuất PDF bằng WeasyPrint
make serve               # Chạy web server
make clean               # Xóa các file đã tạo
```

## 📦 Cài đặt dependencies

```bash
# Cài tất cả dependencies cho PDF export
pip install -r requirements_pdf.txt

# Nếu dùng Playwright, cần cài thêm browser
playwright install chromium
```

## 📁 Cấu trúc file

- `complete_report.html` - Báo cáo hoàn chỉnh (load động 16 slides)
- `merged_report.html` - Báo cáo đã merge (tạo bởi merge_slides.py)
- `slide1.html` đến `slide16.html` - Các slide riêng lẻ
- `serve.py` - Script Python để chạy web server
- `merge_slides.py` - Script merge tất cả slides
- `export_pdf.py` - Script xuất PDF bằng Playwright
- `export_pdf_weasyprint.py` - Script xuất PDF bằng WeasyPrint
- `Makefile` - Shortcuts cho các lệnh thường dùng

## 📝 Ghi chú

- **Playwright**: Chất lượng tốt nhất, sử dụng browser thật để render
- **WeasyPrint**: Đơn giản hơn, không cần browser, nhưng có thể khác biệt về rendering
- **Browser Print**: Cho phép kiểm soát tốt nhất, nhưng phải làm thủ công
- Tất cả slides có kích thước 1280x720px (tỷ lệ 16:9)
