"""
Slide 13 – Multi-brand daily trendline + peak annotations
Input:  week1_all_df, brand, week1_display, week1_start_date, week1_end_date, brands_filter
Output: {title, subtitle, brands, trendlines, annotations}
"""
from typing import Any, Dict, List, Optional
import pandas as pd

from core.data_loader import calculate_engagement
from weekly_report.slides.base import SlideGenerator


class Slide13BrandTrendline(SlideGenerator):
    """Multi-brand trendline with peak annotations."""

    def __init__(self, topic_types: List[str]):
        self.topic_types = topic_types

    def generate(self, *, week1_df: pd.DataFrame, brand: str,
                 week1_display: str, week1_start_date: str, week1_end_date: str,
                 brands_filter: Optional[List[str]] = None) -> Dict[str, Any]:

        all_brands = (
            [b for b in brands_filter if b in week1_df["Topic"].values]
            if brands_filter
            else sorted(week1_df["Topic"].dropna().unique().tolist())
        )

        start = pd.to_datetime(week1_start_date).date()
        end   = pd.to_datetime(week1_end_date).date()
        date_range = [d.date() for d in pd.date_range(start=start, end=end, freq="D")]

        trendlines: Dict[str, List[Dict]] = {}
        for b in all_brands:
            daily = week1_df[week1_df["Topic"] == b].groupby("PublishedDay").size().to_dict()
            trendlines[b] = [{"date": str(d), "mentions": int(daily.get(d, 0))} for d in date_range]

        annotations: Dict[str, Dict] = {}
        for b in all_brands:
            df_b = week1_df[week1_df["Topic"] == b]
            if df_b.empty:
                continue
            daily_counts = df_b.groupby("PublishedDay").size()
            if daily_counts.empty:
                continue
            peak_day   = daily_counts.idxmax()
            peak_count = int(daily_counts[peak_day])

            # Filter posts on peak day with valid URLs
            df_peak = df_b[
                (df_b["PublishedDay"] == peak_day) &
                (df_b["Type"].isin(self.topic_types)) &
                (df_b["UrlTopic"].notna()) &
                (df_b["UrlTopic"].astype(str).str.startswith("http"))
            ].copy()

            if df_peak.empty:
                df_peak = df_b[
                    (df_b["PublishedDay"] == peak_day) &
                    (df_b["UrlTopic"].notna()) &
                    (df_b["UrlTopic"].astype(str).str.startswith("http"))
                ].copy()

            if df_peak.empty:
                continue

            # Sort by Comments (highest first), fallback to engagement if Comments not available
            if "Comments" in df_peak.columns:
                # Convert Comments to numeric, fill NaN with 0
                df_peak["_comments"] = pd.to_numeric(df_peak["Comments"], errors="coerce").fillna(0)
                best = df_peak.sort_values("_comments", ascending=False).iloc[0]
            else:
                # Fallback to engagement if Comments column doesn't exist
                df_peak["_eng"] = calculate_engagement(df_peak)
                best = df_peak.sort_values("_eng", ascending=False).iloc[0]
            
            raw  = str(best.get("Title") or best.get("Content") or "").strip()
            words = raw.split()
            snippet = " ".join(words[:5]) + "..." if len(words) > 5 else raw

            annotations[b] = {
                "date":     str(peak_day),
                "mentions": peak_count,
                "snippet":  snippet,
                "url":      str(best.get("UrlTopic", "")),
                "type":     str(best.get("Type", "")),
            }

        # Get top 5 topics with representative posts (highest comment count)
        top_topics = self._get_top_topics_with_posts(week1_df, all_brands)

        return {
            "title":       f"XU HƯỚNG ĐỀ CẬP CỦA CÁC THƯƠNG HIỆU THEO THỜI GIAN",
            "subtitle":    f"Diễn biến thảo luận theo này và các sự kiện nổi bật tạo đỉnh thảo luận",
            "brands":      all_brands,
            "trendlines":  trendlines,
            "annotations": annotations,
            "top_topics":  top_topics,
        }

    def _get_top_topics_with_posts(self, df: pd.DataFrame, all_brands: List[str]) -> List[Dict]:
        """Get top 5 posts with highest comment count from selected brands."""
        # Filter only topics that are in all_brands (selected brand and competitors)
        df_filtered = df[
            (df["Topic"].isin(all_brands)) &
            (df["Type"].isin(self.topic_types)) &
            (df["UrlTopic"].notna()) &
            (df["UrlTopic"].astype(str).str.startswith("http"))
        ].copy()
        
        if df_filtered.empty:
            # Fallback: any post with valid URL
            df_filtered = df[
                (df["Topic"].isin(all_brands)) &
                (df["UrlTopic"].notna()) &
                (df["UrlTopic"].astype(str).str.startswith("http"))
            ].copy()
        
        if df_filtered.empty:
            return []
        
        # Convert Comments to numeric and sort by comment count (highest first)
        if "Comments" in df_filtered.columns:
            df_filtered["_comments"] = pd.to_numeric(df_filtered["Comments"], errors="coerce").fillna(0)
        else:
            df_filtered["_comments"] = 0
        
        # Sort by comment count and get top 5
        df_top5 = df_filtered.sort_values("_comments", ascending=False).head(5)
        
        result = []
        for _, row in df_top5.iterrows():
            topic = row["Topic"]
            comment_count = int(row["_comments"])
            
            # Get post content
            title = str(row.get("Title") or "").strip()
            content = str(row.get("Content") or "").strip()
            post_text = title if title else content
            
            # Truncate to 100 characters
            if len(post_text) > 100:
                post_text = post_text[:100] + "..."
            
            # Count total mentions for this topic in the week
            total_mentions = int(df[df["Topic"] == topic].shape[0])
            
            result.append({
                "topic": topic,
                "total_mentions": total_mentions,
                "post_text": post_text,
                "comment_count": comment_count,
                "url": str(row.get("UrlTopic", "")),
            })
        
        return result
