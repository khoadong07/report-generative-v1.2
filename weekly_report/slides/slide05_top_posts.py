"""
Slide 05 – Top posts by engagement (table, no LLM)
Input:  week1_df, brand, week1_display, show_interactions
Output: {title, subtitle, table_rows, show_interactions}
"""
from typing import Any, Dict, List
import pandas as pd

from weekly_report.slides.base import SlideGenerator


class Slide05TopPosts(SlideGenerator):
    """Top posts ranked by comments (or plain listing when no interactions)."""

    def __init__(self, topic_types: List[str], top_n: int = 10):
        self.topic_types = topic_types
        self.top_n = top_n

    def generate(self, *, week1_df: pd.DataFrame, brand: str,
                 week1_display: str, show_interactions: bool = True) -> Dict[str, Any]:

        df = week1_df[week1_df["Type"].isin(self.topic_types)].copy()

        if show_interactions:
            # Check if we have individual metrics
            has_comments = "Comments" in df.columns
            
            if has_comments:
                # Sort by Comments (original logic)
                df = df.sort_values("Comments", ascending=False).head(self.top_n)
                has_r = "Reactions" in df.columns
                has_s = "Shares" in df.columns

                table_rows = []
                for i, r in enumerate(df.itertuples(), 1):
                    content = str(r.Content) if pd.notna(r.Content) else str(r.Title)
                    row = {
                        "stt": i, "content": content,
                        "published_date": str(r.PublishedDate),
                        "channel": str(r.Channel),
                        "site_name": str(r.SiteName),
                        "url": str(r.UrlTopic),
                    }
                    if has_r: row["reactions"] = int(r.Reactions)
                    if has_s: row["shares"]    = int(r.Shares)
                    row["comments"] = int(r.Comments)
                    table_rows.append(row)
            else:
                # No interaction metrics available
                show_interactions = False
                df = df.head(self.top_n)
                table_rows = [
                    {"stt": i,
                     "content": str(r.Content) if pd.notna(r.Content) else str(r.Title),
                     "published_date": str(r.PublishedDate),
                     "channel": str(r.Channel),
                     "site_name": str(r.SiteName),
                     "url": str(r.UrlTopic)}
                    for i, r in enumerate(df.itertuples(), 1)
                ]
        elif "Comments" in df.columns:
            df = df.sort_values("Comments", ascending=False).head(self.top_n)
            df = df.head(self.top_n)
            table_rows = [
                {"stt": i,
                 "content": str(r.Content) if pd.notna(r.Content) else str(r.Title),
                 "published_date": str(r.PublishedDate),
                 "channel": str(r.Channel),
                 "site_name": str(r.SiteName),
                 "url": str(r.UrlTopic)}
                for i, r in enumerate(df.itertuples(), 1)
            ]
        else:
            df = df.head(self.top_n)
            table_rows = [
                {"stt": i,
                 "content": str(r.Content) if pd.notna(r.Content) else str(r.Title),
                 "published_date": str(r.PublishedDate),
                 "channel": str(r.Channel),
                 "site_name": str(r.SiteName),
                 "url": str(r.UrlTopic)}
                for i, r in enumerate(df.itertuples(), 1)
            ]

        title = "TOP BÀI ĐĂNG CÓ TƯƠNG TÁC CAO NHẤT" if show_interactions else "TOP BÀI ĐĂNG NỔI BẬT"
        return {
            "title":             title,
            "subtitle":          f"",
            "table_rows":        table_rows,
            "show_interactions": show_interactions,
        }
