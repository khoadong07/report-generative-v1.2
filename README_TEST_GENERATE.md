# Test Generate - Merge HTML & Convert to PDF

Script để merge toàn bộ 16 slides (slide1_merged.html đến slide16_merged.html) thành 1 file HTML duy nhất và convert sang PDF.

## Có 2 phiên bản:

### 1. Python Version (`test_generate.py`)

**Cài đặt dependencies:**
```bash
pip install playwright beautifulsoup4
playwright install chromium
```

**Chạy script:**
```bash
python test_generate.py
```

### 2. Node.js Version (`test_generate.js`)

**Cài đặt dependencies:**
```bash
npm install
# hoặc
npm install puppeteer cheerio
```

**Chạy script:**
```bash
node test_generate.js
# hoặc
npm test
```

## Output

Script sẽ tạo ra 2 files trong thư mục `output/`:
- `merged_slides.html` - File HTML đã merge 2 slides
- `merged_slides.pdf` - File PDF được convert từ HTML

## Tính năng

- ✅ Merge toàn bộ 16 slides (slide1_merged.html đến slide16_merged.html) thành 1 file duy nhất
- ✅ Tự động bỏ qua các slide không tồn tại
- ✅ Giữ nguyên styling và layout
- ✅ Xử lý Chart.js charts (tránh conflict ID)
- ✅ Convert sang PDF với kích thước 1280x720px
- ✅ Page break giữa các slides
- ✅ Print background colors và images

## Yêu cầu

- Python 3.7+ (cho Python version) hoặc Node.js 14+ (cho Node.js version)
- Chromium browser (được cài tự động qua playwright/puppeteer)
