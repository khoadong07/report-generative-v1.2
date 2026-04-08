"""
Slide 12 – Bảng xếp hạng tổng lượt thảo luận theo thương hiệu
Input:  week1_all_df, week2_all_df, brand, week1_display, brands_filter
Output: {title, subtitle, table}
  table: [{stt, brand, total, pct_change, change_color}]
"""
from typing import Any, Dict, List, Optional
import pandas as pd

from weekly_report.slides.base import SlideGenerator


class Slide12BrandRanking(SlideGenerator):
    """Brand mention ranking table with week-over-week change (data-only, no LLM)."""

    def generate(
        self,
        *,
        week1_df: pd.DataFrame,
        week2_df: pd.DataFrame,
        brand: str,
        week1_display: str,
        brands_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        # Resolve brand list
        if brands_filter:
            all_vals = set(week1_df["Topic"].values) | set(week2_df["Topic"].values)
            all_brands = [b for b in brands_filter if b in all_vals]
        else:
            all_brands = sorted(
                set(week1_df["Topic"].dropna()) | set(week2_df["Topic"].dropna())
            )

        rows = []
        for b in all_brands:
            w1c = int((week1_df["Topic"] == b).sum())
            w2c = int((week2_df["Topic"] == b).sum())

            # pct change – same logic as slide11
            if w2c > 0:
                pct = round((w1c - w2c) / w2c * 100, 1)
            elif w1c > 0:
                pct = 100.0
            else:
                pct = 0.0

            rows.append({
                "brand":        b,
                "total":        w1c,
                "pct_change":   pct,
                "change_color": "green" if pct >= 0 else "red",
            })

        # Sort by total descending, then assign STT
        rows.sort(key=lambda x: x["total"], reverse=True)
        for i, row in enumerate(rows):
            row["stt"] = i + 1

        return {
            "title":    "Bảng xếp hạng tổng lượt thảo luận theo thương hiệu",
            "subtitle": f"",
            "table":    rows,
        }
