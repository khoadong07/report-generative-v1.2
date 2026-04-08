# Cập nhật hỗ trợ cột Interactions

## Tổng quan
Hệ thống đã được cập nhật để hỗ trợ cột `Interactions` trong data Excel, đồng thời vẫn tương thích ngược với data không có cột này.

## Logic xử lý

### 1. Tính toán Engagement (core/data_loader.py)
```python
def calculate_engagement(df):
    # Ưu tiên 1: Dùng cột Interactions nếu có
    if "Interactions" in df.columns:
        return df["Interactions"]
    
    # Ưu tiên 2: Tính từ Reactions + Shares + Comments
    return Reactions + Shares + Comments
```

### 2. Slide 01 - Overview

**Khi có cột Interactions:**
- Hiển thị đầy đủ metrics (có thể 6+ KPIs):
  1. Tổng đề cập (so với tuần trước)
  2. Tổng tương tác (từ cột Interactions, so với tuần trước)
  3. Tổng lượt xem (nếu có, so với tuần trước)
  4. Lượt reactions (nếu có, so với tuần trước)
  5. Lượt chia sẻ (nếu có, so với tuần trước)
  6. Lượt bình luận (nếu có, so với tuần trước)

**Khi không có Interactions:**
- Hiển thị 6 KPIs: Tổng đề cập, Tổng tương tác (tính từ R+S+C), Lượt xem, Reactions, Shares, Comments

**Khi show_interactions=False:**
- Hiển thị 3 KPIs cơ bản: Tổng bài đăng, Tổng bình luận, Tổng thảo luận

**Lưu ý về HTML template:**
- HTML template chỉ có 3 metric cards (giới hạn layout)
- Hiển thị 3 metrics quan trọng nhất: Tổng đề cập, Tổng tương tác, Tổng lượt xem
- UI Streamlit hiển thị đầy đủ tất cả metrics

### 3. Slide 04 - Top Sources

**Khi có cột Interactions:**
- Bảng: STT | Nguồn | Tổng tương tác
- Giá trị: Tổng từ cột Interactions

**Khi có Reactions/Shares/Comments:**
- Bảng: STT | Nguồn | Tổng tương tác
- Hiển thị breakdown: R: xxx | S: xxx | C: xxx (dòng phụ)

**Khi show_interactions=False:**
- Bảng: STT | Nguồn | Số lượng đề cập

### 4. Slide 05 - Top Posts

**Khi có cột Interactions:**
- Sort theo Interactions
- Hiển thị: STT | Nội dung | Ngày | Kênh | Nguồn | Interactions | Link

**Khi có Reactions/Shares/Comments:**
- Sort theo Comments
- Hiển thị: STT | Nội dung | Ngày | Kênh | Nguồn | R/S/C | Link

**Khi show_interactions=False:**
- Chỉ hiển thị: STT | Nội dung | Ngày | Kênh | Nguồn | Link

## Files đã cập nhật

### Core
- ✅ `core/data_loader.py` - Hàm calculate_engagement()
- ✅ `core/config.py` - Thêm "Interactions" vào METRIC_COLUMNS

### Slides
- ✅ `weekly_report/slides/slide01_overview.py` - Logic KPIs với đầy đủ metrics
  - Khi có Interactions: hiển thị 6+ metrics (Tổng đề cập, Tổng tương tác, Views, Reactions, Shares, Comments)
  - Khi không có: hiển thị 6 metrics (tính tổng từ R+S+C)
- ✅ `weekly_report/slides/slide04_top_sources.py` - Logic top sources
- ✅ `weekly_report/slides/slide05_top_posts.py` - Logic top posts

### Templates & UI
- ✅ `weekly_report/prompt_builder.py` - Template prompts (tự động xử lý tất cả metrics)
- ✅ `weekly_report/app.py` - Streamlit UI (tự động hiển thị tất cả metrics)
- ✅ `interfaces/app_weekly.py` - Streamlit UI (weekly) (tự động hiển thị tất cả metrics)
- ✅ `merge_slides.py` - HTML template merging
  - `merge_slide01()` - Detect và chọn template phù hợp (3-card hoặc 6-card)
  - `_generate_table_rows_slide04()` - Xử lý bảng slide 4
  - `_generate_table_rows_slide05()` - Xử lý bảng slide 5
- ✅ `html/slide1.html` - Template gốc với 3 metric cards
- ✅ `html/slide1_interactions.html` - Template mới với 6 metric cards (2 cột x 3 hàng)

## Cách test

### 1. Tạo data demo với Interactions
```bash
python seed_interactions.py demo/bidv-092025.xlsx -o demo/bidv_demo.xlsx
```

Script sẽ tạo các cột:
- `Reactions` (0-250)
- `Shares` (0-250)
- `Comments` (0-250)
- `Interactions` (0-250) - cột riêng biệt

### 2. Chạy report với data có Interactions
```bash
streamlit run weekly_report/app.py
```
- Chọn file: `demo/bidv_demo.xlsx`
- Bật "Hiển thị Interactions"
- Generate report

### 3. Kiểm tra output

**Slide 1 - Overview:**
- UI Streamlit: Nên hiển thị 6 metrics (Tổng đề cập, Tổng tương tác, Tổng lượt xem, Reactions, Shares, Comments)
- HTML export: Hiển thị 3 metrics quan trọng nhất
- Tất cả metrics đều có % thay đổi so với tuần trước

**Slide 4 - Top Sources:**
- Xem bảng top sources
- Nếu có Interactions: hiển thị giá trị Interactions
- Nếu có R/S/C: hiển thị breakdown

**Slide 5 - Top Posts:**
- Xem bảng top posts
- Nếu có Interactions: sort theo Interactions, hiển thị giá trị
- Nếu có R/S/C: sort theo Comments, hiển thị R/S/C

## Backward Compatibility

✅ Data không có cột Interactions vẫn hoạt động bình thường
✅ show_interactions=False vẫn hoạt động như cũ
✅ Không breaking changes với code cũ
✅ UI tự động điều chỉnh số lượng columns theo số metrics

## Ví dụ Output

### Khi có cột Interactions (6 metrics) - HTML Export:
```
Slide 1 (slide1_interactions.html):
┌──────────────────────────────────────────────────────────────┐
│ Chart (trái)          │  6 Metric Cards (phải, 2x3 grid)    │
│                       │  ┌──────────┬──────────┐             │
│ So sánh 4 tuần        │  │ Tổng đề  │ Tổng     │             │
│                       │  │ cập      │ tương    │             │
│ [Bar Chart]           │  │ 1,234    │ tác      │             │
│                       │  │ (+5.2%)  │ 5,678    │             │
│                       │  │          │ (+12.3%) │             │
│                       │  ├──────────┼──────────┤             │
│                       │  │ Tổng     │ Lượt     │             │
│                       │  │ lượt xem │ reactions│             │
│                       │  │ 45,678   │ 2,345    │             │
│                       │  │ (+8.1%)  │ (+10.5%) │             │
│                       │  ├──────────┼──────────┤             │
│                       │  │ Lượt     │ Lượt     │             │
│                       │  │ chia sẻ  │ bình luận│             │
│                       │  │ 1,234    │ 2,099    │             │
│                       │  │ (+15.2%) │ (+9.8%)  │             │
│                       │  └──────────┴──────────┘             │
└──────────────────────────────────────────────────────────────┘
```

### Khi có cột Interactions (6 metrics) - UI Streamlit:
```
Slide 1:
┌─────────────────┬─────────────────┬─────────────────┐
│ Tổng đề cập     │ Tổng tương tác  │ Tổng lượt xem   │
│ 1,234 (+5.2%)   │ 5,678 (+12.3%)  │ 45,678 (+8.1%)  │
└─────────────────┴─────────────────┴─────────────────┘
┌─────────────────┬─────────────────┬─────────────────┐
│ Lượt reactions  │ Lượt chia sẻ    │ Lượt bình luận  │
│ 2,345 (+10.5%)  │ 1,234 (+15.2%)  │ 2,099 (+9.8%)   │
└─────────────────┴─────────────────┴─────────────────┘
```

### Khi không có Interactions (6 metrics) - HTML Export:
```
Slide 1 (slide1.html):
┌──────────────────────────────────────────────────────────────┐
│ Chart (trái)          │  3 Metric Cards (phải, stacked)     │
│                       │  ┌────────────────────┐             │
│ So sánh 4 tuần        │  │ Tổng đề cập        │             │
│                       │  │ 1,234 (+5.2%)      │             │
│ [Bar Chart]           │  └────────────────────┘             │
│                       │  ┌────────────────────┐             │
│                       │  │ Tổng tương tác     │             │
│                       │  │ 5,678 (+12.3%)     │             │
│                       │  │ (R+S+C)            │             │
│                       │  └────────────────────┘             │
│                       │  ┌────────────────────┐             │
│                       │  │ Tổng lượt xem      │             │
│                       │  │ 45,678 (+8.1%)     │             │
│                       │  └────────────────────┘             │
└──────────────────────────────────────────────────────────────┘
```

### Khi show_interactions=False (3 metrics):
```
Slide 1:
┌─────────────────┬─────────────────┬─────────────────┐
│ Tổng thảo luận  │ Tổng bài đăng   │ Tổng bình luận  │
│ 1,234 (+5.2%)   │ 890 (+3.1%)     │ 344 (+8.5%)     │
└─────────────────┴─────────────────┴─────────────────┘
```

## Notes

- Cột `Interactions` là optional, không bắt buộc
- Nếu có cả `Interactions` và `Reactions/Shares/Comments`, ưu tiên dùng `Interactions` cho tổng tương tác
- Vẫn hiển thị breakdown R/S/C nếu các cột này tồn tại
- UI tự động detect và hiển thị phù hợp
- HTML templates tự động điều chỉnh layout
- Tất cả metrics đều tính % thay đổi so với tuần trước
