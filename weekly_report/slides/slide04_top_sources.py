"""
Slide 04 – Top sources by engagement (table, no LLM)
Input:  week1_df, brand, week1_display, show_interactions
Output: {title, subtitle, table_rows, show_interactions}
"""
from typing import Any, Dict, List
import pandas as pd

from core.data_loader import calculate_engagement
from weekly_report.slides.base import SlideGenerator


class Slide04TopSources(SlideGenerator):
    """Top sources ranked by engagement or mention count."""

    def __init__(self, topic_types: List[str], top_n: int = 10):
        self.topic_types = topic_types
        self.top_n = top_n

    def generate(self, *, week1_df: pd.DataFrame, brand: str,
                 week1_display: str, show_interactions: bool = True) -> Dict[str, Any]:

        df = week1_df[week1_df["Type"].isin(self.topic_types)].copy()
        df["engagement"] = calculate_engagement(df)

        if show_interactions:
            # Check if we have individual metrics
            has_individual_metrics = {"Reactions", "Shares", "Comments"}.issubset(df.columns)
            
            if has_individual_metrics:
                # Use individual metrics (always calculate from R+S+C)
                agg = (df.groupby("SiteName")
                       .agg(engagement=("engagement", "sum"),
                            Reactions=("Reactions", "sum"),
                            Shares=("Shares", "sum"),
                            Comments=("Comments", "sum"))
                       .reset_index()
                       .sort_values("engagement", ascending=False)
                       .head(self.top_n))

                table_rows = [
                    {"stt": i, "source_name": r.SiteName,
                     "total_engagement": int(r.engagement),
                     "reactions": int(r.Reactions),
                     "shares": int(r.Shares),
                     "comments": int(r.Comments)}
                    for i, r in enumerate(agg.itertuples(), 1)
                ]
            else:
                # Fallback to count mode
                show_interactions = False
                agg = (df.groupby("SiteName").size()
                       .reset_index(name="count")
                       .sort_values("count", ascending=False)
                       .head(self.top_n))
                table_rows = [
                    {"stt": i, "source_name": r.SiteName, "count": int(r.count)}
                    for i, r in enumerate(agg.itertuples(), 1)
                ]
        else:
            agg = (df.groupby("SiteName").size()
                   .reset_index(name="count")
                   .sort_values("count", ascending=False)
                   .head(self.top_n))
            table_rows = [
                {"stt": i, "source_name": r.SiteName, "count": int(r.count)}
                for i, r in enumerate(agg.itertuples(), 1)
            ]

        title = "Top nguồn có lượng tương tác cao nhất" if show_interactions else "Top nguồn có lượng đề cập cao nhất"
        return {
            "title":             title,
            "subtitle":          f"",
            "table_rows":        table_rows,
            "show_interactions": show_interactions,
        }
