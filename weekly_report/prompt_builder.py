#!/usr/bin/env python3
"""
Tạo prompt hoàn chỉnh cho nền tảng slide từ dữ liệu báo cáo tuần.
Đầu vào: report_data dict (có thể chứa một tập con các slide)
Đầu ra: Chuỗi prompt chỉ nhúng các slide đã được build
"""

import json
from datetime import datetime
import pandas as pd


def format_number(num):
    if isinstance(num, (int, float)):
        return f"{int(num):,}"
    return str(num)


def format_date(date_str):
    if isinstance(date_str, str):
        for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"]:
            try:
                return datetime.strptime(date_str, fmt).strftime("%d/%m/%Y")
            except ValueError:
                continue
        try:
            return pd.to_datetime(date_str).strftime("%d/%m/%Y")
        except Exception:
            return str(date_str)
    return date_str.strftime("%d/%m/%Y")


def _header(title):
    return (
        "----------------------------------------------------------------\n"
        f"{title}\n"
        "----------------------------------------------------------------\n\n"
    )


def generate_complete_prompt(report_data):
    metadata    = report_data.get("report_metadata", {})
    brand       = metadata.get("brand", "")
    has_logo    = metadata.get("has_logo", False)
    week1_period = metadata.get("week1_period", "")

    show_interactions = True
    for k in ("slide_1", "slide_4", "slide_5"):
        if k in report_data:
            show_interactions = report_data[k].get("show_interactions", True)
            break

    built      = [k for k in report_data if k.startswith("slide_")]
    built_nums = sorted(int(k.split("_")[1]) for k in built)

    prompt  = f"Tạo bản trình bày chuyên nghiệp {len(built_nums)} slide cho Báo cáo Sức khoẻ Thương hiệu Tuần:\n\n"
    prompt += "===============================================================\n"
    prompt += f"THƯƠNG HIỆU: {brand.upper()}\n"
    prompt += f"KỲ BÁO CÁO: {week1_period} (7 ngày)\n"
    prompt += "LOẠI BÁO CÁO: Phân tích Tuần\n"
    prompt += "===============================================================\n\n"

    # ── SLIDE 1 ───────────────────────────────────────────────────────────────
    if "slide_1" in report_data:
        s = report_data["slide_1"]
        prompt += _header("SLIDE 1 - TỔNG QUAN VỀ THƯƠNG HIỆU")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        if show_interactions:
            prompt += (
                "BỐ CỤC: 2 CỘT\n"
                "  TRÁI (50%): Biểu đồ cột so sánh 4 tuần\n"
                "  PHẢI (50%): Lưới 6 thẻ KPI (2 hàng x 3 cột)\n"
                "  DƯỚI: Khung nhận định\n\n"
            )
        else:
            prompt += (
                "BỐ CỤC: 2 CỘT\n"
                "  TRÁI (50%): Biểu đồ cột so sánh 4 tuần\n"
                "  PHẢI (50%): 3 thẻ KPI (Tổng bài đăng, Tổng bình luận, Tổng thảo luận)\n"
                "  DƯỚI: Khung nhận định\n\n"
            )
        prompt += "CHỈ SỐ TUẦN HIỆN TẠI:\n"
        for m in s["current_week_metrics"]:
            cp   = m.get("change_percent")
            sign = f" ({'+' if cp > 0 else ''}{cp}% so với tuần liền kề)" if cp is not None else ""
            prompt += f"- {m['label']}: {format_number(m['value'])}{sign}\n"
        prompt += "\nSO SÁNH 4 TUẦN:\n"
        for w in s["weekly_comparison"]:
            gr   = w["growth_rate"]
            sign = f" ({'+' if gr > 0 else ''}{gr}%)" if gr is not None else ""
            prompt += f"- {w['week']}: {format_number(w['total_mentions'])} lượt{sign}\n"
        prompt += f"\nNHẬN ĐỊNH:\n{s['insight']}\n\n"

    # ── SLIDE 2 ───────────────────────────────────────────────────────────────
    if "slide_2" in report_data:
        s = report_data["slide_2"]
        prompt += _header("SLIDE 2 - XU HƯỚNG ĐỀ CẬP THEO THỜI GIAN (ĐƯỜNG TRENDLINE)")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: 1 CỘT\n"
            "  TRÊN: Biểu đồ đường xu hướng 7 ngày\n"
            "  DƯỚI: Diễn biến chính\n\n"
        )
        prompt += "DỮ LIỆU XU HƯỚNG (7 ngày):\n"
        for p in s["trendline"]:
            prompt += f"- {format_date(p['date'])}: {format_number(p['mentions'])} lượt\n"
        prompt += f"\n{s['insight']}\n\n"

    # ── SLIDE 3 ───────────────────────────────────────────────────────────────
    if "slide_3" in report_data:
        s = report_data["slide_3"]
        prompt += _header("SLIDE 3 - PHÂN BỔ LƯỢT ĐỀ CẬP THEO KÊNH")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: 2 CỘT\n"
            "  TRÁI (60%): Biểu đồ donut phân bổ kênh\n"
            "  PHẢI (40%): Biểu đồ thanh ngang top 10 nguồn\n"
            "  DƯỚI: Khung nhận định\n\n"
            "QUY TẮC DONUT KÊNH:\n"
            "  - Hiển thị % trên từng phần của vòng ngoài\n"
            "  - Ở giữa donut: tổng số lượt đề cập (số tuyệt đối)\n"
            "  - Legend nằm dọc bên phải chart (KHÔNG nằm dưới), mỗi dòng: ■ Tên kênh — X,XXX lượt (XX.X%)\n\n"
        )
        prompt += "PHÂN BỔ THEO KÊNH:\n"
        total_ch = sum(c["count"] for c in s["channel_distribution"])
        for c in s["channel_distribution"]:
            pct = (c["count"] / total_ch * 100) if total_ch > 0 else 0
            prompt += f"- {c['Channel']}: {format_number(c['count'])} lượt ({pct:.1f}%)\n"
        prompt += f"Tổng: {format_number(total_ch)} lượt\n"
        prompt += "\nTOP 10 NGUỒN:\n"
        for src in s["top_sources"]:
            prompt += f"- {src['SiteName']}: {format_number(src['count'])} lượt\n"
        prompt += f"\nNHẬN ĐỊNH:\n{s['insight']}\n\n"

    # ── SLIDE 4 ───────────────────────────────────────────────────────────────
    if "slide_4" in report_data:
        s = report_data["slide_4"]
        prompt += _header("SLIDE 4 - TOP NGUỒN CÓ LƯỢNG TƯƠNG TÁC CAO NHẤT")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += "BỐ CỤC: Bảng toàn trang (Header tô màu xanh #0045C4), KHÔNG có nhận định\n\n"
        if s.get("show_interactions") and s["table_rows"] and "total_engagement" in s["table_rows"][0]:
            # Check if we have Interactions column or individual metrics
            if "interactions" in s["table_rows"][0]:
                prompt += "CỘT: STT | Nguồn | Tổng tương tác | Interactions\n\nDỮ LIỆU BẢNG:\n"
                for r in s["table_rows"]:
                    prompt += (
                        f"- [{r['stt']}] {r['source_name']} | "
                        f"{format_number(r['total_engagement'])} | "
                        f"{format_number(r['interactions'])}\n"
                    )
            else:
                prompt += "CỘT: STT | Nguồn | Tổng tương tác | Reactions | Shares | Bình luận\n\nDỮ LIỆU BẢNG:\n"
                for r in s["table_rows"]:
                    prompt += (
                        f"- [{r['stt']}] {r['source_name']} | "
                        f"{format_number(r['total_engagement'])} | "
                        f"{format_number(r['reactions'])} | "
                        f"{format_number(r['shares'])} | "
                        f"{format_number(r['comments'])}\n"
                    )
        else:
            prompt += "CỘT: STT | Nguồn | Số lượng đề cập\n\nDỮ LIỆU BẢNG:\n"
            for r in s["table_rows"]:
                prompt += f"- [{r['stt']}] {r['source_name']} | {format_number(r['count'])}\n"
        prompt += "\n"

    # ── SLIDE 5 ───────────────────────────────────────────────────────────────
    if "slide_5" in report_data:
        s = report_data["slide_5"]
        prompt += _header("SLIDE 5 - TOP BÀI ĐĂNG CÓ TƯƠNG TÁC CAO NHẤT")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += "BỐ CỤC: Bảng toàn trang (Header tô màu xanh #0045C4), KHÔNG có nhận định\n\n"
        if s.get("show_interactions") and s["table_rows"]:
            # Check if we have Interactions column or individual metrics
            if "interactions" in s["table_rows"][0]:
                prompt += "CỘT: STT | Nội dung | Ngày đăng | Kênh | Nguồn | Interactions\n\nDỮ LIỆU BẢNG:\n"
                for r in s["table_rows"]:
                    preview = r["content"][:100] + "..." if len(r["content"]) > 100 else r["content"]
                    prompt += (
                        f"- [{r['stt']}] {preview} | "
                        f"{format_date(r['published_date'])} | "
                        f"{r['channel']} | {r['site_name']} | "
                        f"{format_number(r['interactions'])} | "
                        f"{r['url']}\n"
                    )
            elif "comments" in s["table_rows"][0]:
                prompt += "CỘT: STT | Nội dung | Ngày đăng | Kênh | Nguồn | Reactions | Shares | Bình luận\n\nDỮ LIỆU BẢNG:\n"
                for r in s["table_rows"]:
                    preview = r["content"][:100] + "..." if len(r["content"]) > 100 else r["content"]
                    prompt += (
                        f"- [{r['stt']}] {preview} | "
                        f"{format_date(r['published_date'])} | "
                        f"{r['channel']} | {r['site_name']} | "
                        f"{format_number(r.get('reactions', 0))} | "
                        f"{format_number(r.get('shares', 0))} | "
                        f"{format_number(r['comments'])} | "
                        f"{r['url']}\n"
                    )
            else:
                prompt += "CỘT: STT | Nội dung | Ngày đăng | Kênh | Nguồn | URL\n\nDỮ LIỆU BẢNG:\n"
                for r in s["table_rows"]:
                    preview = r["content"][:100] + "..." if len(r["content"]) > 100 else r["content"]
                    prompt += (
                        f"- [{r['stt']}] {preview} | "
                        f"{format_date(r['published_date'])} | "
                        f"{r['channel']} | {r['site_name']} | "
                        f"{r['url']}\n"
                    )
                    f"- [{r['stt']}] {preview} | "
                    f"{format_date(r['published_date'])} | "
                    f"{r['channel']} | {r['site_name']} | {r['url']}\n"
                )
        prompt += "\n"

    # ── SLIDE 6 ───────────────────────────────────────────────────────────────
    if "slide_6" in report_data:
        s = report_data["slide_6"]
        prompt += _header("SLIDE 6 - SẮC THÁI VÀ CỤM CHỦ ĐỀ ĐỀ CẬP NỔI BẬT")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"

        nsr_sign = "+" if s["nsr_growth"] > 0 else ""
        prev_nsr = s["previous_nsr"]
        curr_nsr = s["current_nsr"]

        # Xác định cấp độ NSR
        def _nsr_level(nsr):
            if nsr > 0:   return "Tích cực"
            if nsr >= 0:    return "Trung lập"
            if nsr < 0:  return "Tiêu cực"

        prompt += (
            "BỐ CỤC: 2 CỘT\n"
            "  CỘT TRÁI (50%):\n"
            "    HÀNG TRÊN: 2 thẻ cấp độ NSR cạnh nhau\n"
            "      Thẻ trái  — Tuần trước: cấp độ NSR\n"
            f"      Thẻ phải — Tuần này:   cấp độ NSR  |  So với kỳ trước: {nsr_sign}{s['nsr_growth']:.2f}%\n"
            "    HÀNG DƯỚI: 2 biểu đồ donut cạnh nhau (Tuần trước | Tuần này)\n"
            "      Mỗi donut: vòng ngoài = % từng sentiment, tâm = %NSR\n"
            "      Màu: Positive #2A9D5C | Neutral #ADB5BD | Negative #E63946\n"
            "      Legend nằm BÊN DƯỚI mỗi donut (KHÔNG nằm bên phải)\n\n"
            "  CỘT PHẢI (50%): Biểu đồ thanh ngang xếp chồng top 10 chủ đề\n\n"
            "  DƯỚI: Khung nhận định\n\n"
        )

        prompt += f"DỮ LIỆU NSR:\n"
        prompt += f"  Tuần trước: NSR = {prev_nsr}%  →  Cấp độ: {_nsr_level(prev_nsr)}\n"
        prompt += f"  Tuần này:   NSR = {curr_nsr}%  →  Cấp độ: {_nsr_level(curr_nsr)}\n"
        prompt += f"  Biến động:  {nsr_sign}{s['nsr_growth']:.2f}%\n\n"

        prompt += "SẮC THÁI DONUT — TUẦN TRƯỚC:\n"
        total_prev = sum(x["count"] for x in s["previous_sentiment"])
        for x in s["previous_sentiment"]:
            pct = (x["count"] / total_prev * 100) if total_prev > 0 else 0
            prompt += f"  - {x['sentiment']}: {format_number(x['count'])} lượt ({pct:.1f}%)\n"

        prompt += "\nSẮC THÁI DONUT — TUẦN NÀY:\n"
        total_curr = sum(x["count"] for x in s["current_sentiment"])
        for x in s["current_sentiment"]:
            pct = (x["count"] / total_curr * 100) if total_curr > 0 else 0
            prompt += f"  - {x['sentiment']}: {format_number(x['count'])} lượt ({pct:.1f}%)\n"

        prompt += "\nBIỂU ĐỒ THANH — Top 10 chủ đề theo sắc thái:\n"
        for t in s["top_topics_with_sentiment"]:
            prompt += (
                f"  - {t['topic']}: Tổng {format_number(t['total'])} "
                f"(Tiêu cực: {t['negative']}, Trung lập: {t['neutral']}, Tích cực: {t['positive']})\n"
            )
        prompt += f"\nNHẬN ĐỊNH:\n{s['insight']}\n\n"

    # ── SLIDE 7 ───────────────────────────────────────────────────────────────
    if "slide_7" in report_data:
        s = report_data["slide_7"]
        prompt += _header("SLIDE 7 - CÁC CHỦ ĐỀ ĐỀ CẬP TÍCH CỰC")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: 1 CỘT\n"
            "  TRÊN: Biểu đồ thanh ngang top 10 chủ đề tích cực (màu: #00C055)\n"
            "  DƯỚI: Khung nhận định\n\n"
        )
        prompt += "CHỦ ĐỀ TÍCH CỰC:\n"
        prompt += "Tên biểu đồ: Xếp hạng chủ đề chính dựa trên tổng thảo luận\n"
        for t in s["positive_topics"]:
            prompt += f"- {t['Labels1']}: {format_number(t['count'])} lượt\n"
        prompt += f"\nNHẬN ĐỊNH:\n{s['insight']}\n\n"

    # ── SLIDE 8 ───────────────────────────────────────────────────────────────
    if "slide_8" in report_data:
        s = report_data["slide_8"]
        prompt += _header("SLIDE 8 - TOP BÀI ĐĂNG TÍCH CỰC")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: Bảng toàn trang (Header tô màu xanh #0045C4), KHÔNG có nhận định\n"
            "CỘT: STT | Nội dung | Ngày đăng | Kênh | Nguồn | Tích cực | URL\n\n"
            "DỮ LIỆU BẢNG:\n"
        )
        for r in s["table_rows"]:
            preview = r["content"][:100] + "..." if len(r["content"]) > 100 else r["content"]
            prompt += (
                f"- [{r['stt']}] {preview} | "
                f"{format_date(r['published_date'])} | "
                f"{r['channel']} | {r['site_name']} | "
                f"{format_number(r['positive_comments'])} | "
                f"{r['url']}\n"
            )
        prompt += "\n"

    # ── SLIDE 9 ───────────────────────────────────────────────────────────────
    if "slide_9" in report_data:
        s = report_data["slide_9"]
        prompt += _header("SLIDE 9 - CÁC CHỦ ĐỀ ĐỀ CẬP TIÊU CỰC")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: 1 CỘT\n"
            "  TRÊN: Biểu đồ thanh ngang top 10 chủ đề tiêu cực (màu: #EC003F)\n"
            "  DƯỚI: Khung nhận định\n\n"
        )
        prompt += "CHỦ ĐỀ TIÊU CỰC:\n"
        prompt += "Tên biểu đồ: Xếp hạng chủ đề chính dựa trên tổng thảo luận\n"
        for t in s["negative_topics"]:
            prompt += f"- {t['Labels1']}: {format_number(t['count'])} lượt\n"
        prompt += f"\nNHẬN ĐỊNH:\n{s['insight']}\n\n"

    # ── SLIDE 10 ──────────────────────────────────────────────────────────────
    if "slide_10" in report_data:
        s = report_data["slide_10"]
        prompt += _header("SLIDE 10 - TOP BÀI ĐĂNG TIÊU CỰC")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: Bảng toàn trang, KHÔNG có nhận định\n"
            "CỘT: STT | Nội dung | Ngày đăng | Kênh | Nguồn | Tiêu cực | URL\n\n"
            "DỮ LIỆU BẢNG:\n"
        )
        for r in s["table_rows"]:
            preview = r["content"][:100] + "..." if len(r["content"]) > 100 else r["content"]
            prompt += (
                f"- [{r['stt']}] {preview} | "
                f"{format_date(r['published_date'])} | "
                f"{r['channel']} | {r['site_name']} | "
                f"{format_number(r['negative_comments'])} | "
                f"{r['url']}\n"
            )
        prompt += "\n"

    # ── SLIDE 11 ──────────────────────────────────────────────────────────────
    if "slide_11" in report_data:
        s = report_data["slide_11"]
        prompt += _header("SLIDE 11 - TỔNG QUAN VỀ THƯƠNG HIỆU VỚI CÁC ĐỐI THỦ")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: 2 HÀNG\n"
            "  HÀNG 1: Khung nhận định\n"
            "  HÀNG 2 TRÁI (50%): Hai biểu đồ donut cạnh nhau (Tuần trước | Tuần hiện tại)\n"
            "  HÀNG 2 PHẢI (50%): Biểu đồ cột đôi đứng\n\n"
            "QUY TẮC DONUT (cả 2 chart):\n"
            "  Tiêu đề: 'Tỷ trọng đề cập giữa các thương hiệu'\n"
            "  - Vòng ngoài: % của từng thương hiệu (hiển thị nhãn % trực tiếp trên vòng)\n"
            "  - Tâm donut: tổng số lượt đề cập (số tuyệt đối, font lớn)\n"
            "  - Legend nằm BÊN DƯỚI chart (KHÔNG nằm bên phải), mỗi dòng: ■ Tên thương hiệu\n\n"
            "QUY TẮC BIỂU ĐỒ CỘT PHẢI:\n"
            "  Tiêu đề: 'Tổng đề cập của các thương hiệu'\n"
            "  - Legend nằm góc trên bên phải của chart\n"
            "  - Sắp xếp giảm dần theo tuần hiện tại\n"
            "  - Hiển thị số lượng + mũi tên biến động trên mỗi cặp cột\n\n"
        )
        prompt += f"NHẬN ĐỊNH:\n{s['insight']}\n\n"

        prompt += "─── BIỂU ĐỒ DONUT ───────────────────────────────────────────\n"
        prompt += "QUY TẮC: Tổng ở giữa (tâm), tỷ lệ % trên vòng ngoài, legend BÊN DƯỚI chart\n\n"
        prev_data  = [i for i in s["donut_charts"]["week_before"]["data"]  if i["mentions"] > 0]
        curr_data  = [i for i in s["donut_charts"]["current_week"]["data"] if i["mentions"] > 0]
        total_prev = sum(i["mentions"] for i in prev_data)
        total_curr = sum(i["mentions"] for i in curr_data)

        prompt += f"DONUT TUẦN TRƯỚC — tổng: {format_number(total_prev)} lượt\n"
        for item in sorted(prev_data, key=lambda x: x["mentions"], reverse=True):
            pct = (item["mentions"] / total_prev * 100) if total_prev > 0 else 0
            prompt += f"  {item['brand']}: {format_number(item['mentions'])} lượt ({pct:.1f}%) | màu {item['color']}\n"

        prompt += f"\nDONUT TUẦN HIỆN TẠI — tổng: {format_number(total_curr)} lượt\n"
        for item in sorted(curr_data, key=lambda x: x["mentions"], reverse=True):
            pct = (item["mentions"] / total_curr * 100) if total_curr > 0 else 0
            prompt += f"  {item['brand']}: {format_number(item['mentions'])} lượt ({pct:.1f}%) | màu {item['color']}\n"

        prompt += "\nCHÚ GIẢI:\n"
        for item in s["legend"]:
            prompt += f"  ■ {item['brand']}: {item['color']}\n"

        prompt += "\n─── BIỂU ĐỒ CỘT ĐÔI ĐỨNG ──────────────────────────────────\n"
        prompt += f"Tiêu đề: {s['bar_chart']['title']}\n"
        prompt += "QUY TẮC: Cột TRÁI = Tuần trước, Cột PHẢI = Tuần này, sắp xếp giảm dần theo tuần hiện tại\n\n"
        prompt += "DỮ LIỆU:\n"
        for item in sorted(s["bar_chart"]["data"], key=lambda x: x["current_week"], reverse=True):
            sign  = "+" if item["percentage_change"] >= 0 else ""
            arrow = "↑" if item["percentage_change"] > 0 else ("↓" if item["percentage_change"] < 0 else "→")
            mau   = "xanh lá" if item["change_color"] == "green" else ("đỏ" if item["change_color"] == "red" else "xám")
            prompt += (
                f"  {item['brand']}: Tuần trước={format_number(item['week_before'])} | "
                f"Tuần này={format_number(item['current_week'])} | "
                f"{arrow} {sign}{item['percentage_change']}% ({mau})\n"
            )
        prompt += "\n"

    # ── SLIDE 12 ──────────────────────────────────────────────────────────────
    if "slide_12" in report_data:
        s = report_data["slide_12"]
        prompt += _header("SLIDE 12 - BẢNG XẾP HẠNG TỔNG LƯỢT THẢO LUẬN THEO THƯƠNG HIỆU")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: Bảng toàn trang (Header tô màu xanh #0045C4), KHÔNG có nhận định\n"
            "CỘT: STT | Thương hiệu | Tổng lượt thảo luận | Biến động\n\n"
            "DỮ LIỆU BẢNG:\n"
        )
        for r in s.get("table", []):
            sign  = "+" if r["pct_change"] >= 0 else ""
            arrow = "↑" if r["pct_change"] > 0 else ("↓" if r["pct_change"] < 0 else "→")
            mau   = "xanh lá" if r["change_color"] == "green" else "đỏ"
            prompt += (
                f"- [{r['stt']}] {r['brand']} | "
                f"{format_number(r['total'])} lượt | "
                f"{arrow} {sign}{r['pct_change']}% ({mau})\n"
            )
        prompt += "\n"

    # ── SLIDE 13 ──────────────────────────────────────────────────────────────
    if "slide_13" in report_data:
        s = report_data["slide_13"]
        prompt += _header("SLIDE 13 - XU HƯỚNG THẢO LUẬN THEO THỜI GIAN CỦA CÁC THƯƠNG HIỆU")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: 1 CỘT TOÀN TRANG\n"
            "  TRÊN: Biểu đồ đường theo ngày, mỗi thương hiệu một đường màu riêng\n"
            "  DƯỚI: Chú giải màu sắc\n\n"
        )
        prompt += "DỮ LIỆU ĐƯỜNG XU HƯỚNG:\n"
        for b in s["brands"]:
            tl    = s["trendlines"].get(b, [])
            total = sum(p["mentions"] for p in tl)
            dates_str = " | ".join(
                f"{format_date(p['date'])}: {p['mentions']}"
                for p in tl if p["mentions"] > 0
            )
            prompt += f"  [{b}] Tổng: {format_number(total)} lượt\n"
            if dates_str:
                prompt += f"    {dates_str}\n"
        prompt += "\nĐIỂM ĐỈNH (PEAK) THEO THƯƠNG HIỆU:\n"
        for b, ann in s["annotations"].items():
            prompt += (
                f"  [{b}] Ngày {format_date(ann['date'])} — {format_number(ann['mentions'])} lượt\n"
                f"    Trích dẫn: \"{ann['snippet']}\"\n"
                f"    Đường dẫn: {ann['url']}\n"
            )
        prompt += "\n"

    # ── SLIDE 14 ──────────────────────────────────────────────────────────────
    if "slide_14" in report_data:
        s = report_data["slide_14"]
        prompt += _header("SLIDE 14 - PHÂN BỐ TRÊN CÁC KÊNH TRUYỀN THÔNG")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: 2 HÀNG\n"
            "  HÀNG 1: 3 khung nhận định theo kênh (Facebook | Báo chí | Fanpage)\n"
            "  HÀNG 2: Biểu đồ cột xếp chồng phân bổ kênh theo từng thương hiệu/chủ đề\n\n"
            "QUY TẮC BIỂU ĐỒ CỘT XẾP CHỒNG:\n"
            "  - Mỗi cột = 1 thương hiệu/chủ đề, phân tầng theo nhóm kênh\n"
            "  - Đỉnh cột = tổng lượt đề cập, đáy cột = tên chủ đề\n"
            "  - Hiển thị nhãn % trên cột nếu >= 20%, ẩn nếu < 20%\n"
            "  - Legend nằm CỐ ĐỊNH BÊN PHẢI chart (KHÔNG nằm dưới)\n\n"
        )

        for sec in s.get("insight_sections", []):
            prompt += f"--- NHẬN ĐỊNH KÊNH: {sec['group']} ---\n"
            for topic in sec.get("topics", []):
                prompt += f"  Chủ đề nổi bật: {topic['label']} ({format_number(topic['count'])} lượt)\n"
            prompt += f"  Tóm tắt: {sec.get('summary', '')}\n\n"

        chart = s.get("stacked_bar_chart", {})
        prompt += f"BIỂU ĐỒ CỘT XẾP CHỒNG: {chart.get('title', '')}\n"
        prompt += "DỮ LIỆU:\n"
        for row in chart.get("data", []):
            prompt += f"  [{row['topic']}] Tổng: {format_number(row['total'])} lượt\n"
            for seg in row.get("segments", []):
                if seg["percent"] > 0:
                    hien_thi = " (hiển thị nhãn)" if seg["show_label"] else " (ẩn nhãn)"
                    prompt += f"    - {seg['group']}: {format_number(seg['count'])} lượt ({seg['percent']}%){hien_thi}\n"

        prompt += "\nCHÚ GIẢI KÊNH (cố định):\n"
        for leg in s.get("channel_legend", []):
            prompt += f"  ■ {leg['group']}: {leg['color']}\n"
        prompt += "\n"

    # ── SLIDE 15 ──────────────────────────────────────────────────────────────
    if "slide_15" in report_data:
        s = report_data["slide_15"]
        prompt += _header("SLIDE 15 - SẮC THÁI THEO CHỦ ĐỀ (TOPIC)")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: 3 HÀNG\n"
            "  HÀNG 1: Khung nhận định\n"
            "  HÀNG 2: Biểu đồ cột xếp chồng tỷ trọng sentiment theo Topic\n"
            "          Legend nằm BÊN DƯỚI chart (KHÔNG nằm bên phải)\n"
            "          Màu: Positive #2A9D5C | Neutral #ADB5BD | Negative #E63946\n"
            "  HÀNG 3: Bảng tổng hợp — CỘT: Thương hiệu | NSR | Biến động | Bài đăng tích cực | Bài đăng tiêu cực\n\n"
        )
        prompt += f"NHẬN ĐỊNH:\n{s['insight']}\n\n"

        chart = s.get("stacked_bar_chart", {})
        prompt += f"BIỂU ĐỒ CỘT XẾP CHỒNG: {chart.get('title', '')}\n"
        prompt += "DỮ LIỆU BIỂU ĐỒ:\n"
        for row in chart.get("data", []):
            prompt += f"  [{row['topic']}] Tổng: {format_number(row['total'])} lượt\n"
            for seg in row.get("segments", []):
                if seg["percent"] > 0:
                    prompt += f"    - {seg['sentiment']}: {seg['percent']}% ({format_number(seg['count'])} lượt)\n"

        prompt += "\nBẢNG TỔNG HỢP THEO TOPIC:\n"
        prompt += "CỘT: Thương hiệu | NSR | Biến động | Bài đăng tích cực (URL) | Bài đăng tiêu cực (URL)\n\n"
        tbl = s.get("summary_table", {})
        for topic in tbl.get("topics", []):
            nsr = tbl["NSR"].get(topic, 0)
            pct = tbl["pct_change"].get(topic, 0)
            sign  = "+" if pct >= 0 else ""
            arrow = "↑" if pct > 0 else ("↓" if pct < 0 else "→")
            mau   = "xanh lá" if pct >= 0 else "đỏ"
            prompt += f"  [{topic}] NSR: {nsr:+.1f}% | Biến động: {arrow} {sign}{pct}% ({mau})\n"

            pos_posts = tbl["positive_posts"].get(topic, [])
            if pos_posts:
                prompt += "    Bài đăng tích cực:\n"
                for p in pos_posts:
                    text = p["text"][:100] + "..." if len(p["text"]) > 100 else p["text"]
                    url  = p.get("url", "")
                    if url:
                        prompt += f"      • [{text}]({url})\n"
                    else:
                        prompt += f"      • {text}\n"

            neg_posts = tbl["negative_posts"].get(topic, [])
            if neg_posts:
                prompt += "    Bài đăng tiêu cực:\n"
                for p in neg_posts:
                    text = p["text"][:100] + "..." if len(p["text"]) > 100 else p["text"]
                    url  = p.get("url", "")
                    if url:
                        prompt += f"      • [{text}]({url})\n"
                    else:
                        prompt += f"      • {text}\n"
        prompt += "\n"

    # ── SLIDE 16 ──────────────────────────────────────────────────────────────
    if "slide_16" in report_data:
        s = report_data["slide_16"]
        prompt += _header("SLIDE 16 - TOP BÀI ĐĂNG CÓ LƯỢT BÌNH LUẬN CAO NHẤT")
        prompt += f"Tiêu đề: \"{s['title']}\"\nPhụ đề: \"{s['subtitle']}\"\n\n"
        prompt += (
            "BỐ CỤC: Bảng toàn trang (Header tô màu xanh #0045C4), KHÔNG có nhận định\n"
            "CỘT CỐ ĐỊNH: STT | Thương hiệu | Bài đăng | Kênh | Nguồn | Bình luận\n\n"
            "DỮ LIỆU BẢNG:\n"
        )
        for r in s.get("table", []):
            content = r["content"][:150] + "..." if len(r["content"]) > 150 else r["content"]
            prompt += (
                f"- [{r['stt']}] {r['topic']} | {content} | "
                f"{r['channel']} | {r['source_name']} | "
                f"{format_number(r['comment_count'])} lượt | {r['source_url']}\n"
            )
        prompt += "\n"

    # ── THIẾT KẾ TỔNG THỂ ────────────────────────────────────────────────────
    prompt += "===============================================================\n"
    prompt += "THIẾT KẾ TỔNG THỂ\n"
    prompt += "===============================================================\n\n"
    prompt += (
        "BẢNG MÀU: Màu chủ đạo #0045C4 | Tích cực #00C055 | Tiêu cực #EC003F | Trung lập #6b7280 | Nền #FFFFFF\n"
        "KIỂU CHỮ: Tiêu đề 32px Đậm | Mục 24px Đậm | Nội dung 14px Thường | Font: Inter/Roboto\n"
        "ĐỊNH DẠNG SỐ: dấu phẩy hàng nghìn (ví dụ: 1,234)\n\n"
    )
    if has_logo:
        prompt += "LOGO: Hiển thị Kompa.ai ở góc trái phía trên tiêu đề của mỗi slide\n\n"
    else:
        prompt += "LOGO: Không hiển thị bất kỳ logo nào trên các slide\n\n"
    prompt += "===============================================================\n"
    prompt += "HƯỚNG DẪN BẮT BUỘC:\n"
    prompt += (
        "1. Tạo đúng các slide có dữ liệu ở trên, tuân thủ bố cục từng slide\n"
        "2. Đảm bảo biểu đồ được định dạng và gán nhãn đúng. Tiêu đề phụ nằm dưới tiêu đề chính, thời gian lấy dữ liệu nằm bên góc phải\n"
        "3. Sử dụng bảng màu nhất quán, giữ nguyên đường dẫn (hyperlink)\n"
        "4. Slide 1: các thẻ KPI cần thêm cụm 'So với tuần liền kề' bên dưới % thay đổi\n"
        "5. Slide 2 đường trendline: hiển thị legend\n"
        "6. Slide 2 bảng diễn biến chính: hiển thị 2 cột gồm 3 bài và 4 bài\n"
        "7. Slide 3 donut: % hiển thị trên vòng ngoài, tổng lượt ở giữa, legend dọc bên PHẢI chart (không nằm dưới)\n"
        "8. Slide 6 cột trái: 2 thẻ cấp độ NSR phía trên (thẻ phải có biến động so kỳ trước), 2 donut phía dưới — tâm donut = %NSR, vòng ngoài = % sentiment (Positive #2A9D5C / Neutral #ADB5BD / Negative #E63946), legend nằm BÊN DƯỚI mỗi donut\n"
        "9. Slide 11 donut: tâm = tổng lượt, vòng ngoài = % từng thương hiệu, legend BÊN DƯỚI chart; biểu đồ cột phải có legend góc trên bên phải\n"
        "10. Slide 11 cột đôi: sắp xếp giảm dần, số lượng + mũi tên biến động trên mỗi cặp cột\n"
        "11. Slide 12: bảng xếp hạng sắp xếp giảm dần theo tổng lượt, cột Biến động hiển thị mũi tên + màu xanh/đỏ\n"
        "12. Slide 13: đánh dấu điểm đỉnh (peak) mỗi thương hiệu, trích dẫn là hyperlink dẫn đến URL\n"
        "13. Slide 14: cột xếp chồng — đỉnh cột ghi tổng lượt, ẩn nhãn % nếu < 20%, legend CỐ ĐỊNH BÊN PHẢI chart\n"
        "14. Slide 15: biểu đồ cột xếp chồng sentiment có legend BÊN DƯỚI; bảng tổng hợp gồm 4 cột: Thương hiệu\\NSR | Biến động | Bài đăng tích cực | Bài đăng tiêu cực; nội dung bài đăng là hyperlink dẫn đến URL\n"
        "15. Slide 16: bảng top bài đăng có lượt bình luận cao nhất, hiển thị nội dung và link nguồn\n"
    )
    prompt += "===============================================================\n"

    return prompt
