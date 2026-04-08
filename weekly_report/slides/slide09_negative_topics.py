"""
Slide 09 – Negative topics chart + insight
Input:  week1_df, brand, week1_display
Output: {title, subtitle, negative_topics: [{Labels1, count}], insight}
"""
from typing import Any, Dict, List
import pandas as pd

from core.data_loader import calculate_engagement
from core.llm_client import LLMClient
from weekly_report.slides.base import SlideGenerator, InsightMixin
from weekly_report.prompts import get_weekly_negative_insight_prompt


class Slide09NegativeTopics(SlideGenerator, InsightMixin):
    """Negative topics analysis slide."""

    def __init__(self, llm_client: LLMClient, topic_types: List[str]):
        self.llm_client = llm_client
        self.topic_types = topic_types

    def generate(self, *, week1_df: pd.DataFrame, brand: str,
                 week1_display: str) -> Dict[str, Any]:

        df_neg = week1_df[
            (week1_df["Sentiment"].str.lower() == "negative") &
            (week1_df["Type"].isin(self.topic_types))
        ].copy()

        if df_neg.empty:
            return {
                "title":           f"CHỦ ĐỀ TẠO NÊN ĐỀ CẬP TIÊU CỰC",
                "subtitle":        f"Top 10 chủ đề nhận được phản hồi tiêu cực từ cộng đồng",
                "negative_topics": [{"Labels1": "Không xác định", "count": 0}],
                "insight":         f"Không có dữ liệu đề cập tiêu cực về {brand.upper()} trong giai đoạn {week1_display}.",
            }

        df_neg["Labels1"] = df_neg["Labels1"].fillna("Không xác định").replace("", "Không xác định")
        agg = (df_neg.groupby("Labels1").size()
               .reset_index(name="count")
               .sort_values("count", ascending=False)
               .head(10))

        insight = self._generate_insight(
            df_negative=df_neg, brand=brand,
            week1_display=week1_display, negative_topics=agg
        )

        return {
            "title":           f"CHỦ ĐỀ TẠO NÊN ĐỀ CẬP TIÊU CỰC",
            "subtitle":        f"Top 10 chủ đề nhận được phản hồi tiêu cực từ cộng đồng",
            "negative_topics": agg.to_dict(orient="records"),
            "insight":         insight,
        }

    def _generate_insight(self, *, df_negative: pd.DataFrame, brand: str,
                          week1_display: str, negative_topics: pd.DataFrame) -> str:
        df_negative = df_negative.copy()
        df_negative["engagement"] = calculate_engagement(df_negative)
        df_top = df_negative.sort_values("engagement", ascending=False).head(5)
        context_text = "\n\n---\n\n".join([
            f"Labels1: {r['Labels1']}\nTiêu đề: {r['Title']}\nNội dung: {r['Content']}\nURL: {r['UrlTopic']}"
            for _, r in df_top.iterrows()
        ])
        prompt = get_weekly_negative_insight_prompt(
            brand, week1_display, negative_topics.to_string(index=False), context_text
        )
        return self.llm_client.generate_insight(prompt)
