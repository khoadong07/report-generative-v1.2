"""
Slide 03 – Channel distribution + top 10 sources
Input:  week1_df, brand, week1_display
Output: {title, subtitle, channel_distribution, top_sources, insight}
"""
from typing import Any, Dict, List
import pandas as pd

from core.data_loader import calculate_engagement
from core.llm_client import LLMClient
from weekly_report.slides.base import SlideGenerator, InsightMixin
from weekly_report.prompts import get_weekly_channel_insight_prompt


class Slide03Channels(SlideGenerator, InsightMixin):
    """Generate channel distribution slide."""

    def __init__(self, llm_client: LLMClient, topic_types: List[str]):
        self.llm_client = llm_client
        self.topic_types = topic_types

    def generate(self, *, week1_df: pd.DataFrame, brand: str,
                 week1_display: str) -> Dict[str, Any]:

        channel_dist = (week1_df.groupby("Channel").size()
                        .reset_index(name="count")
                        .sort_values("count", ascending=False))

        top_sources = (week1_df.groupby("SiteName").size()
                       .reset_index(name="count")
                       .sort_values("count", ascending=False)
                       .head(10))

        insight = self._generate_insight(
            week1_df=week1_df, brand=brand, week1_display=week1_display,
            channel_dist=channel_dist, top_sources=top_sources
        )

        return {
            "title":                f"PHÂN BỔ ĐỀ CẬP VỀ {brand.upper()} TRÊN CÁC KÊNH TRỰC TUYẾN",
            "subtitle":             f"",
            "channel_distribution": channel_dist.to_dict(orient="records"),
            "top_sources":          top_sources.to_dict(orient="records"),
            "insight":              insight,
        }

    def _generate_insight(self, *, week1_df: pd.DataFrame, brand: str,
                          week1_display: str, channel_dist: pd.DataFrame,
                          top_sources: pd.DataFrame) -> str:
        df_topics = week1_df[week1_df["Type"].isin(self.topic_types)].copy()
        if df_topics.empty:
            return (f"Phân bố thảo luận về {brand.upper()} trên các kênh trong giai đoạn {week1_display}. "
                    "Không có dữ liệu bài đăng chính (topics) để phân tích chi tiết.")

        df_topics["engagement"] = calculate_engagement(df_topics)
        df_top = df_topics.sort_values("engagement", ascending=False).head(3)
        context_text = "\n\n---\n\n".join([
            f"Channel: {r['Channel']}\nSiteName: {r['SiteName']}\nTiêu đề: {r['Title']}\nURL: {r['UrlTopic']}"
            for _, r in df_top.iterrows()
        ])
        prompt = get_weekly_channel_insight_prompt(
            brand, week1_display,
            channel_dist.to_string(index=False),
            top_sources.to_string(index=False),
            context_text
        )
        return self.llm_client.generate_insight(prompt)
