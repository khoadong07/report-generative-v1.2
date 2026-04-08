#!/usr/bin/env python3
"""
Streamlit App – Weekly Report HTML Generator
Tạo HTML slides từ JSON data và HTML templates
"""
import os
import json
import tempfile
import sys
from pathlib import Path
from datetime import datetime, timedelta, time
from dotenv import load_dotenv
import streamlit as st
import pandas as pd

# Setup paths
_ROOT = str(Path(__file__).resolve().parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

load_dotenv(Path(_ROOT) / '.env')
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

from weekly_report.orchestrator import WeeklyReportOrchestrator
from core.data_loader import DataLoader
from core.config import TEXT_COLUMNS, METRIC_COLUMNS
from merge_slides import SlideHTMLMerger

# ── Streamlit Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Weekly Report HTML Generator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""<style>
.block-container{padding-top:1.5rem;padding-bottom:1rem}
div[data-testid="stMetric"]{background:#f8f9fa;border-radius:8px;padding:10px}
.slide-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 1rem;
}
.slide-counter {
    font-size: 1.2rem;
    font-weight: 600;
    color: #0045c4;
}
.slide-preview-container {
    width: 100%;
    display: flex;
    justify-content: center;
    background: #e5e7eb;
    padding: 20px;
    border-radius: 8px;
    margin: 1rem 0;
}
.slide-preview-frame {
    border: 2px solid #ccc;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    background: white;
    border-radius: 4px;
}
</style>""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────────────────────────
for k, v in {
    "report_generated": False,
    "report_data": None,
    "html_files": {},
    "current_slide": 0,
    "date_range": ""
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helper Functions ───────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Đang đọc file...")
def load_excel(file_bytes: bytes) -> pd.DataFrame:
    import io
    return DataLoader(io.BytesIO(file_bytes), TEXT_COLUMNS, METRIC_COLUMNS).preprocess()

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 Weekly Report HTML")
    
    # API Check
    if not (API_KEY and BASE_URL):
        st.error("⚠️ Thiếu API credentials trong .env")
        st.stop()
    st.success("✅ API credentials OK", icon="✅")
    st.divider()
    
    # 1. Upload Data
    st.subheader("1. Upload dữ liệu")
    uploaded_file = st.file_uploader(
        "File Excel (.xlsx / .xls)",
        type=["xlsx", "xls"]
    )
    
    df_full, available_topics = None, []
    if uploaded_file:
        try:
            df_full = load_excel(uploaded_file.getvalue())
            available_topics = sorted(df_full["Topic"].dropna().unique().tolist())
            st.caption(f"✅ {len(df_full):,} dòng · {len(available_topics)} topics")
        except Exception as e:
            st.error(f"❌ Lỗi đọc file: {e}")
            st.stop()
    
    # 2. Brand Selection
    st.subheader("2. Thương hiệu")
    if available_topics:
        brand_name = st.selectbox("Brand chính", options=available_topics)
    else:
        brand_name = st.text_input(
            "Brand name (cột Topic)",
            placeholder="Nhập tên brand..."
        )
    
    # 3. Report Period
    st.subheader("3. Kỳ báo cáo")
    col_d, col_t = st.columns([3, 2])
    with col_d:
        report_date = st.date_input(
            "Ngày kết thúc",
            value=datetime.now()
        )
    with col_t:
        report_time = st.time_input("Giờ cắt", value=time(23, 59))
    
    week1_end = datetime.combine(report_date, report_time)
    week1_start = week1_end - timedelta(days=6)  # 7 days inclusive
    week2_end = week1_start - timedelta(seconds=1)
    week2_start = week2_end - timedelta(days=6)
    week3_end = week2_start - timedelta(seconds=1)
    week3_start = week3_end - timedelta(days=6)
    week4_end = week3_start - timedelta(seconds=1)
    week4_start = week4_end - timedelta(days=6)
    
    def _fmt(dt):
        return dt.strftime("%d/%m %H:%M")
    
    st.caption(
        f"W1: {_fmt(week1_start)} → {_fmt(week1_end)}  \n"
        f"W2: {_fmt(week2_start)} → {_fmt(week2_end)}  \n"
        f"W3: {_fmt(week3_start)} → {_fmt(week3_end)}  \n"
        f"W4: {_fmt(week4_start)} → {_fmt(week4_end)}"
    )
    
    # 4. Options
    st.subheader("4. Tuỳ chọn")
    show_interactions = st.toggle("Hiển thị Interactions", value=False)
    
    # 4.1. Competitor Selection (for slides 11-16)
    st.subheader("4.1. Đối thủ cạnh tranh")
    st.caption("Chọn đối thủ để phân tích so sánh (slide 11-16)")
    
    competitor_brands = []
    if available_topics:
        # Remove main brand from competitor list
        competitor_options = [t for t in available_topics if t != brand_name]
        competitor_brands = st.multiselect(
            "Chọn đối thủ",
            options=competitor_options,
            help="Chọn tối đa 5 đối thủ để so sánh"
        )
        if len(competitor_brands) > 5:
            st.warning("⚠️ Chỉ nên chọn tối đa 5 đối thủ để biểu đồ dễ đọc")
    
    # 5. Chọn slides cần build
    st.subheader("5. Chọn slides")
    st.caption("Chọn các slides bạn muốn tạo")
    
    # Buttons chọn/bỏ chọn tất cả
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("✅ Chọn tất cả", use_container_width=True):
            for i in range(1, 17):
                st.session_state[f"slide_{i}"] = True
            st.rerun()
    with col_btn2:
        if st.button("❌ Bỏ chọn tất cả", use_container_width=True):
            for i in range(1, 17):
                st.session_state[f"slide_{i}"] = False
            st.rerun()
    
    st.markdown("---")
    
    # Danh sách slides dạng list
    slide_1 = st.checkbox("Slide 1: Tổng quan", value=st.session_state.get("slide_1", True), key="slide_1")
    slide_2 = st.checkbox("Slide 2: Xu hướng", value=st.session_state.get("slide_2", True), key="slide_2")
    slide_3 = st.checkbox("Slide 3: Phân bổ kênh", value=st.session_state.get("slide_3", True), key="slide_3")
    slide_4 = st.checkbox("Slide 4: Top nguồn", value=st.session_state.get("slide_4", True), key="slide_4")
    slide_5 = st.checkbox("Slide 5: Top bài đăng", value=st.session_state.get("slide_5", True), key="slide_5")
    slide_6 = st.checkbox("Slide 6: Phân tích sắc thái", value=st.session_state.get("slide_6", True), key="slide_6")
    slide_7 = st.checkbox("Slide 7: Chủ đề tích cực", value=st.session_state.get("slide_7", True), key="slide_7")
    slide_8 = st.checkbox("Slide 8: Bài đăng tích cực", value=st.session_state.get("slide_8", True), key="slide_8")
    slide_9 = st.checkbox("Slide 9: Chủ đề tiêu cực", value=st.session_state.get("slide_9", True), key="slide_9")
    slide_10 = st.checkbox("Slide 10: Bài đăng tiêu cực", value=st.session_state.get("slide_10", True), key="slide_10")
    
    st.markdown("**Slides so sánh đối thủ:**")
    slide_11 = st.checkbox("Slide 11: So sánh thương hiệu", value=st.session_state.get("slide_11", False), disabled=not competitor_brands, key="slide_11")
    slide_12 = st.checkbox("Slide 12: Xếp hạng thương hiệu", value=st.session_state.get("slide_12", False), disabled=not competitor_brands, key="slide_12")
    slide_13 = st.checkbox("Slide 13: Xu hướng đối thủ", value=st.session_state.get("slide_13", False), disabled=not competitor_brands, key="slide_13")
    slide_14 = st.checkbox("Slide 14: Phân bổ kênh đối thủ", value=st.session_state.get("slide_14", False), disabled=not competitor_brands, key="slide_14")
    slide_15 = st.checkbox("Slide 15: Sắc thái theo chủ đề", value=st.session_state.get("slide_15", False), disabled=not competitor_brands, key="slide_15")
    slide_16 = st.checkbox("Slide 16: Top bài đăng nhiều bình luận", value=st.session_state.get("slide_16", False), disabled=not competitor_brands, key="slide_16")
    
    if not competitor_brands:
        st.caption("💡 Chọn đối thủ ở mục 4.1 để kích hoạt slide 11-16")
    
    # Count selected slides
    selected_slides = []
    if slide_1: selected_slides.append("slide_1")
    if slide_2: selected_slides.append("slide_2")
    if slide_3: selected_slides.append("slide_3")
    if slide_4: selected_slides.append("slide_4")
    if slide_5: selected_slides.append("slide_5")
    if slide_6: selected_slides.append("slide_6")
    if slide_7: selected_slides.append("slide_7")
    if slide_8: selected_slides.append("slide_8")
    if slide_9: selected_slides.append("slide_9")
    if slide_10: selected_slides.append("slide_10")
    if slide_11: selected_slides.append("slide_11")
    if slide_12: selected_slides.append("slide_12")
    if slide_13: selected_slides.append("slide_13")
    if slide_14: selected_slides.append("slide_14")
    if slide_15: selected_slides.append("slide_15")
    if slide_16: selected_slides.append("slide_16")
    
    if selected_slides:
        st.caption(f"✓ Đã chọn {len(selected_slides)} slide(s)")
    else:
        st.warning("⚠️ Vui lòng chọn ít nhất 1 slide")
    
    st.divider()
    
    # Generate Button
    can_generate = bool(uploaded_file and brand_name and selected_slides)
    generate_btn = st.button(
        f"🚀 Tạo HTML Slides ({len(selected_slides)} slide{'s' if len(selected_slides) > 1 else ''})",
        disabled=not can_generate,
        type="primary",
        use_container_width=True
    )
    
    if st.button("🔄 Reset", use_container_width=True):
        st.cache_data.clear()
        st.session_state.update(
            report_generated=False,
            report_data=None,
            html_files={}
        )
        st.rerun()

# ── MAIN CONTENT ───────────────────────────────────────────────────────────────
if not can_generate:
    st.info("👈 Upload file và chọn brand để bắt đầu.", icon="ℹ️")
    st.stop()

# ── GENERATE REPORT ────────────────────────────────────────────────────────────
if generate_btn:
    st.session_state.report_generated = False
    st.session_state.html_files = {}
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name
    
    try:
        with st.status("Đang tạo báo cáo...", expanded=True) as status:
            # Step 1: Generate JSON data
            st.write("⚙️ Khởi tạo orchestrator...")
            orch = WeeklyReportOrchestrator(
                api_key=API_KEY,
                base_url=BASE_URL,
                file_path=tmp_path,
                brand_name=brand_name,
                week1_end=week1_end.strftime("%Y-%m-%d %H:%M:%S"),
                week2_end=week2_end.strftime("%Y-%m-%d %H:%M:%S"),
                week3_end=week3_end.strftime("%Y-%m-%d %H:%M:%S"),
                week4_end=week4_end.strftime("%Y-%m-%d %H:%M:%S"),
                show_interactions=show_interactions,
                competitor_brands=competitor_brands if competitor_brands else None,
                has_logo=False
            )
            
            st.write(f"📊 Đang build {len(selected_slides)} slide(s)...")
            report_data = orch.generate_slides(selected_slides)
            st.session_state.report_data = report_data
            
            # Step 2: Merge into HTML
            st.write("🎨 Đang merge data vào HTML templates...")
            merger = SlideHTMLMerger(html_dir="html", output_dir="output")
            
            # Format date range - FIX: Use correct week1_start
            date_range = f"{week1_start.strftime('%d/%m/%Y')} → {week1_end.strftime('%d/%m/%Y')}"
            st.session_state.date_range = date_range
            
            # Merge selected slides
            if "slide_1" in selected_slides:
                html1 = merger.merge_slide01(report_data["slide_1"], date_range)
                path1 = merger.save_html(html1, "slide1_merged.html")
                st.session_state.html_files["slide_1"] = {
                    "path": str(path1),
                    "html": html1,
                    "title": "Slide 1: Tổng quan"
                }
            
            if "slide_2" in selected_slides:
                html2 = merger.merge_slide02(report_data["slide_2"], date_range)
                path2 = merger.save_html(html2, "slide2_merged.html")
                st.session_state.html_files["slide_2"] = {
                    "path": str(path2),
                    "html": html2,
                    "title": "Slide 2: Xu hướng"
                }
            
            if "slide_3" in selected_slides:
                html3 = merger.merge_slide03(report_data["slide_3"], date_range)
                path3 = merger.save_html(html3, "slide3_merged.html")
                st.session_state.html_files["slide_3"] = {
                    "path": str(path3),
                    "html": html3,
                    "title": "Slide 3: Phân bổ kênh"
                }
            
            if "slide_4" in selected_slides:
                html4 = merger.merge_slide04(report_data["slide_4"], date_range)
                path4 = merger.save_html(html4, "slide4_merged.html")
                st.session_state.html_files["slide_4"] = {
                    "path": str(path4),
                    "html": html4,
                    "title": "Slide 4: Top nguồn"
                }
            
            if "slide_5" in selected_slides:
                html5 = merger.merge_slide05(report_data["slide_5"], date_range)
                path5 = merger.save_html(html5, "slide5_merged.html")
                st.session_state.html_files["slide_5"] = {
                    "path": str(path5),
                    "html": html5,
                    "title": "Slide 5: Top bài đăng"
                }
            
            if "slide_6" in selected_slides:
                html6 = merger.merge_slide06(report_data["slide_6"], date_range)
                path6 = merger.save_html(html6, "slide6_merged.html")
                st.session_state.html_files["slide_6"] = {
                    "path": str(path6),
                    "html": html6,
                    "title": "Slide 6: Phân tích sắc thái"
                }
            
            if "slide_7" in selected_slides:
                html7 = merger.merge_slide07(report_data["slide_7"], date_range)
                path7 = merger.save_html(html7, "slide7_merged.html")
                st.session_state.html_files["slide_7"] = {
                    "path": str(path7),
                    "html": html7,
                    "title": "Slide 7: Chủ đề tích cực"
                }
            
            if "slide_8" in selected_slides:
                html8 = merger.merge_slide08(report_data["slide_8"], date_range)
                path8 = merger.save_html(html8, "slide8_merged.html")
                st.session_state.html_files["slide_8"] = {
                    "path": str(path8),
                    "html": html8,
                    "title": "Slide 8: Bài đăng tích cực"
                }
            
            if "slide_9" in selected_slides:
                html9 = merger.merge_slide09(report_data["slide_9"], date_range)
                path9 = merger.save_html(html9, "slide9_merged.html")
                st.session_state.html_files["slide_9"] = {
                    "path": str(path9),
                    "html": html9,
                    "title": "Slide 9: Chủ đề tiêu cực"
                }
            
            if "slide_10" in selected_slides:
                html10 = merger.merge_slide10(report_data["slide_10"], date_range)
                path10 = merger.save_html(html10, "slide10_merged.html")
                st.session_state.html_files["slide_10"] = {
                    "path": str(path10),
                    "html": html10,
                    "title": "Slide 10: Bài đăng tiêu cực"
                }
            
            # Competitor slides (11-16) - chỉ merge nếu có đối thủ
            if competitor_brands:
                if "slide_11" in selected_slides and "slide_11" in report_data:
                    html11 = merger.merge_slide11(report_data["slide_11"], date_range)
                    path11 = merger.save_html(html11, "slide11_merged.html")
                    st.session_state.html_files["slide_11"] = {
                        "path": str(path11),
                        "html": html11,
                        "title": "Slide 11: So sánh thương hiệu"
                    }
                
                if "slide_12" in selected_slides and "slide_12" in report_data:
                    html12 = merger.merge_slide12(report_data["slide_12"], date_range)
                    path12 = merger.save_html(html12, "slide12_merged.html")
                    st.session_state.html_files["slide_12"] = {
                        "path": str(path12),
                        "html": html12,
                        "title": "Slide 12: Xếp hạng thương hiệu"
                    }
                
                if "slide_13" in selected_slides and "slide_13" in report_data:
                    html13 = merger.merge_slide13(report_data["slide_13"], date_range)
                    path13 = merger.save_html(html13, "slide13_merged.html")
                    st.session_state.html_files["slide_13"] = {
                        "path": str(path13),
                        "html": html13,
                        "title": "Slide 13: Xu hướng đối thủ"
                    }
                
                if "slide_14" in selected_slides and "slide_14" in report_data:
                    html14 = merger.merge_slide14(report_data["slide_14"], date_range)
                    path14 = merger.save_html(html14, "slide14_merged.html")
                    st.session_state.html_files["slide_14"] = {
                        "path": str(path14),
                        "html": html14,
                        "title": "Slide 14: Phân bổ kênh đối thủ"
                    }
                
                if "slide_15" in selected_slides and "slide_15" in report_data:
                    html15 = merger.merge_slide15(report_data["slide_15"], date_range)
                    path15 = merger.save_html(html15, "slide15_merged.html")
                    st.session_state.html_files["slide_15"] = {
                        "path": str(path15),
                        "html": html15,
                        "title": "Slide 15: Sắc thái theo chủ đề"
                    }
                
                if "slide_16" in selected_slides and "slide_16" in report_data:
                    html16 = merger.merge_slide16(report_data["slide_16"], date_range)
                    path16 = merger.save_html(html16, "slide16_merged.html")
                    st.session_state.html_files["slide_16"] = {
                        "path": str(path16),
                        "html": html16,
                        "title": "Slide 16: Top bài đăng nhiều bình luận"
                    }
            
            st.session_state.report_generated = True
            st.session_state.current_slide = 0
            status.update(label="✅ Hoàn thành!", state="complete")
            
    except Exception as e:
        st.error(f"❌ Lỗi: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

# ── DISPLAY RESULTS ────────────────────────────────────────────────────────────
if not st.session_state.report_generated:
    st.stop()

data = st.session_state.report_data
html_files = st.session_state.html_files
date_range = st.session_state.date_range

# ── SLIDE NAVIGATION ───────────────────────────────────────────────────────────
slide_keys = list(html_files.keys())
total_slides = len(slide_keys)

if total_slides > 0:
    # Navigation header with date range
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_left:
        if st.button("⬅️ Previous", disabled=st.session_state.current_slide == 0, use_container_width=True):
            st.session_state.current_slide = max(0, st.session_state.current_slide - 1)
            st.rerun()
    
    with col_center:
        st.markdown(
            f'<div style="text-align: center; padding: 0.5rem;">'
            f'<div style="font-size: 1.5rem; font-weight: 700; color: #111827;">{brand_name}</div>'
            f'<div style="font-size: 1rem; color: #0045c4; font-weight: 600;">{date_range}</div>'
            f'<div style="font-size: 0.9rem; color: #6b7280;">Slide {st.session_state.current_slide + 1} / {total_slides}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col_right:
        if st.button("Next ➡️", disabled=st.session_state.current_slide >= total_slides - 1, use_container_width=True):
            st.session_state.current_slide = min(total_slides - 1, st.session_state.current_slide + 1)
            st.rerun()
    
    st.divider()
    
    # Slide thumbnail navigator
    st.markdown("**Chuyển nhanh đến slide:**")
    cols = st.columns(min(len(slide_keys), 8))
    for idx, key in enumerate(slide_keys):
        col_idx = idx % 8
        with cols[col_idx]:
            is_current = idx == st.session_state.current_slide
            button_type = "primary" if is_current else "secondary"
            if st.button(
                f"{'📍' if is_current else ''} {idx + 1}",
                key=f"nav_{key}",
                use_container_width=True,
                type=button_type if is_current else "secondary"
            ):
                st.session_state.current_slide = idx
                st.rerun()
    
    st.divider()
    
    # Display current slide
    current_key = slide_keys[st.session_state.current_slide]
    current_slide = html_files[current_key]
    
    # Show slide title and view options
    col_title, col_view = st.columns([3, 1])
    with col_title:
        st.subheader(current_slide["title"])
    with col_view:
        view_mode = st.radio(
            "Chế độ xem",
            ["1280x720 (Gốc)", "Fit to screen"],
            horizontal=True,
            label_visibility="collapsed"
        )
    
    # Show HTML preview based on view mode
    if view_mode == "1280x720 (Gốc)":
        st.components.v1.html(
            f"""
            <div style="width: 100%; display: flex; justify-content: center; background: #e5e7eb; padding: 20px; border-radius: 8px;">
                <iframe srcdoc='{current_slide["html"].replace("'", "&apos;")}' 
                        style="width: 1280px; height: 720px; border: 2px solid #ccc; box-shadow: 0 4px 12px rgba(0,0,0,0.15); background: white; border-radius: 4px;">
                </iframe>
            </div>
            """,
            height=760,
            scrolling=False
        )
    else:
        # Fit to screen mode - scale to fit container
        st.components.v1.html(
            f"""
            <div style="width: 100%; background: #e5e7eb; padding: 20px; border-radius: 8px;">
                <iframe srcdoc='{current_slide["html"].replace("'", "&apos;")}' 
                        style="width: 100%; height: 720px; border: 2px solid #ccc; box-shadow: 0 4px 12px rgba(0,0,0,0.15); background: white; border-radius: 4px;">
                </iframe>
            </div>
            """,
            height=760,
            scrolling=False
        )
    
    # Download section
    st.divider()
    col_dl1, col_dl2, col_dl3, col_dl4, col_dl5 = st.columns(5)
    
    with col_dl1:
        st.download_button(
            label=f"⬇️ Tải {current_slide['title']}",
            data=current_slide["html"],
            file_name=f"{brand_name}_{current_key}_{report_date:%Y%m%d}.html",
            mime="text/html",
            use_container_width=True
        )
    
    with col_dl2:
        if current_key in data:
            st.download_button(
                label="⬇️ Tải JSON data",
                data=json.dumps(data[current_key], ensure_ascii=False, indent=2),
                file_name=f"{brand_name}_{current_key}_{report_date:%Y%m%d}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col_dl3:
        # Download merged HTML (all slides in one page)
        merger = SlideHTMLMerger()
        merged_html = merger.merge_all_slides(data, slide_keys, date_range)
        st.download_button(
            label="📄 Tải HTML tổng hợp",
            data=merged_html,
            file_name=f"{brand_name}_complete_{report_date:%Y%m%d}.html",
            mime="text/html",
            use_container_width=True,
            help="Tất cả slides trong 1 file HTML"
        )
    
    with col_dl4:
        # Download all slides as ZIP
        if st.button("📦 Tải ZIP", use_container_width=True):
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for key, slide_data in html_files.items():
                    zip_file.writestr(
                        f"{brand_name}_{key}_{report_date:%Y%m%d}.html",
                        slide_data["html"]
                    )
            
            st.download_button(
                label="⬇️ Tải file ZIP",
                data=zip_buffer.getvalue(),
                file_name=f"{brand_name}_slides_{report_date:%Y%m%d}.zip",
                mime="application/zip",
                use_container_width=True
            )
    
    with col_dl5:
        # Export all slides as PDF
        if st.button("📄 Export PDF", use_container_width=True, type="primary"):
            with st.spinner("Đang tạo PDF từ tất cả slides..."):
                try:
                    import io
                    
                    # Merge all slides into one HTML
                    merger = SlideHTMLMerger()
                    merged_html = merger.merge_all_slides(data, slide_keys, date_range)
                    
                    # Try to convert to PDF
                    pdf_bytes = None
                    method_used = None
                    
                    # Method 1: Try weasyprint (recommended)
                    try:
                        from weasyprint import HTML
                        pdf_buffer = io.BytesIO()
                        HTML(string=merged_html).write_pdf(pdf_buffer)
                        pdf_bytes = pdf_buffer.getvalue()
                        method_used = "weasyprint"
                    except ImportError:
                        pass
                    except Exception as e:
                        st.warning(f"Weasyprint failed: {e}")
                    
                    # Method 2: Try pdfkit if weasyprint not available
                    if pdf_bytes is None:
                        try:
                            import pdfkit
                            pdf_bytes = pdfkit.from_string(merged_html, False, options={
                                'page-size': 'A4',
                                'orientation': 'Landscape',
                                'margin-top': '0',
                                'margin-right': '0',
                                'margin-bottom': '0',
                                'margin-left': '0',
                                'encoding': 'UTF-8',
                                'enable-local-file-access': None,
                                'no-stop-slow-scripts': None,
                            })
                            method_used = "pdfkit"
                        except ImportError:
                            pass
                        except Exception as e:
                            st.warning(f"Pdfkit failed: {e}")
                    
                    # If PDF conversion succeeded
                    if pdf_bytes:
                        st.download_button(
                            "⬇️ Tải PDF",
                            pdf_bytes,
                            file_name=f"{brand_name}_report_{report_date:%Y%m%d}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                        st.success(f"✅ PDF đã sẵn sàng! (sử dụng {method_used})")
                    else:
                        # Fallback: download merged HTML
                        st.warning("⚠️ Không thể tạo PDF. Cài đặt: pip install weasyprint")
                        st.download_button(
                            "⬇️ Tải HTML đầy đủ (fallback)",
                            merged_html,
                            file_name=f"{brand_name}_report_{report_date:%Y%m%d}.html",
                            mime="text/html",
                            use_container_width=True,
                        )
                        
                except Exception as e:
                    st.error(f"Lỗi tạo PDF: {e}")
                    import traceback
                    st.code(traceback.format_exc())

else:
    st.warning("Không có slides để hiển thị")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "💡 **Hướng dẫn:** Upload file Excel → Chọn brand → Click 'Tạo HTML Slides' → "
    "Xem preview và tải xuống HTML files từ tab Downloads"
)
