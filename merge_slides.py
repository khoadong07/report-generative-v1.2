#!/usr/bin/env python3
"""
Script để merge JSON data vào HTML templates cho weekly report slides.
Sử dụng: python merge_slides.py
"""
import json
import re
from pathlib import Path
from typing import Dict, Any, List


class SlideHTMLMerger:
    """Merge JSON data into HTML slide templates."""
    
    def __init__(self, html_dir: str = "html", output_dir: str = "output"):
        self.html_dir = Path(html_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def merge_slide01(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 1 (Overview)."""
        metrics = data["current_week_metrics"]
        show_interactions = data.get("show_interactions", True)
        
        # Detect if we need the 6-card template
        # Use 6-card template when show_interactions=True and we have 6 metrics
        use_6_card_template = show_interactions and len(metrics) >= 6
        
        # Choose template
        if use_6_card_template:
            html_path = self.html_dir / "slide1_interactions.html"
        else:
            html_path = self.html_dir / "slide1.html"
        
        html = html_path.read_text(encoding="utf-8")
        
        # Replace placeholders
        html = html.replace("{{DATE_RANGE}}", date_range)
        html = html.replace("{{TITLE}}", data["title"])
        html = html.replace("{{SUBTITLE}}", data["subtitle"])
        
        # Replace metrics cards
        if use_6_card_template:
            # 6-card template: replace all 6 metrics
            for i in range(min(6, len(metrics))):
                html = self._replace_metric_card(html, i, metrics[i], metrics[i]["label"])
        else:
            # 3-card template: show top 3 metrics
            if show_interactions:
                # Interactions mode: show first 3
                for i in range(min(3, len(metrics))):
                    html = self._replace_metric_card(html, i, metrics[i], metrics[i]["label"])
            else:
                # Basic mode: posts, comments, discussions (3 metrics)
                if len(metrics) >= 3:
                    # Card 1: Total discussions (moved to top)
                    html = self._replace_metric_card(html, 0, metrics[2], "Tổng thảo luận")
                    # Card 2: Total posts (middle)
                    html = self._replace_metric_card(html, 1, metrics[0], "Tổng bài đăng")
                    # Card 3: Total comments (bottom)
                    html = self._replace_metric_card(html, 2, metrics[1], "Tổng bình luận")
        
        # Replace chart data (weekly comparison)
        html = self._replace_chart_data(html, data["weekly_comparison"])
        
        # Replace insight/footer with hyperlinked URLs
        insight = self._format_insight_with_hyperlinks(data["insight"])
        html = html.replace("{{INSIGHT}}", insight)
        
        return html
    
    def merge_slide02(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 2 (Trendline)."""
        html_path = self.html_dir / "slide2.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace placeholders
        html = html.replace("{{DATE_RANGE}}", date_range)
        html = html.replace("{{TITLE}}", data["title"])
        html = html.replace("{{SUBTITLE}}", data["subtitle"])
        
        # Replace trendline chart data
        html = self._replace_trendline_data(html, data["trendline"])
        
        # Replace events (DIỄN BIẾN CHÍNH)
        html = self._replace_events(html, data["insight"])
        
        return html
    
    def merge_slide03(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 3 (Channel Distribution)."""
        html_path = self.html_dir / "slide3.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace basic placeholders
        html = html.replace("{{DATE_RANGE}}", date_range)
        html = html.replace("{{TITLE}}", data["title"])
        html = html.replace("{{SUBTITLE}}", data["subtitle"])
        
        # Replace channel distribution (donut chart)
        html = self._replace_channel_distribution(html, data["channel_distribution"])
        
        # Replace top sources (bar chart)
        html = self._replace_top_sources(html, data["top_sources"])
        
        # Replace insight with hyperlinked URLs
        insight = self._format_insight_with_hyperlinks(data["insight"])
        html = html.replace("{{INSIGHT}}", insight)
        
        return html
    
    def merge_slide04(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 4 (Top Sources Table)."""
        show_interactions = data.get("show_interactions", False)
        has_individual_metrics = data["table_rows"] and "reactions" in data["table_rows"][0]
        
        # Choose template based on interactions mode
        if show_interactions and has_individual_metrics:
            html_path = self.html_dir / "slide4_interactions.html"
        else:
            html_path = self.html_dir / "slide4.html"
        
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range and title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Generate table rows dynamically
        table_rows_html = self._generate_table_rows_slide04(data["table_rows"], show_interactions)
        
        # Replace all hardcoded table rows - match from first row to page footer
        pattern = r'<!-- Table Row 1 -->.*?(?=<!-- Page Number -->|<!-- Bottom Strip -->|</div>\s*</body>)'
        html = re.sub(pattern, table_rows_html, html, flags=re.DOTALL)
        
        return html
    
    def merge_slide05(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 5 (Top Posts Table)."""
        show_interactions = data.get("show_interactions", False)
        has_individual_metrics = data["table_rows"] and "reactions" in data["table_rows"][0]
        
        # Choose template based on interactions mode
        if show_interactions and has_individual_metrics:
            html_path = self.html_dir / "slide5_interactions.html"
        else:
            html_path = self.html_dir / "slide5.html"
        
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range, title, subtitle
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Generate table rows dynamically
        table_rows_html = self._generate_table_rows_slide05(data["table_rows"], show_interactions)
        
        # Replace all hardcoded table rows - match from first row to last row separator
        if show_interactions and has_individual_metrics:
            # For interactions template
            pattern = r'<!-- Table Row 1 -->.*?(?=<!-- Page Number -->|<!-- Bottom Strip -->|</div>\s*</body>)'
        else:
            # For regular template - match all rows including separators
            pattern = r'<!-- Table Row 1 -->.*?(?=<!-- Page Number -->|<!-- Bottom Strip -->|</div>\s*</body>)'
        html = re.sub(pattern, table_rows_html, html, flags=re.DOTALL)
        
        return html
    
    def merge_slide06(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 6 (Sentiment Analysis)."""
        html_path = self.html_dir / "slide6.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range, title, subtitle
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 32px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 17\.33px; color: #4b5563;">)[^<]+(</p>)',
            rf'\g<1>{data["subtitle"]}\g<2>',
            html,
            count=1
        )
        
        # Replace NSR values and sentiment data in JavaScript
        html = self._replace_sentiment_data(html, data)
        
        # Replace insight with hyperlinked URLs
        insight = self._format_insight_with_hyperlinks(data["insight"])
        # Find and replace insight in footer
        pattern = r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 12px; color: #374151; line-height: 1\.5; text-align: justify;">)\s*.*?\s*(</p>)'
        html = re.sub(pattern, rf'\g<1>\n            {insight}\n        \g<2>', html, flags=re.DOTALL)
        
        return html
    
    def merge_slide07(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 7 (Positive Topics)."""
        html = (self.html_dir / "slide7.html").read_text(encoding="utf-8")
        
        # Replace date range
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        
        # Replace title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Replace subtitle
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 17\.33px; color: #4b5563;">)[^<]+(</p>)',
            rf'\g<1>{data["subtitle"]}\g<2>',
            html,
            count=1
        )
        
        # Replace chart data
        topics = data["positive_topics"]
        labels = [t["Labels1"] for t in topics]
        counts = [t["count"] for t in topics]
        
        labels_json = json.dumps(labels, ensure_ascii=False)
        counts_json = json.dumps(counts)
        
        # Replace labels
        old_labels = "labels: ['Không xác định', 'Tài chính / Chứng khoán', 'Khuyến mãi & Ưu đãi', 'Khác', 'Lãi suất', 'Ứng dụng & Ngân hàng số'],"
        new_labels = f"labels: {labels_json},"
        html = html.replace(old_labels, new_labels)
        
        # Replace data
        old_data = "data: [103, 4, 1, 1, 1, 1],"
        new_data = f"data: {counts_json},"
        html = html.replace(old_data, new_data)
        
        # Replace insight with hyperlinked URLs
        insight = self._format_insight_with_hyperlinks(data["insight"])
        pattern = r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 12px; color: #374151; line-height: 1\.5; text-align: justify;">)\s*.*?\s*(</p>)'
        html = re.sub(pattern, rf'\g<1>\n            {insight}\n        \g<2>', html, flags=re.DOTALL)
        
        return html
    
    def merge_slide08(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 8 (Positive Posts Table)."""
        html_path = self.html_dir / "slide8.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        
        # Replace title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Replace subtitle
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 17\.33px; color: #4b5563;">)[^<]+(</p>)',
            rf'\g<1>{data["subtitle"]}\g<2>',
            html,
            count=1
        )
        
        # Generate table rows dynamically
        table_rows_html = self._generate_table_rows_slide08(data["table_rows"])
        
        # Replace all hardcoded table rows
        pattern = r'(<!-- Table Row 1 -->.*?<!-- Table Row 10 -->.*?target="_blank">Xem chi tiết</a></p>\s*</div>)'
        html = re.sub(pattern, table_rows_html, html, flags=re.DOTALL)
        
        return html
    
    def merge_slide09(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 9 (Negative Topics)."""
        html = (self.html_dir / "slide9.html").read_text(encoding="utf-8")
        
        # Replace date range
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        
        # Replace title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Replace subtitle
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 17\.33px; color: #4b5563;">)[^<]+(</p>)',
            rf'\g<1>{data["subtitle"]}\g<2>',
            html,
            count=1
        )
        
        # Replace chart data
        topics = data["negative_topics"]
        labels = [t["Labels1"] for t in topics]
        counts = [t["count"] for t in topics]
        
        labels_json = json.dumps(labels, ensure_ascii=False)
        counts_json = json.dumps(counts)
        
        # Replace labels
        old_labels = "labels: ['Không xác định', 'Ứng dụng & Ngân hàng số', 'Hoạt động kinh doanh', 'Phí dịch vụ', 'SMART BANKING', ['SẢN PHẨM / DỊCH VỤ', 'DOANH NGHIỆP'], 'Sản phẩm & Dịch vụ Tài chính', ['Đối thủ/So sánh', 'giữa các doanh nghiệp']],"
        new_labels = f"labels: {labels_json},"
        html = html.replace(old_labels, new_labels)
        
        # Replace data
        old_data = "data: [20, 6, 4, 2, 2, 1, 1, 1],"
        new_data = f"data: {counts_json},"
        html = html.replace(old_data, new_data)
        
        # Replace insight with hyperlinked URLs
        insight = self._format_insight_with_hyperlinks(data["insight"])
        pattern = r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 11px; color: #374151; line-height: 1\.5; text-align: justify;">)\s*.*?\s*(</p>)'
        html = re.sub(pattern, rf'\g<1>\n            {insight}\n        \g<2>', html, flags=re.DOTALL)
        
        return html
    
    def merge_slide10(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 10 (Negative Posts Table)."""
        html_path = self.html_dir / "slide10.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        
        # Replace title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Replace subtitle
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 17\.33px; color: #4b5563;">)[^<]+(</p>)',
            rf'\g<1>{data["subtitle"]}\g<2>',
            html,
            count=1
        )
        
        # Generate table rows dynamically
        table_rows_html = self._generate_table_rows_slide10(data["table_rows"])
        
        # Replace all hardcoded table rows
        pattern = r'(<!-- Table Row 1 -->.*?<!-- Table Row 10 -->.*?target="_blank">Xem chi tiết</a></p>\s*</div>)'
        html = re.sub(pattern, table_rows_html, html, flags=re.DOTALL)
        
        return html
    
    def merge_slide11(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 11 (Brand Comparison)."""
        html_path = self.html_dir / "slide11.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        
        # Replace title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 32px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Replace insight with hyperlinked URLs
        insight = self._format_insight_with_hyperlinks(data["insight"])
        pattern = r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 12px; color: #374151; line-height: 1\.5; text-align: justify;">)\s*.*?\s*(</p>)'
        html = re.sub(pattern, rf'\g<1>\n            {insight}\n        \g<2>', html, flags=re.DOTALL)
        
        # Prepare donut chart data
        donut_w2 = data["donut_charts"]["week_before"]["data"]  # Tuần trước
        donut_w1 = data["donut_charts"]["current_week"]["data"]  # Tuần này
        
        # Calculate totals
        total_w2 = sum(d["mentions"] for d in donut_w2)
        total_w1 = sum(d["mentions"] for d in donut_w1)
        
        # Calculate percentages for donut charts
        donut_w2_pct = []
        donut_w1_pct = []
        for d in donut_w2:
            pct = (d["mentions"] / total_w2 * 100) if total_w2 > 0 else 0
            donut_w2_pct.append(round(pct, 1))
        for d in donut_w1:
            pct = (d["mentions"] / total_w1 * 100) if total_w1 > 0 else 0
            donut_w1_pct.append(round(pct, 1))
        
        # Extract labels and colors
        labels = [d["brand"] for d in donut_w1]
        colors = [d["color"] for d in donut_w1]
        
        labels_json = json.dumps(labels, ensure_ascii=False)
        colors_json = json.dumps(colors)
        donut_w2_json = json.dumps(donut_w2_pct)
        donut_w1_json = json.dumps(donut_w1_pct)
        
        # Replace donut chart data - Last Week
        html = html.replace(
            "labels: ['Vietcombank', 'Techcombank', 'BIDV'],",
            f"labels: {labels_json},"
        )
        html = html.replace(
            "data: [48.2, 26.5, 25.3],",
            f"data: {donut_w2_json},"
        )
        html = html.replace(
            "backgroundColor: ['#1D6FA4', '#F4A261', '#E63946'],",
            f"backgroundColor: {colors_json},"
        )
        
        # Replace donut chart data - This Week (second occurrence)
        # Find the second occurrence of labels
        parts = html.split("labels: " + labels_json + ",", 1)
        if len(parts) == 2:
            # Replace in the second part
            parts[1] = parts[1].replace(
                "data: [51.0, 32.4, 16.6],",
                f"data: {donut_w1_json},",
                1
            )
            parts[1] = parts[1].replace(
                "backgroundColor: " + colors_json + ",",
                f"backgroundColor: {colors_json},",
                1
            )
            html = parts[0] + "labels: " + labels_json + "," + parts[1]
        
        # Replace total mentions
        html = html.replace(
            '<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 18px; font-weight: 700; color: #111827;">17,130</p>',
            f'<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 18px; font-weight: 700; color: #111827;">{total_w2:,}</p>'
        )
        html = html.replace(
            '<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 18px; font-weight: 700; color: #111827;">33,686</p>',
            f'<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 18px; font-weight: 700; color: #111827;">{total_w1:,}</p>'
        )
        
        # Build legend HTML
        legend_html = '<div style="display: flex; justify-content: center; gap: 20px;">\n'
        for item in data["legend"]:
            legend_html += f'<div style="display: flex; align-items: center; gap: 6px;"><div style="width: 12px; height: 12px; background-color: {item["color"]}; border-radius: 2px;"></div><span style="font-family: \'Inter\', sans-serif; font-size: 12px; color: #4b5563;">{item["brand"]}</span></div>\n'
        legend_html += '</div>'
        
        # Replace legend
        old_legend = '<div style="display: flex; justify-content: center; gap: 20px;">\n<div style="display: flex; align-items: center; gap: 6px;"><div style="width: 12px; height: 12px; background-color: #1D6FA4; border-radius: 2px;"></div><span style="font-family: \'Inter\', sans-serif; font-size: 12px; color: #4b5563;">Vietcombank</span></div>\n<div style="display: flex; align-items: center; gap: 6px;"><div style="width: 12px; height: 12px; background-color: #F4A261; border-radius: 2px;"></div><span style="font-family: \'Inter\', sans-serif; font-size: 12px; color: #4b5563;">Techcombank</span></div>\n<div style="display: flex; align-items: center; gap: 6px;"><div style="width: 12px; height: 12px; background-color: #E63946; border-radius: 2px;"></div><span style="font-family: \'Inter\', sans-serif; font-size: 12px; color: #4b5563;">BIDV</span></div>\n</div>'
        html = html.replace(old_legend, legend_html)
        
        # Replace bar chart data
        bar_data = data["bar_chart"]["data"]
        bar_labels = [d["brand"] for d in bar_data]
        bar_week_before = [d["week_before"] for d in bar_data]
        bar_current_week = [d["current_week"] for d in bar_data]
        
        bar_labels_json = json.dumps(bar_labels, ensure_ascii=False)
        bar_week_before_json = json.dumps(bar_week_before)
        bar_current_week_json = json.dumps(bar_current_week)
        
        # Replace bar chart labels and data
        html = html.replace(
            "labels: ['Vietcombank', 'Techcombank', 'BIDV'],",
            f"labels: {bar_labels_json},"
        )
        html = html.replace(
            "data: [8254, 4544, 4332],",
            f"data: {bar_week_before_json},"
        )
        html = html.replace(
            "data: [17175, 10920, 5591],",
            f"data: {bar_current_week_json},"
        )
        
        # Replace growth calculation arrays in datalabels formatter
        old_arrays = "const lastWeek = [8254, 4544, 4332];\n                                const thisWeek = [17175, 10920, 5591];"
        new_arrays = f"const lastWeek = {bar_week_before_json};\n                                const thisWeek = {bar_current_week_json};"
        html = html.replace(old_arrays, new_arrays)
        
        # Also replace in color function
        html = html.replace(
            "const lastWeek = [8254, 4544, 4332];\n                                const thisWeek = [17175, 10920, 5591];",
            f"const lastWeek = {bar_week_before_json};\n                                const thisWeek = {bar_current_week_json};"
        )
        
        return html
    
    def _format_insight_with_hyperlinks(self, insight: str) -> str:
        """
        Convert URLs in insight to hyperlinks.
        Format: [Nguồn: https://example.com] -> <a href="https://example.com">Nguồn</a>
        """
        import re
        
        # Pattern to match [Nguồn: URL] or [URL]
        pattern = r'\[(?:Nguồn:\s*)?(https?://[^\]]+)\]'
        
        def replace_url(match):
            url = match.group(1).strip()
            return f'<a href="{url}" style="color: #0045c4; text-decoration: none;">Nguồn</a>'
        
        return re.sub(pattern, replace_url, insight)
    
    def _replace_metric_card(self, html: str, card_index: int, 
                            metric: Dict[str, Any], label: str) -> str:
        """Replace metric value and percentage in a card using placeholders."""
        value = metric["value"]
        change = metric["change_percent"]
        
        # Format value with thousand separator
        value_str = f"{value:,}"
        
        # Format change percentage
        if change is None or change == 0:
            change_str = "0%"
            color = "#6b7280"
        elif change > 0:
            change_str = f"↑ {abs(change):.2f}%"
            color = "#00c055"
        else:
            change_str = f"↓ {abs(change):.2f}%"
            color = "#ec003f"
        
        # Replace placeholders based on card index
        placeholder_num = card_index + 1
        html = html.replace(f"{{{{METRIC_{placeholder_num}_VALUE}}}}", value_str)
        html = html.replace(f"{{{{METRIC_{placeholder_num}_CHANGE}}}}", change_str)
        
        # Update color in the percentage tag
        # Find and replace the color for this specific metric
        old_color_pattern = f'<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; font-weight: 700; color: #[0-9a-f]+;">{re.escape(change_str)}</p>'
        new_color_tag = f'<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; font-weight: 700; color: {color};">{change_str}</p>'
        html = re.sub(old_color_pattern, new_color_tag, html, count=1)
        
        return html
    
    def _replace_chart_data(self, html: str, weekly_comparison: List[Dict]) -> str:
        """Replace bar chart data in slide 1."""
        labels = [w["week"] for w in weekly_comparison]
        values = [w["total_mentions"] for w in weekly_comparison]
        
        # Replace week labels
        for i, label in enumerate(labels, 1):
            html = html.replace(f"{{{{WEEK_LABEL_{i}}}}}", label)
        
        # Replace data values in JavaScript
        values_js = json.dumps(values)
        html = re.sub(
            r"data:\s*\[[^\]]+\]",
            "data: " + values_js,
            html,
            count=1
        )
        
        return html
    
    def _replace_trendline_data(self, html: str, trendline: List[Dict]) -> str:
        """Replace line chart data in slide 2."""
        # Extract dates and format as DD/MM
        for i, item in enumerate(trendline, 1):
            date_str = item["date"]  # YYYY-MM-DD
            parts = date_str.split("-")
            day_label = f"{parts[2]}/{parts[1]}"
            html = html.replace(f"{{{{DAY_{i}}}}}", day_label)
        
        values = [item["mentions"] for item in trendline]
        
        # Replace data values
        values_js = json.dumps(values)
        html = re.sub(
            r"const data = \[[^\]]+\];",
            "const data = " + values_js + ";",
            html,
            count=1
        )
        
        return html
    
    def _replace_insight(self, html: str, insight: str) -> str:
        """Replace insight text in footer section."""
        # Find and replace the insight paragraph
        pattern = r'(<p style="margin: 0; font-family[^>]+>)\s*Số lượng thảo luận[^<]+(?:<a[^>]+>[^<]+</a>[^<]*)*\s*(</p>)'
        replacement = r'\1' + insight + r'\2'
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)
        return html
    
    def _replace_events(self, html: str, insight: str) -> str:
        """Replace events section (DIỄN BIẾN CHÍNH) in slide 2."""
        # Parse insight to extract date-event pairs
        lines = insight.split("\n")
        events = []
        for line in lines:
            line = line.strip()
            if not line or line == "DIỄN BIẾN CHÍNH:":
                continue
            # Check if line starts with a date (YYYY-MM-DD or date object string)
            if " - " in line:
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    date_str = parts[0].strip()
                    text = parts[1].strip()
                    # Format date if it's in YYYY-MM-DD format
                    try:
                        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
                            # Convert YYYY-MM-DD to DD/MM/YYYY
                            year, month, day = date_str.split('-')
                            date_str = f"{day}/{month}/{year}"
                    except:
                        pass
                    events.append((date_str, text))
        
        if not events:
            return html
        
        # Split into left (first 3) and right (rest) columns
        left_events = events[:3]
        right_events = events[3:7]  # Max 4 items in right column
        
        # Build HTML for left column
        left_html = ""
        for i, (date, text) in enumerate(left_events):
            margin = "12px" if i < len(left_events) - 1 else "0"
            left_html += f'''<div style="margin-bottom: {margin}; font-family: 'Product Sans', sans-serif; font-size: 12px; color: #374151;">
<span style="font-weight: 700; color: #0045c4; display: inline-block; width: 80px;">{date}</span>
<span style="color: #4b5563;">{text}</span>
</div>
'''
        
        # Build HTML for right column
        right_html = ""
        for i, (date, text) in enumerate(right_events):
            margin = "8px" if i < len(right_events) - 1 else "0"
            right_html += f'''<div style="margin-bottom: {margin}; font-family: 'Product Sans', sans-serif; font-size: 12px; color: #374151;">
<span style="font-weight: 700; color: #0045c4; display: inline-block; width: 80px;">{date}</span>
<span style="color: #4b5563;">{text}</span>
</div>
'''
        
        # Replace placeholders
        html = html.replace("{{LEFT_EVENTS}}", left_html)
        html = html.replace("{{RIGHT_EVENTS}}", right_html)
        
        return html
    
    def _replace_channel_distribution(self, html: str, channels: List[Dict]) -> str:
        """Replace donut chart data for channel distribution."""
        # Define color mapping for common channels
        channel_colors = {
            "News": "#F4A261",
            "Facebook": "#42B72A",
            "Tiktok": "#010101",
            "Social": "#ADB5BD",
            "Youtube": "#FF0000",
            "Threads": "#000000",
            "Instagram": "#E4405F",
            "Twitter": "#1DA1F2",
            "LinkedIn": "#0077B5"
        }
        
        labels = []
        data = []
        colors = []
        total = sum(ch["count"] for ch in channels)
        
        for ch in channels:
            channel_name = ch["Channel"]
            count = ch["count"]
            labels.append(channel_name)
            data.append(count)
            # Use predefined color or generate a default one
            colors.append(channel_colors.get(channel_name, "#6B7280"))
        
        # Replace chart data
        html = html.replace("{{CHANNEL_LABELS}}", json.dumps(labels))
        html = html.replace("{{CHANNEL_DATA}}", json.dumps(data))
        html = html.replace("{{CHANNEL_COLORS}}", json.dumps(colors))
        
        # Replace total count
        html = html.replace("{{TOTAL_COUNT}}", f"{total:,}")
        
        # Build custom legend HTML - chỉ hiển thị tên kênh
        legend_html = ""
        for i, ch in enumerate(channels):
            channel_name = ch["Channel"]
            color = colors[i]
            
            legend_html += f'''<div style="margin-bottom: 12px; display: flex; align-items: center;">
<span style="width: 12px; height: 12px; background-color: {color}; border-radius: 2px; margin-right: 8px;"></span>
<span style="font-family: 'Product Sans', sans-serif; font-size: 13px; color: #374151;">{channel_name}</span>
</div>
'''
        
        html = html.replace("{{CHANNEL_LEGEND}}", legend_html)
        
        return html
    
    def _replace_top_sources(self, html: str, sources: List[Dict]) -> str:
        """Replace bar chart data for top sources."""
        # Take top 10 sources
        top_sources = sources[:10]
        
        labels = [s["SiteName"] for s in top_sources]
        data = [s["count"] for s in top_sources]
        
        # Replace chart data
        html = html.replace("{{SOURCE_LABELS}}", json.dumps(labels))
        html = html.replace("{{SOURCE_DATA}}", json.dumps(data))
        
        return html
    
    def _generate_table_rows_slide04(self, table_rows: List[Dict], show_interactions: bool) -> str:
        """Generate HTML for table rows in slide 4 (Top Sources)."""
        html = ""
        
        # Check if we have individual metrics
        has_individual_metrics = table_rows and "reactions" in table_rows[0]
        
        for i, row in enumerate(table_rows, 1):
            top_pos = 215 + (i - 1) * 40
            sep_pos = top_pos + 30
            
            # Determine what value to display
            if show_interactions and "total_engagement" in row:
                value = row["total_engagement"]
            else:
                value = row.get("count", 0)
            
            if show_interactions and has_individual_metrics:
                # Use interactions template layout (6 columns)
                reactions = row.get("reactions", 0)
                shares = row.get("shares", 0)
                comments = row.get("comments", 0)
                
                html += f'''<!-- Table Row {i} -->
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 80px; top: {top_pos}px; width: 60px; height: 20px; z-index: 205; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #6b7280;">{row["stt"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 180px; top: {top_pos}px; width: 500px; height: 20px; z-index: 206;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #111827;">{row["source_name"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 720px; top: {top_pos}px; width: 120px; height: 20px; z-index: 207; text-align: right;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; font-weight: 700; color: #0045c4;">{value:,}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 860px; top: {top_pos}px; width: 100px; height: 20px; z-index: 208; text-align: right;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #6b7280;">{reactions:,}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 980px; top: {top_pos}px; width: 100px; height: 20px; z-index: 209; text-align: right;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #6b7280;">{shares:,}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 1100px; top: {top_pos}px; width: 100px; height: 20px; z-index: 210; text-align: right;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #6b7280;">{comments:,}</p>
</div>
'''
            else:
                # Use regular template layout (3 columns)
                html += f'''<!-- Table Row {i} -->
<div style="position: absolute; left: 80px; top: {top_pos}px; width: 60px; height: 20px; z-index: 205; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #6b7280;">{row["stt"]}</p>
</div>
<div style="position: absolute; left: 180px; top: {top_pos}px; width: 700px; height: 20px; z-index: 206;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #111827;">{row["source_name"]}</p>
</div>
<div style="position: absolute; left: 920px; top: {top_pos}px; width: 260px; height: 20px; z-index: 207; text-align: right;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; font-weight: 700; color: #0045c4;">{value:,}</p>
</div>
'''
            
            # Separator (except for last row)
            if i < len(table_rows):
                html += f'''<!-- Row Separator {i} -->
<div data-object="true" data-object-type="shape" style="position: absolute; left: 80px; top: {sep_pos}px; width: 1120px; height: 1px; background-color: #e5e7eb; z-index: 201;"></div>
'''
        
        return html
    
    def _generate_table_rows_slide05(self, table_rows: List[Dict], show_interactions: bool = False) -> str:
        """Generate HTML for table rows in slide 5 (Top Posts)."""
        html = ""
        
        # Check if we have individual metrics
        has_individual_metrics = table_rows and "reactions" in table_rows[0]
        
        for i, row in enumerate(table_rows, 1):
            top_pos = 215 + (i - 1) * 45
            sep_pos = top_pos + 35
            
            # Truncate content to fit column width
            if show_interactions and has_individual_metrics:
                content = row["content"][:50] + "..." if len(row["content"]) > 50 else row["content"]
            else:
                content = row["content"][:70] + "..." if len(row["content"]) > 70 else row["content"]
            
            # Format date (DD/MM/YYYY)
            pub_date = row["published_date"][:10] if len(row["published_date"]) >= 10 else row["published_date"]
            
            # Truncate site name
            site_name = row["site_name"][:25] + "..." if len(row["site_name"]) > 25 else row["site_name"]
            
            if show_interactions and has_individual_metrics:
                # Use interactions template layout (9 columns with R/S/C)
                reactions = row.get("reactions", 0)
                shares = row.get("shares", 0)
                comments = row.get("comments", 0)
                
                html += f'''<!-- Table Row {i} -->
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 80px; top: {top_pos}px; width: 50px; height: 35px; z-index: 205; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #6b7280;">{row["stt"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 150px; top: {top_pos}px; width: 320px; height: 35px; z-index: 206;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #111827; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{content}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 490px; top: {top_pos}px; width: 80px; height: 35px; z-index: 207; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #4b5563;">{pub_date}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 590px; top: {top_pos}px; width: 80px; height: 35px; z-index: 208; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #4b5563;">{row["channel"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 690px; top: {top_pos}px; width: 140px; height: 35px; z-index: 209;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #4b5563; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{site_name}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 850px; top: {top_pos}px; width: 80px; height: 35px; z-index: 210; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #6b7280;">{reactions:,}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 950px; top: {top_pos}px; width: 80px; height: 35px; z-index: 211; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #6b7280;">{shares:,}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 1050px; top: {top_pos}px; width: 80px; height: 35px; z-index: 212; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #6b7280;">{comments:,}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 1150px; top: {top_pos}px; width: 50px; height: 35px; z-index: 213; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px;"><a href="{row["url"]}" style="color: #0045c4; text-decoration: none;" target="_blank">Link</a></p>
</div>
'''
            else:
                # Use regular template layout (6 columns)
                html += f'''<!-- Table Row {i} -->
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 80px; top: {top_pos}px; width: 50px; height: 35px; z-index: 205; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #6b7280;">{row["stt"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 150px; top: {top_pos}px; width: 420px; height: 35px; z-index: 206;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #111827; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{content}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 590px; top: {top_pos}px; width: 100px; height: 35px; z-index: 207; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563;">{pub_date}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 710px; top: {top_pos}px; width: 100px; height: 35px; z-index: 208; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563;">{row["channel"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 830px; top: {top_pos}px; width: 180px; height: 35px; z-index: 209;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{site_name}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 1030px; top: {top_pos}px; width: 170px; height: 35px; z-index: 210; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px;"><a href="{row["url"]}" style="color: #0045c4; text-decoration: none;" target="_blank">Xem chi tiết</a></p>
</div>
'''
            
            # Separator
            if i < len(table_rows):
                html += f'''<!-- Row Separator {i} -->
<div data-object="true" data-object-type="shape" style="position: absolute; left: 80px; top: {sep_pos}px; width: 1120px; height: 1px; background-color: #e5e7eb; z-index: 201;"></div>
'''
        
        return html
    
    def _generate_table_rows_slide08(self, table_rows: List[Dict]) -> str:
        """Generate HTML for table rows in slide 8 (Positive Posts)."""
        html = ""
        for i, row in enumerate(table_rows, 1):
            top_pos = 235 + (i - 1) * 40  # Changed from 215 to 235 (20px offset)
            sep_pos = top_pos + 30
            
            # Truncate content to fit column width
            content = row["content"][:90] + "..." if len(row["content"]) > 90 else row["content"]
            
            # Format date (DD/MM/YYYY)
            pub_date = row["published_date"][:10] if len(row["published_date"]) >= 10 else row["published_date"]
            
            # Truncate site name
            site_name = row["site_name"][:18] + "..." if len(row["site_name"]) > 18 else row["site_name"]
            
            html += f'''<!-- Table Row {i} -->
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 70px; top: {top_pos}px; width: 40px; height: 35px; z-index: 205; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #6b7280;">{row["stt"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 120px; top: {top_pos}px; width: 500px; height: 35px; z-index: 206;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #111827; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{content}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 630px; top: {top_pos}px; width: 90px; height: 35px; z-index: 207; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563;">{pub_date}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 730px; top: {top_pos}px; width: 80px; height: 35px; z-index: 207; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563;">{row["channel"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 820px; top: {top_pos}px; width: 140px; height: 35px; z-index: 207;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{site_name}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 970px; top: {top_pos}px; width: 80px; height: 35px; z-index: 207; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; font-weight: 700; color: #00C055;">{row["positive_comments"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 1060px; top: {top_pos}px; width: 140px; height: 35px; z-index: 207; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px;"><a href="{row["url"]}" style="color: #0045c4; text-decoration: none;" target="_blank">Xem chi tiết</a></p>
</div>
'''
            # Separator
            if i < len(table_rows):
                html += f'''<!-- Row Separator {i} -->
<div data-object="true" data-object-type="shape" style="position: absolute; left: 70px; top: {sep_pos}px; width: 1140px; height: 1px; background-color: #e5e7eb; z-index: 201;"></div>
'''
        
        return html
    
    def _generate_table_rows_slide10(self, table_rows: List[Dict]) -> str:
        """Generate HTML for table rows in slide 10 (Negative Posts)."""
        html = ""
        for i, row in enumerate(table_rows, 1):
            top_pos = 235 + (i - 1) * 40  # Changed from 215 to 235 (20px offset)
            sep_pos = top_pos + 30
            
            # Truncate content to fit column width (same as slide 8)
            content = row["content"][:90] + "..." if len(row["content"]) > 90 else row["content"]
            
            # Format date (DD/MM/YYYY)
            pub_date = row["published_date"][:10] if len(row["published_date"]) >= 10 else row["published_date"]
            
            # Truncate site name (same as slide 8)
            site_name = row["site_name"][:18] + "..." if len(row["site_name"]) > 18 else row["site_name"]
            
            html += f'''<!-- Table Row {i} -->
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 70px; top: {top_pos}px; width: 40px; height: 35px; z-index: 205; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #6b7280;">{row["stt"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 120px; top: {top_pos}px; width: 500px; height: 35px; z-index: 206;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #111827; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{content}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 630px; top: {top_pos}px; width: 90px; height: 35px; z-index: 207; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563;">{pub_date}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 730px; top: {top_pos}px; width: 80px; height: 35px; z-index: 207; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563;">{row["channel"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 820px; top: {top_pos}px; width: 140px; height: 35px; z-index: 207;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{site_name}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 970px; top: {top_pos}px; width: 80px; height: 35px; z-index: 207; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; font-weight: 700; color: #EC003F;">{row["negative_comments"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 1060px; top: {top_pos}px; width: 140px; height: 35px; z-index: 207; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px;"><a href="{row["url"]}" style="color: #0045c4; text-decoration: none;" target="_blank">Xem chi tiết</a></p>
</div>
'''
            # Separator
            if i < len(table_rows):
                html += f'''<!-- Row Separator {i} -->
<div data-object="true" data-object-type="shape" style="position: absolute; left: 70px; top: {sep_pos}px; width: 1140px; height: 1px; background-color: #e5e7eb; z-index: 201;"></div>
'''
        
        return html
    
    def _replace_sentiment_data(self, html: str, data: Dict[str, Any]) -> str:
        """Replace sentiment chart data in slide 6."""
        # Replace NSR values in JavaScript
        html = re.sub(
            r'const nsrLastWeek = [\d.]+;',
            f'const nsrLastWeek = {data["previous_nsr"]};',
            html
        )
        html = re.sub(
            r'const nsrThisWeek = [\d.]+;',
            f'const nsrThisWeek = {data["current_nsr"]};',
            html
        )
        
        # Replace NSR display values in center text
        # Last week NSR
        html = html.replace(
            '<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 24px; font-weight: 700; color: #111827;">55.9%</p>',
            f'<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 24px; font-weight: 700; color: #111827;">{data["previous_nsr"]:.1f}%</p>'
        )
        
        # This week NSR
        html = html.replace(
            '<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 24px; font-weight: 700; color: #0045c4;">38.5%</p>',
            f'<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 24px; font-weight: 700; color: #0045c4;">{data["current_nsr"]:.1f}%</p>'
        )
        
        # Replace NSR growth percentage
        nsr_growth = data.get("nsr_growth", 0)
        growth_symbol = "↑" if nsr_growth >= 0 else "↓"
        growth_color = "#00c055" if nsr_growth >= 0 else "#EC003F"
        
        # Find and replace the growth text (show actual value, not absolute)
        old_growth = '<span style="color: #EC003F; font-weight: 600;">↓ 17.12%</span>'
        new_growth = f'<span style="color: {growth_color}; font-weight: 600;">{growth_symbol} {nsr_growth:.2f}%</span>'
        html = html.replace(old_growth, new_growth)
        
        # ===== STEP 1: Replace stacked bar chart data FIRST =====
        topics = data["top_topics_with_sentiment"]
        labels = [t["topic"] for t in topics]
        
        # Store raw counts for tooltip
        positive_counts = [t["positive"] for t in topics]
        neutral_counts = [t["neutral"] for t in topics]
        negative_counts = [t["negative"] for t in topics]
        
        # Calculate percentages for each topic (normalize to 100%)
        positive_data = []
        neutral_data = []
        negative_data = []
        
        for t in topics:
            total = t["total"]
            if total > 0:
                positive_pct = round((t["positive"] / total) * 100, 1)
                neutral_pct = round((t["neutral"] / total) * 100, 1)
                negative_pct = round((t["negative"] / total) * 100, 1)
            else:
                positive_pct = neutral_pct = negative_pct = 0
            
            positive_data.append(positive_pct)
            neutral_data.append(neutral_pct)
            negative_data.append(negative_pct)
        
        # Use json.dumps with ensure_ascii=False to preserve Vietnamese characters
        labels_json = json.dumps(labels, ensure_ascii=False)
        positive_json = json.dumps(positive_data)
        neutral_json = json.dumps(neutral_data)
        negative_json = json.dumps(negative_data)
        
        # Store raw counts as JSON for tooltip access
        positive_counts_json = json.dumps(positive_counts)
        neutral_counts_json = json.dumps(neutral_counts)
        negative_counts_json = json.dumps(negative_counts)
        
        # Replace raw counts in JavaScript
        old_raw_counts = """const rawCounts = {
            positive: [49, 49, 8, 10, 19, 6, 1, 6, 41, 1],
            neutral: [604, 604, 601, 453, 382, 181, 29, 59, 7, 41],
            negative: [0, 0, 0, 2, 0, 0, 52, 8, 0, 1]
        };"""
        new_raw_counts = f"""const rawCounts = {{
            positive: {positive_counts_json},
            neutral: {neutral_counts_json},
            negative: {negative_counts_json}
        }};"""
        html = html.replace(old_raw_counts, new_raw_counts)
        
        # Find the old labels section in the BAR CHART (after "type: 'bar'")
        start_marker = "labels: ["
        end_marker = "],"
        start_idx = html.find(start_marker, html.find("type: 'bar'"))
        if start_idx != -1:
            end_idx = html.find(end_marker, start_idx) + len(end_marker)
            old_labels_section = html[start_idx:end_idx]
            new_labels_section = f"labels: {labels_json},"
            html = html.replace(old_labels_section, new_labels_section, 1)
        
        # Replace bar chart datasets using more precise pattern matching
        bar_chart_start = html.find("type: 'bar'")
        
        if bar_chart_start == -1:
            print("WARNING: Could not find bar chart in HTML")
            return html
        
        # Replace positive data - find pattern: label: 'Tích cực', followed by data: [...]
        pos_pattern = r"(label:\s*'Tích cực',\s*data:\s*)\[[^\]]+\]"
        pos_replacement = rf"\g<1>{positive_json}"
        html = re.sub(pos_pattern, pos_replacement, html, count=1)
        
        # Replace neutral data
        neu_pattern = r"(label:\s*'Trung lập',\s*data:\s*)\[[^\]]+\]"
        neu_replacement = rf"\g<1>{neutral_json}"
        html = re.sub(neu_pattern, neu_replacement, html, count=1)
        
        # Replace negative data
        neg_pattern = r"(label:\s*'Tiêu cực',\s*data:\s*)\[[^\]]+\]"
        neg_replacement = rf"\g<1>{negative_json}"
        html = re.sub(neg_pattern, neg_replacement, html, count=1)
        
        # ===== STEP 2: Replace donut chart data AFTER bar chart =====
        # Replace donut chart data for last week - use raw counts, not percentages
        # Chart.js will automatically calculate percentages from raw values
        prev_sent = {s["sentiment"]: s["count"] for s in data["previous_sentiment"]}
        prev_neutral = prev_sent.get("Neutral", 0)
        prev_positive = prev_sent.get("Positive", 0)
        prev_negative = prev_sent.get("Negative", 0)
        
        print(f"DEBUG - Previous sentiment: Neutral={prev_neutral}, Positive={prev_positive}, Negative={prev_negative}")
        
        # Use simple string replacement for donut chart data (more reliable than regex)
        old_data_last = "data: [90.7, 7.3, 2.1],"
        new_data_last = f"data: [{prev_neutral}, {prev_positive}, {prev_negative}],"
        if old_data_last in html:
            html = html.replace(old_data_last, new_data_last, 1)
            print(f"DEBUG - Replaced donut last week: [{prev_neutral}, {prev_positive}, {prev_negative}]")
        else:
            print(f"WARNING - Could not find donut last week data pattern")
        
        # Replace donut chart data for this week - use raw counts, not percentages
        curr_sent = {s["sentiment"]: s["count"] for s in data["current_sentiment"]}
        curr_neutral = curr_sent.get("Neutral", 0)
        curr_positive = curr_sent.get("Positive", 0)
        curr_negative = curr_sent.get("Negative", 0)
        
        print(f"DEBUG - Current sentiment: Neutral={curr_neutral}, Positive={curr_positive}, Negative={curr_negative}")
        
        # Use simple string replacement for donut chart data
        old_data_this = "data: [91.6, 5.8, 2.6],"
        new_data_this = f"data: [{curr_neutral}, {curr_positive}, {curr_negative}],"
        if old_data_this in html:
            html = html.replace(old_data_this, new_data_this, 1)
            print(f"DEBUG - Replaced donut this week: [{curr_neutral}, {curr_positive}, {curr_negative}]")
        else:
            print(f"WARNING - Could not find donut this week data pattern")
        
        return html
    
    def merge_slide12(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 12 (Brand Ranking Table)."""
        html_path = self.html_dir / "slide12.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        
        # Replace title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Generate table rows dynamically
        table_rows_html = self._generate_table_rows_slide12(data["table"])
        
        # Replace all hardcoded table rows - match from first row comment to before page number
        # This pattern captures everything from "<!-- Table Row 1 -->" to just before "<!-- Page Number -->"
        pattern = r'<!-- Table Row 1 -->.*?(?=<!-- Page Number -->)'
        html = re.sub(pattern, table_rows_html + '\n', html, flags=re.DOTALL)
        
        return html
        return html
    
    def merge_slide13(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 13 (Brand Trendline)."""
        html_path = self.html_dir / "slide13.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        
        # Replace title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Replace subtitle
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 18px; color: #4b5563;">)[^<]+(</p>)',
            rf'\g<1>{data["subtitle"]}\g<2>',
            html,
            count=1
        )
        
        # Replace trendline data, legend, and annotations
        html = self._replace_multi_brand_trendline(html, data)
        
        # Generate top topics list HTML
        top_topics_html = self._generate_top_topics_html(data.get("top_topics", []))
        
        # Replace topic list container content
        pattern = r'(<div id="topicListContainer"[^>]*>)[\s\S]*?(</div>)'
        html = re.sub(pattern, rf'\g<1>\n{top_topics_html}\n\g<2>', html, count=1)
        
        return html
    
    def _generate_top_topics_html(self, top_topics: List[Dict]) -> str:
        """Generate HTML for top 5 topics with representative posts."""
        if not top_topics:
            return '<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 13px; color: #6b7280;">Không có dữ liệu</p>'
        
        html = ""
        for i, topic in enumerate(top_topics, 1):
            topic_name = topic["topic"]
            total_mentions = topic["total_mentions"]
            post_text = topic["post_text"]
            comment_count = topic["comment_count"]
            url = topic["url"]
            
            # Topic item with border
            border_style = "border-bottom: 1px solid #e5e7eb;" if i < len(top_topics) else ""
            
            html += f'''
<div style="padding: 12px 0; {border_style}">
    <div style="display: flex; align-items: center; margin-bottom: 6px;">
        <span style="font-family: 'Product Sans', sans-serif; font-size: 14px; font-weight: 700; color: #0045c4; margin-right: 8px;">{i}.</span>
        <span style="font-family: 'Product Sans', sans-serif; font-size: 14px; font-weight: 700; color: #111827;">{topic_name}</span>
        <span style="font-family: 'Product Sans', sans-serif; font-size: 12px; color: #6b7280; margin-left: auto;">({total_mentions:,} lượt)</span>
    </div>
    <p style="margin: 0 0 6px 0; font-family: 'Product Sans', sans-serif; font-size: 12px; color: #4b5563; line-height: 1.4;">{post_text}</p>
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <span style="font-family: 'Product Sans', sans-serif; font-size: 11px; color: #6b7280;">💬 {comment_count:,} bình luận</span>
        <a href="{url}" target="_blank" style="font-family: 'Product Sans', sans-serif; font-size: 11px; color: #0045c4; text-decoration: none;">Xem chi tiết →</a>
    </div>
</div>
'''
        
        return html
    
    def _get_brand_color(self, index: int) -> str:
        """Get brand color by index."""
        colors = ["#1D6FA4", "#F4A261", "#E63946", "#7B2D8B", "#2A9D5C", "#E76F51", "#264653"]
        return colors[index % len(colors)]
    
    def merge_slide14(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 14 (Channel Distribution - Multi-brand)."""
        html_path = self.html_dir / "slide14.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        
        # Replace title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Replace insight sections using placeholders
        insight_sections = data["insight_sections"]
        
        # Find and replace each insight by group name
        for section in insight_sections:
            group = section["group"]
            summary = section["summary"]
            placeholder = f"{{{{{group.upper()}_INSIGHT}}}}"
            
            if placeholder in html:
                html = html.replace(placeholder, summary)
        
        # Replace stacked bar chart data
        html = self._replace_stacked_bar_chart(html, data["stacked_bar_chart"])
        
        return html
    
    def merge_slide15(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 15 (Topic Sentiment Analysis)."""
        html_path = self.html_dir / "slide15.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280; white-space: nowrap;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        
        # Replace title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Replace insight placeholder
        insight = data["insight"]
        html = html.replace("{{INSIGHT}}", insight)
        
        # Replace stacked bar chart data
        html = self._replace_sentiment_stacked_bar(html, data["stacked_bar_chart"])
        
        # Replace summary table
        html = self._replace_sentiment_summary_table(html, data["summary_table"])
        
        return html
    
    def merge_slide16(self, data: Dict[str, Any], date_range: str) -> str:
        """Merge data into slide 16 (Top Commented Posts)."""
        html_path = self.html_dir / "slide16.html"
        html = html_path.read_text(encoding="utf-8")
        
        # Replace date range
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 16px; color: #6b7280;">)[^<]+(</p>)',
            rf'\g<1>{date_range}\g<2>',
            html,
            count=1
        )
        
        # Replace title
        html = re.sub(
            r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 36px; font-weight: 700; color: #111827;">)[^<]+(</p>)',
            rf'\g<1>{data["title"]}\g<2>',
            html,
            count=1
        )
        
        # Generate table rows dynamically
        table_rows_html = self._generate_table_rows_slide16(data["table"])
        
        # Replace table rows using comment marker
        pattern = r'(<!-- Table rows will be dynamically generated -->)'
        replacement = rf'<!-- Table rows will be dynamically generated -->\n{table_rows_html}'
        html = re.sub(pattern, replacement, html, count=1)
        
        return html
    
    def _generate_table_rows_slide12(self, table_rows: List[Dict]) -> str:
        """Generate HTML for table rows in slide 12 (Brand Ranking)."""
        html = ""
        for i, row in enumerate(table_rows, 1):
            top_pos = 215 + (i - 1) * 40
            sep_pos = top_pos + 30
            
            # Format percentage change with color
            pct = row["pct_change"]
            if pct > 0:
                pct_str = f"↑ {pct:.1f}%"
                pct_color = "#00c055"
            elif pct < 0:
                pct_str = f"↓ {abs(pct):.1f}%"
                pct_color = "#EC003F"
            else:
                pct_str = "0%"
                pct_color = "#6b7280"
            
            html += f'''<!-- Table Row {i} -->
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 80px; top: {top_pos}px; width: 80px; height: 20px; z-index: 205; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #6b7280;">{row["stt"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 180px; top: {top_pos}px; width: 500px; height: 20px; z-index: 206;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; color: #111827;">{row["brand"]}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 720px; top: {top_pos}px; width: 200px; height: 20px; z-index: 207; text-align: right;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; font-weight: 700; color: #0045c4;">{row["total"]:,}</p>
</div>
<div data-object="true" data-object-type="textbox" style="position: absolute; left: 960px; top: {top_pos}px; width: 220px; height: 20px; z-index: 208; text-align: right;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; font-weight: 700; color: {pct_color};">{pct_str}</p>
</div>
'''
            # Separator (except for last row)
            if i < len(table_rows):
                html += f'''<!-- Row Separator {i} -->
<div data-object="true" data-object-type="shape" style="position: absolute; left: 80px; top: {sep_pos}px; width: 1120px; height: 1px; background-color: #e5e7eb; z-index: 201;"></div>
'''
        
        return html
    
    def _generate_table_rows_slide16(self, table_rows: List[Dict]) -> str:
        """Generate HTML for table rows in slide 16 (Top Commented Posts)."""
        html = ""
        for i, row in enumerate(table_rows, 1):
            top_pos = 225 + (i - 1) * 40
            sep_pos = top_pos + 30
            
            # Truncate content to fit column width
            content = row["content"][:85] + "..." if len(row["content"]) > 85 else row["content"]
            
            # Truncate brand name
            topic = row["topic"][:18] + "..." if len(row["topic"]) > 18 else row["topic"]
            
            # Truncate site name
            site_name = row["source_name"][:20] + "..." if len(row["source_name"]) > 20 else row["source_name"]
            
            html += f'''<!-- Table Row {i} -->
<div style="position: absolute; left: 70px; top: {top_pos}px; width: 50px; height: 35px; z-index: 205; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #6b7280;">{row["stt"]}</p>
</div>
<div style="position: absolute; left: 130px; top: {top_pos}px; width: 140px; height: 35px; z-index: 206;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #111827; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{topic}</p>
</div>
<div style="position: absolute; left: 280px; top: {top_pos}px; width: 380px; height: 35px; z-index: 207;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #111827; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{content}</p>
</div>
<div style="position: absolute; left: 670px; top: {top_pos}px; width: 90px; height: 35px; z-index: 208; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563;">{row["channel"]}</p>
</div>
<div style="position: absolute; left: 770px; top: {top_pos}px; width: 160px; height: 35px; z-index: 209;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px; color: #4b5563; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{site_name}</p>
</div>
<div style="position: absolute; left: 940px; top: {top_pos}px; width: 110px; height: 35px; z-index: 210; text-align: center;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 14px; font-weight: 700; color: #0045c4;">{row["comment_count"]:,}</p>
</div>
<div style="position: absolute; left: 1060px; top: {top_pos}px; width: 150px; height: 35px; z-index: 211;">
<p style="margin: 0; font-family: 'Product Sans', sans-serif; font-size: 13px;"><a href="{row["source_url"]}" style="color: #0045c4; text-decoration: none;" target="_blank">Xem chi tiết</a></p>
</div>
'''
            # Separator
            if i < len(table_rows):
                html += f'''<!-- Row Separator {i} -->
<div style="position: absolute; left: 70px; top: {sep_pos}px; width: 1140px; height: 1px; background-color: #e5e7eb; z-index: 201;"></div>
'''
        
        return html
    
    def _replace_multi_brand_trendline(self, html: str, data: Dict[str, Any]) -> str:
        """Replace multi-brand trendline chart data in slide 13."""
        brands = data["brands"]
        trendlines = data["trendlines"]
        annotations = data.get("annotations", {})
        
        # Build datasets for Chart.js with full styling
        datasets = []
        colors = ["#1D6FA4", "#F4A261", "#E63946", "#7B2D8B", "#2A9D5C", "#E76F51", "#264653"]
        
        # Get dates from first brand's trendline (all brands should have same dates)
        if brands and brands[0] in trendlines:
            dates = [d["date"] for d in trendlines[brands[0]]]
            # Format as DD/MM for display
            labels = [f"{d.split('-')[2]}/{d.split('-')[1]}" for d in dates]
        else:
            labels = []
            dates = []
        
        # Build datasets with actual data values
        for i, brand in enumerate(brands):
            color = colors[i % len(colors)]
            brand_data = trendlines.get(brand, [])
            
            # Extract values in same order as dates
            values = [d["mentions"] for d in brand_data]
            
            datasets.append({
                "label": brand,
                "data": values,
                "borderColor": color,
                "backgroundColor": color,
                "borderWidth": 2,
                "pointRadius": 4,
                "pointBackgroundColor": "#ffffff",
                "pointBorderWidth": 2,
                "tension": 0.3
            })
        
        # Replace chart data
        labels_json = json.dumps(labels, ensure_ascii=False)
        datasets_json = json.dumps(datasets, ensure_ascii=False)
        
        # Replace empty labels array
        html = html.replace(
            "labels: [],",
            f"labels: {labels_json},"
        )
        
        # Replace empty datasets array
        html = html.replace(
            "datasets: []",
            f"datasets: {datasets_json}"
        )
        
        # Replace custom legend
        html = self._replace_custom_legend(html, brands, colors)
        
        # Replace annotations (peak points) - pass dates for verification
        html = self._replace_annotations(html, annotations, labels, colors, brands, dates)
        
        # Replace insight/footer text
        if "subtitle" in data:
            html = re.sub(
                r'(<p style="margin: 0; font-family: \'Inter\', sans-serif; font-size: 18px; color: #4b5563;">)[^<]+(</p>)',
                rf'\g<1>{data["subtitle"]}\g<2>',
                html,
                count=1
            )
        
        return html
    
    def _replace_custom_legend(self, html: str, brands: List[str], colors: List[str]) -> str:
        """Replace custom legend for multi-brand trendline (horizontal layout)."""
        legend_items = []
        
        for i, brand in enumerate(brands):
            color = colors[i % len(colors)]
            legend_items.append(f'''<div style="display: flex; align-items: center; gap: 6px;">
    <div style="position: relative; width: 16px; height: 8px;">
        <div style="position: absolute; left: 0; top: 2px; width: 16px; height: 4px; background-color: {color}; border-radius: 2px;"></div>
        <div style="position: absolute; left: 4px; top: 0; width: 8px; height: 8px; background-color: {color}; border-radius: 50%; border: 2px solid #fff;"></div>
    </div>
    <span style="font-family: 'Product Sans', sans-serif; font-size: 12px; font-weight: 600; color: #374151;">{brand}</span>
</div>''')
        
        legend_html = '\n'.join(legend_items)
        
        # Replace the legend section - find the div with id="chartLegend" and replace its content
        pattern = r'(<div id="chartLegend"[^>]*>[\s\S]*?<div[^>]*>)([\s\S]*?)(</div>[\s\S]*?</div>)'
        replacement = rf'\g<1>\n{legend_html}\n\g<3>'
        html = re.sub(pattern, replacement, html, count=1)
        
        return html
    
    def _replace_annotations(self, html: str, annotations: Dict[str, Dict], 
                            labels: List[str], colors: List[str], brands: List[str],
                            dates: List[str]) -> str:
        """Replace Chart.js annotations for peak points.
        
        Args:
            html: HTML template
            annotations: Dict mapping brand -> {date, mentions, snippet, url}
            labels: List of formatted date labels (DD/MM)
            colors: List of brand colors
            brands: List of brand names
            dates: List of raw dates (YYYY-MM-DD) matching labels
        """
        if not annotations:
            # Remove all annotations if none provided
            annotations_pattern = r'annotation:\s*\{[\s\S]*?\}\s*(?=\}[\s\S]*?\}[\s\S]*?\}[\s\S]*?$)'
            html = re.sub(annotations_pattern, '', html)
            return html
        
        # Build annotations object
        annotations_obj = {}
        
        for i, brand in enumerate(brands):
            if brand not in annotations:
                continue
            
            ann = annotations[brand]
            color = colors[i % len(colors)]
            
            # Get peak date from annotation
            peak_date_str = ann["date"]  # YYYY-MM-DD format
            
            # Verify this date exists in our date range
            if peak_date_str not in dates:
                print(f"Warning: Peak date {peak_date_str} for {brand} not in date range")
                continue
            
            # Format as DD/MM for chart x-axis
            date_label = f"{peak_date_str.split('-')[2]}/{peak_date_str.split('-')[1]}"
            
            # Verify the label exists in labels array
            if date_label not in labels:
                print(f"Warning: Date label {date_label} for {brand} not in labels")
                continue
            
            # Truncate snippet to fit (max 30 chars)
            snippet = ann.get("snippet", "")
            if len(snippet) > 30:
                snippet = snippet[:30] + "..."
            
            # Create annotation key (remove spaces from brand name)
            ann_key = f"peak{brand.replace(' ', '').replace('-', '')}"
            
            # ALWAYS position above the peak point
            annotations_obj[ann_key] = {
                "type": "label",
                "xValue": date_label,
                "yValue": ann["mentions"],
                "backgroundColor": f"rgba({self._hex_to_rgb(color)}, 0.1)",
                "borderRadius": 4,
                "color": color,
                "content": [snippet],
                "font": {"size": 10, "family": "Inter"},
                "position": "start",  # Always start (above)
                "yAdjust": -25 - (i * 5),  # Stagger vertically to avoid overlap
                "callout": {"display": True, "side": 5}
            }
            
            # Add click handler if URL exists
            if ann.get("url"):
                url = ann["url"].replace("'", "\\'")  # Escape single quotes
                annotations_obj[ann_key]["click"] = f"function() {{ window.open('{url}', '_blank'); }}"
        
        # If no valid annotations, remove annotation plugin
        if not annotations_obj:
            annotations_pattern = r'annotation:\s*\{[\s\S]*?\}\s*(?=\}[\s\S]*?\}[\s\S]*?\}[\s\S]*?$)'
            html = re.sub(annotations_pattern, '', html)
            return html
        
        # Convert to JSON (but keep click function as string)
        annotations_json = json.dumps(annotations_obj, ensure_ascii=False, indent=20)
        
        # Replace click function strings with actual functions
        for key in annotations_obj:
            if "click" in annotations_obj[key]:
                click_func = annotations_obj[key]["click"]
                annotations_json = annotations_json.replace(f'"{click_func}"', click_func)
        
        # Replace annotations in HTML - simple string replacement
        # Find the empty annotations object and replace it
        old_annotations = """annotation: {
                        annotations: {
                        }
                    }"""
        
        new_annotations = f"""annotation: {{
                        annotations: {annotations_json}
                    }}"""
        
        if old_annotations in html:
            html = html.replace(old_annotations, new_annotations)
        else:
            # Fallback: try with different whitespace
            print("Warning: Could not find annotation placeholder in HTML")
        
        return html
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string for rgba()."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    
    def _replace_stacked_bar_chart(self, html: str, chart_data: Dict[str, Any]) -> str:
        """Replace stacked bar chart data for channel distribution."""
        bar_data = chart_data["data"]
        
        # Extract labels (brand names) and totals
        labels = [d["topic"] for d in bar_data]
        totals = [d["total"] for d in bar_data]
        
        # Build data arrays for each channel group (using counts, not percentages)
        channel_groups = ["Fanpage", "Facebook", "Tiktok", "Youtube", "News", "Others"]
        data_arrays = {group: [] for group in channel_groups}
        
        for brand_data in bar_data:
            for group in channel_groups:
                # Find segment for this group
                segment = next((s for s in brand_data["segments"] if s["group"] == group), None)
                if segment:
                    data_arrays[group].append(segment["count"])
                else:
                    data_arrays[group].append(0)
        
        # Replace brands array
        brands_json = json.dumps(labels, ensure_ascii=False)
        html = html.replace("const brands = [];", f"const brands = {brands_json};")
        
        # Replace totals array
        totals_json = json.dumps(totals)
        html = html.replace("const totals = [];", f"const totals = {totals_json};")
        
        # Replace data arrays for each channel
        for group in channel_groups:
            data_json = json.dumps(data_arrays[group])
            var_name = f"data{group}"
            html = html.replace(f"const {var_name} = [];", f"const {var_name} = {data_json};")
        
        return html
    
    def _replace_sentiment_stacked_bar(self, html: str, chart_data: Dict[str, Any]) -> str:
        """Replace sentiment stacked bar chart data."""
        bar_data = chart_data["data"]
        
        # Extract labels (topic names) and totals
        labels = [d["topic"] for d in bar_data]
        totals = [d["total"] for d in bar_data]
        
        # Build datasets for each sentiment
        sentiments = ["Positive", "Neutral", "Negative"]
        datasets = []
        
        for sentiment in sentiments:
            data_values = []
            color = None
            
            for topic_data in bar_data:
                # Find segment for this sentiment
                segment = next((s for s in topic_data["segments"] if s["sentiment"] == sentiment), None)
                if segment:
                    data_values.append(segment["count"])
                    if color is None:
                        color = segment["color"]
                else:
                    data_values.append(0)
            
            # Map sentiment to Vietnamese label
            label_map = {"Positive": "Tích cực", "Neutral": "Trung lập", "Negative": "Tiêu cực"}
            
            datasets.append({
                "label": label_map.get(sentiment, sentiment),
                "data": data_values,
                "backgroundColor": color or "#ADB5BD"
            })
        
        # Replace chart data
        labels_json = json.dumps(labels, ensure_ascii=False)
        datasets_json = json.dumps(datasets, ensure_ascii=False)
        totals_json = json.dumps(totals)
        
        # Replace labels
        html = html.replace("labels: [],", f"labels: {labels_json},")
        
        # Replace datasets
        html = html.replace("datasets: []", f"datasets: {datasets_json}")
        
        # Replace totals array
        html = html.replace("const totals = [];", f"const totals = {totals_json};")
        
        return html
    
    def _replace_sentiment_summary_table(self, html: str, summary_table: Dict[str, Any]) -> str:
        """Replace sentiment summary table in slide 15."""
        topics = summary_table["topics"]
        nsr_week1_map = summary_table["nsr_week1"]
        nsr_week2_map = summary_table["nsr_week2"]
        nsr_change_map = summary_table["nsr_change"]
        positive_posts_map = summary_table["positive_posts"]
        negative_posts_map = summary_table["negative_posts"]
        
        # Generate table rows
        table_rows = ""
        for topic in topics:
            nsr_week1 = nsr_week1_map.get(topic, 0)
            nsr_week2 = nsr_week2_map.get(topic, 0)
            nsr_change = nsr_change_map.get(topic, 0)
            
            # Format NSR tuần trước with color (no + sign for positive)
            if nsr_week2 >= 0:
                nsr2_str = f"{nsr_week2:.1f}%"
                nsr2_class = "nsr-positive"
            else:
                nsr2_str = f"{nsr_week2:.1f}%"
                nsr2_class = "nsr-negative"
            
            # Format NSR tuần này with color (no + sign for positive)
            if nsr_week1 >= 0:
                nsr1_str = f"{nsr_week1:.1f}%"
                nsr1_class = "nsr-positive"
            else:
                nsr1_str = f"{nsr_week1:.1f}%"
                nsr1_class = "nsr-negative"
            
            # Format NSR change (difference between week1 and week2)
            # No + sign for positive values
            if nsr_change > 0:
                change_str = f"{nsr_change:.1f}%"
                change_class = "nsr-positive"
            elif nsr_change < 0:
                change_str = f"{nsr_change:.1f}%"
                change_class = "nsr-negative"
            else:
                change_str = "0%"
                change_class = "nsr-neutral"
            
            # Get sample posts
            pos_posts = positive_posts_map.get(topic, [])
            neg_posts = negative_posts_map.get(topic, [])
            
            if pos_posts:
                pos_text = pos_posts[0]["text"][:60] + "..." if len(pos_posts[0]["text"]) > 60 else pos_posts[0]["text"]
                pos_url = pos_posts[0]["url"] if pos_posts[0]["url"] else "#"
            else:
                pos_text = "N/A"
                pos_url = "#"
            
            if neg_posts:
                neg_text = neg_posts[0]["text"][:60] + "..." if len(neg_posts[0]["text"]) > 60 else neg_posts[0]["text"]
                neg_url = neg_posts[0]["url"] if neg_posts[0]["url"] else "#"
            else:
                neg_text = "N/A"
                neg_url = "#"
            
            table_rows += f'''<tr>
<td style="font-weight: 600;">{topic}</td>
<td class="{nsr2_class}" style="text-align: center;">{nsr2_str}</td>
<td class="{nsr1_class}" style="text-align: center;">{nsr1_str}</td>
<td class="{change_class}" style="text-align: center;">{change_str}</td>
<td><a href="{pos_url}" style="color: #0045c4; text-decoration: none;" target="_blank">{pos_text}</a></td>
<td><a href="{neg_url}" style="color: #0045c4; text-decoration: none;" target="_blank">{neg_text}</a></td>
</tr>
'''
        
        # Replace tbody content
        pattern = r'(<tbody>)\s*<!-- Table rows will be dynamically generated -->\s*(</tbody>)'
        replacement = rf'\g<1>\n{table_rows}\g<2>'
        html = re.sub(pattern, replacement, html, flags=re.DOTALL)
        
        return html
    
    def _format_insight_sections(self, sections: List[Dict]) -> str:
        """Format insight sections with colored headers for slide 14."""
        html = '<p style="margin: 0 0 5px 0; font-family: \'Inter\', sans-serif; font-size: 13px; font-weight: 700; color: #374151;">PHÂN TÍCH THEO KÊNH:</p>\n'
        
        for section in sections:
            group = section["group"]
            color = section["color"]
            summary = section["summary"]
            
            # Format summary with hyperlinks
            summary_formatted = self._format_insight_with_hyperlinks(summary)
            
            html += f'<p style="margin: 5px 0; font-family: \'Inter\', sans-serif; font-size: 12px; color: #374151; line-height: 1.5; text-align: justify;">'
            html += f'<span style="font-weight: 700; color: {color};">{group}:</span> {summary_formatted}'
            html += '</p>\n'
        
        return html
    
    def save_html(self, html: str, filename: str) -> Path:
        """Save merged HTML to output directory."""
        output_path = self.output_dir / filename
        output_path.write_text(html, encoding="utf-8")
        print(f"✓ Saved: {output_path}")
        return output_path
    
    def merge_all_slides(self, report_data: Dict[str, Any], slide_keys: List[str], 
                         date_range: str = "") -> str:
        """
        Merge all selected slides into a single long HTML document for PDF export.
        Each slide becomes a section/page in the final document.
        
        Args:
            report_data: Dictionary containing data for all slides
            slide_keys: List of slide keys to include (e.g., ['slide_1', 'slide_2', ...])
            date_range: Optional date range string for slide headers
            
        Returns:
            Complete HTML string with all slides as separate pages
        """
        # HTML wrapper for multi-page document
        html_header = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Report - Complete</title>
    <link href="https://fonts.cdnfonts.com/css/product-sans" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Product Sans', sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f5f7fa;
            color: #111827;
        }
        .page {
            width: 1280px;
            height: 720px;
            margin: 20px auto;
            position: relative;
            background: #f5f7fa;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            page-break-after: always;
            page-break-inside: avoid;
            overflow: hidden;
        }
        .page:last-child {
            margin-bottom: 20px;
        }
        @media print {
            body {
                background: #ffffff;
            }
            .page {
                margin: 0;
                box-shadow: none;
                page-break-after: always;
            }
        }
        @page {
            size: 1280px 720px;
            margin: 0;
        }
    </style>
</head>
<body>
"""
        html_footer = """
</body>
</html>
"""
        
        # Map slide keys to merge methods
        merge_methods = {
            "slide_1": self.merge_slide01,
            "slide_2": self.merge_slide02,
            "slide_3": self.merge_slide03,
            "slide_4": self.merge_slide04,
            "slide_5": self.merge_slide05,
            "slide_6": self.merge_slide06,
            "slide_7": self.merge_slide07,
            "slide_8": self.merge_slide08,
            "slide_9": self.merge_slide09,
            "slide_10": self.merge_slide10,
            "slide_11": self.merge_slide11,
            "slide_12": self.merge_slide12,
            "slide_13": self.merge_slide13,
            "slide_14": self.merge_slide14,
            "slide_15": self.merge_slide15,
            "slide_16": self.merge_slide16,
        }
        
        # Collect all slide HTML
        pages_html = []
        for idx, key in enumerate(slide_keys, 1):
            if key not in report_data:
                continue
            
            merge_method = merge_methods.get(key)
            if not merge_method:
                continue
            
            try:
                # Get merged slide HTML
                slide_html = merge_method(report_data[key], date_range)
                
                # Make canvas IDs and chart variable names unique by adding slide index
                # Replace canvas IDs: id="barChart" -> id="barChart_slide1"
                slide_html = re.sub(
                    r'id="([^"]+)"',
                    lambda m: f'id="{m.group(1)}_slide{idx}"',
                    slide_html
                )
                
                # Replace getElementById references in scripts
                slide_html = re.sub(
                    r'getElementById\(["\']([^"\']+)["\']\)',
                    lambda m: f'getElementById("{m.group(1)}_slide{idx}")',
                    slide_html
                )
                
                # Replace ALL common JavaScript variable names to avoid conflicts
                # Pattern: const/let/var VARNAME = 
                common_vars = [
                    'ctx', 'data', 'maxValue', 'maxIndex', 'labels', 'values',
                    'total', 'colors', 'datasets', 'options', 'chart',
                    'nsrLastWeek', 'nsrThisWeek', 'statusLastWeek', 'statusThisWeek',
                    'rawCounts', 'percentages', 'numTopics', 'donut_w2', 'donut_w1',
                    'total_w2', 'total_w1', 'donut_w2_pct', 'donut_w1_pct',
                    'bar_data', 'bar_labels', 'bar_week_before', 'bar_current_week',
                    'topics', 'positive_counts', 'neutral_counts', 'negative_counts',
                    'positive_data', 'neutral_data', 'negative_data'
                ]
                
                for var_name in common_vars:
                    # Replace variable declarations: const ctx = -> const ctx_slide1 =
                    slide_html = re.sub(
                        rf'\b(const|let|var)\s+{var_name}\s*=',
                        rf'\g<1> {var_name}_slide{idx} =',
                        slide_html
                    )
                    # Replace variable usage in code (but not in strings)
                    # This is tricky - we'll use word boundaries to avoid replacing inside strings
                    slide_html = re.sub(
                        rf'\b{var_name}\b(?=\s*[;\.,\)\]\+\-\*/=<>!&|\s])',
                        f'{var_name}_slide{idx}',
                        slide_html
                    )
                
                # Replace chart variable names: const barChart = -> const barChart_slide1 =
                slide_html = re.sub(
                    r'\b(const|let|var)\s+(\w+Chart)\s*=',
                    lambda m: f'{m.group(1)} {m.group(2)}_slide{idx} =',
                    slide_html
                )
                
                # Extract slide-container content AND any scripts after it (before </body>)
                # Pattern: extract from <div class="slide-container"> to </body>
                match = re.search(r'<div class="slide-container">(.*?)</body>', slide_html, re.DOTALL)
                if match:
                    slide_content = match.group(1)
                    pages_html.append(f'<div class="page">\n{slide_content}\n</div>')
                else:
                    # Fallback: wrap entire slide HTML
                    pages_html.append(f'<div class="page">\n{slide_html}\n</div>')
                    
            except Exception as e:
                print(f"Warning: Failed to merge {key}: {e}")
                continue
        
        # Combine all pages
        return html_header + "\n".join(pages_html) + html_footer


def main():
    """
    Main execution function - FOR TESTING ONLY.
    This uses EXAMPLE DATA to test the merge functionality.
    
    In production, use app_template_html.py which generates data from real Excel files.
    """
    print("\n" + "="*60)
    print("⚠️  TESTING MODE - Using example data")
    print("="*60)
    
    merger = SlideHTMLMerger()
    
    # EXAMPLE data for slide 1 (for testing only)
    # In production, this data comes from slide01_overview.py with real Excel data
    slide01_data = {
        "title": "TỔNG QUAN LƯỢNG ĐỀ CẬP CỦA BIDV",
        "subtitle": "Tổng quan lược đề cập trong tuần",
        "current_week_metrics": [
            {"label": "Tổng bài đăng", "value": 3809, "change_percent": 97.66},
            {"label": "Tổng bình luận", "value": 1782, "change_percent": -25.9},
            {"label": "Tổng thảo luận", "value": 5591, "change_percent": 29.06}
        ],
        "weekly_comparison": [
            {"week": "3 tuần trước", "total_mentions": 7030, "growth_rate": None},
            {"week": "2 tuần trước", "total_mentions": 7211, "growth_rate": 2.57},
            {"week": "Tuần trước", "total_mentions": 4332, "growth_rate": -39.92},
            {"week": "Tuần hiện tại", "total_mentions": 5591, "growth_rate": 29.06}
        ],
        "insight": "Số lượng thảo luận về BIDV trong tuần này là 5591 lượt, tăng nhẹ so với tuần trước..."
    }
    
    # EXAMPLE data for slide 2 (for testing only)
    # In production, this data comes from slide02_trendline.py with real Excel data
    slide02_data = {
        "title": "XU HƯỚNG ĐỀ CẬP CỦA BIDV THEO THỜI GIAN",
        "subtitle": "Phân tích biến động lượng thảo luận theo ngày",
        "trendline": [
            {"date": "2026-02-21", "mentions": 78},
            {"date": "2026-02-22", "mentions": 214},
            {"date": "2026-02-23", "mentions": 755},
            {"date": "2026-02-24", "mentions": 987},
            {"date": "2026-02-25", "mentions": 1187},
            {"date": "2026-02-26", "mentions": 1061},
            {"date": "2026-02-27", "mentions": 1135}
            # NOTE: 7 days only (21-27 Feb), not 8 days
        ],
        "insight": """DIỄN BIẾN CHÍNH:
2026-02-21 - Không biết các Newbie ở đây, có ai là người cũ còn nhớ Amy huyền thoại ko 😂😂 Ae hồi...
2026-02-22 - Sóng DN Nhà Nước đầu 2026 đã Kết Thúc? Các DN Nhà nước đang đóng góp ~1/3 GDP, giữ vị...
2026-02-23 - Ngày làm việc mà anh chị em mong đợi nhất trong năm không phải ngày cuối trước nghỉ tết mà...
2026-02-24 - 1 lần rút được 30tr tại ATM từ khi nào vậy mọi người !? #ATM #bidv
2026-02-25 - Không việc gì phải vay với 15-16%, gói vay này của BIDV sẽ giúp bạn giảm phân nửa lãi suất....
2026-02-26 - #danhtrochoi #bidv #nganhang Đi làm ngày zui nhất là ngày nhận lương
2026-02-27 - VTB, BIDV, MSB, NCB, HDB CHÍNH THỨC DỪNG GIẢI NGÂN BĐS DỰ ÁN..."""
    }
    
    # EXAMPLE data for slide 3 (for testing only)
    # In production, this data comes from slide03_channels.py with real Excel data
    slide03_data = {
        "title": "PHÂN BỔ ĐỀ CẬP VỀ BIDV TRÊN CÁC KÊNH TRỰC TUYẾN",
        "subtitle": "Phân tích tỷ trọng thảo luận theo nền tảng và nguồn tin",
        "channel_distribution": [
            {"Channel": "News", "count": 2966},
            {"Channel": "Facebook", "count": 1261},
            {"Channel": "Tiktok", "count": 1084},
            {"Channel": "Social", "count": 183},
            {"Channel": "Youtube", "count": 86},
            {"Channel": "Threads", "count": 11}
        ],
        "top_sources": [
            {"SiteName": "baomoi.com", "count": 488},
            {"SiteName": "BIDV", "count": 453},
            {"SiteName": "kienthuckinhte28", "count": 402},
            {"SiteName": "dnse.com.vn", "count": 248},
            {"SiteName": "phu_nhadat", "count": 184},
            {"SiteName": "fireant.vn", "count": 183},
            {"SiteName": "chuyendongthitruong.vn", "count": 162},
            {"SiteName": "nguoiquansat.vn", "count": 129},
            {"SiteName": "cafef.vn", "count": 120},
            {"SiteName": "vietnambiz.vn", "count": 104}
        ],
        "insight": "Trong tuần từ 21/02/2026 đến 28/02/2026, kênh News dẫn đầu về số lượng thảo luận về BIDV với 2966 lượt đề cập, cho thấy báo chí vẫn là nguồn thông tin chính về ngân hàng này [Nguồn: https://www.tiktok.com/@andocapital/video/7610698792068844808]. Facebook và TikTok cũng đóng góp đáng kể với 1261 và 1084 lượt thảo luận, thể hiện sự quan tâm của công chúng trên các nền tảng mạng xã hội này [Nguồn: https://www.tiktok.com/@nguyentrungphucbds/video/7611371448829070613]. Về các nguồn tin, baomoi.com nổi bật với 488 lượt đề cập, cho thấy đây là một cổng thông tin được nhiều người theo dõi về các vấn đề liên quan đến BIDV [Nguồn: https://www.tiktok.com/@phu_nhadat/video/7610418439609421077]. Bên cạnh đó, trang web chính thức của BIDV cũng xuất hiện với 453 lượt đề cập, cho thấy người dùng thường xuyên tìm kiếm thông tin trực tiếp từ ngân hàng [Nguồn: https://kienthuckinhte28.com]."
    }
    
    date_range = "21/02/2026 → 28/02/2026"
    
    print("\n⚠️  Note: These are EXAMPLE numbers for testing.")
    print("    Use app_template_html.py for real data from Excel files.\n")
    
    # Merge and save slide 1
    print("📄 Processing Slide 1...")
    html1 = merger.merge_slide01(slide01_data, date_range)
    merger.save_html(html1, "slide1_merged.html")
    
    # Merge and save slide 2
    print("\n📄 Processing Slide 2...")
    html2 = merger.merge_slide02(slide02_data, date_range)
    merger.save_html(html2, "slide2_merged.html")
    
    # Merge and save slide 3
    print("\n📄 Processing Slide 3...")
    html3 = merger.merge_slide03(slide03_data, date_range)
    merger.save_html(html3, "slide3_merged.html")
    
    print("\n✅ Done! Check the 'output' directory for merged HTML files.")


if __name__ == "__main__":
    main()
