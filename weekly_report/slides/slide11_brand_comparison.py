"""
Slide 11 – Brand comparison: donut charts + grouped bar chart + insight
Input:  week1_all_df, week2_all_df, brand, week1_display, brands_filter
Output: {title, subtitle, insight, donut_charts, legend, bar_chart}
"""
from typing import Any, Dict, List, Optional
import pandas as pd

from core.data_loader import calculate_percentage_change
from core.llm_client import LLMClient
from weekly_report.slides.base import SlideGenerator, InsightMixin
from weekly_report.prompts import get_weekly_brand_comparison_insight_prompt

_DISTINCT_COLORS = [
    "#E63946", "#1D6FA4", "#F4A261", "#7B2D8B", "#2A9D5C",
    "#E76F51", "#264653", "#F4C430", "#0077B6", "#C77DFF",
    "#6A994E", "#D62828",
]


class Slide11BrandComparison(SlideGenerator, InsightMixin):
    """Brand comparison overview slide."""

    def __init__(self, llm_client: LLMClient, topic_types: List[str]):
        self.llm_client = llm_client
        self.topic_types = topic_types

    def generate(self, *, week1_df: pd.DataFrame, week2_df: pd.DataFrame,
                 brand: str, week1_display: str,
                 brands_filter: Optional[List[str]] = None) -> Dict[str, Any]:

        all_brands = self._resolve_brands(week1_df, week2_df, brands_filter)

        m1 = {b: len(week1_df[week1_df["Topic"] == b]) for b in all_brands}
        m2 = {b: len(week2_df[week2_df["Topic"] == b]) for b in all_brands}

        donut_w1, donut_w2 = [], []
        for i, b in enumerate(all_brands):
            color = _DISTINCT_COLORS[i % len(_DISTINCT_COLORS)]
            donut_w1.append({"brand": b, "mentions": m1.get(b, 0), "color": color})
            donut_w2.append({"brand": b, "mentions": m2.get(b, 0), "color": color})

        bar_data = []
        for b in all_brands:
            w1c = m1.get(b, 0); w2c = m2.get(b, 0)
            if w2c > 0:
                pct = round((w1c - w2c) / w2c * 100, 1)
            elif w1c > 0:
                pct = 100.0
            else:
                pct = 0.0
            bar_data.append({
                "brand": b, "week_before": w2c, "current_week": w1c,
                "percentage_change": pct,
                "change_color": "green" if pct >= 0 else "red",
            })
        bar_data.sort(key=lambda x: x["current_week"], reverse=True)

        insight = self._generate_insight(
            week1_df=week1_df, week2_df=week2_df, brand=brand,
            week1_display=week1_display, all_brands=all_brands, m1=m1, m2=m2
        )

        return {
            "title":    f"Tổng quan đề cập về thương hiệu {brand.upper()} với các đối thủ",
            "subtitle": f"",
            "insight":  insight,
            "donut_charts": {
                "week_before":   {"title": "Tuần trước",    "data": donut_w2},
                "current_week":  {"title": "Tuần hiện tại", "data": donut_w1},
            },
            "legend":    [{"brand": d["brand"], "color": d["color"]} for d in donut_w1],
            "bar_chart": {"title": "Tổng đề cập của các thương hiệu", "data": bar_data},
        }

    # ── helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _resolve_brands(w1, w2, brands_filter):
        if brands_filter:
            all_vals = set(w1["Topic"].values) | set(w2["Topic"].values)
            return [b for b in brands_filter if b in all_vals]
        return sorted(set(w1["Topic"].dropna()) | set(w2["Topic"].dropna()))

    def _generate_insight(self, *, week1_df, week2_df, brand, week1_display,
                          all_brands, m1, m2) -> str:
        lines = []
        for b in all_brands:
            w1c = m1.get(b, 0); w2c = m2.get(b, 0)
            if w2c > 0:
                chg = f"{((w1c - w2c) / w2c * 100):+.1f}%"
            elif w1c > 0:
                chg = "+100% (mới xuất hiện)"
            else:
                chg = "0%"
            lines.append(f"- {b}: Tuần trước {w2c} lượt → Tuần này {w1c} lượt ({chg})")

        context_lines = []
        for b in all_brands:
            mask = (week1_df["Topic"] == b) & week1_df["UrlTopic"].notna()
            for _, r in week1_df[mask].head(3).iterrows():
                context_lines.append(
                    f"[{b}] Title: {str(r.get('Title',''))[:120]} | Type: {r.get('Type','')} | URL: {r.get('UrlTopic','')}"
                )

        prompt = get_weekly_brand_comparison_insight_prompt(
            brand, week1_display, "\n".join(lines), "\n".join(context_lines)
        )
        try:
            return self.llm_client.generate_insight(prompt)
        except Exception as e:
            print(f"Warning: LLM insight failed: {e}")
            return f"Phân tích so sánh thương hiệu {brand.upper()} với các đối thủ trong giai đoạn {week1_display}."
