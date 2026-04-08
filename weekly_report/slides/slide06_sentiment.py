"""
Slide 06 – Sentiment analysis: 2 pie charts + topic breakdown + NSR + insight
Input:  week1_df, week2_df, brand, week1_display
Output: {title, subtitle, current_sentiment, previous_sentiment,
         current_nsr, previous_nsr, nsr_growth, top_topics_with_sentiment, insight}
"""
from typing import Any, Dict, List
import pandas as pd

from core.data_loader import calculate_percentage_change, calculate_engagement
from core.llm_client import LLMClient
from weekly_report.slides.base import SlideGenerator, InsightMixin
from weekly_report.prompts import get_weekly_sentiment_insight_prompt


class Slide06Sentiment(SlideGenerator, InsightMixin):
    """Sentiment analysis slide."""

    def __init__(self, llm_client: LLMClient, topic_types: List[str]):
        self.llm_client = llm_client
        self.topic_types = topic_types

    def generate(self, *, week1_df: pd.DataFrame, week2_df: pd.DataFrame,
                 brand: str, week1_display: str) -> Dict[str, Any]:

        w1 = week1_df.copy(); w1["Sentiment"] = w1["Sentiment"].str.capitalize()
        w2 = week2_df.copy(); w2["Sentiment"] = w2["Sentiment"].str.capitalize()

        curr_sent = self._sentiment_counts(w1)
        prev_sent = self._sentiment_counts(w2)

        curr_nsr = self._nsr(curr_sent)
        prev_nsr = self._nsr(prev_sent)
        nsr_growth = curr_nsr - prev_nsr

        top_topics = self._top_topics_with_sentiment(w1)
        insight = self._generate_insight(week1_df=w1, brand=brand,
                                         week1_display=week1_display,
                                         top_topics=top_topics)

        return {
            "title":                   f"PHÂN TÍCH SẮC THÁI ĐỀ CẬP CỦA {brand.upper()}",
            "subtitle":                f"Phân tích chỉ số cảm xúc (Sentiment) và các chủ đề thảo luận chính",
            "current_sentiment":       curr_sent,
            "previous_sentiment":      prev_sent,
            "current_nsr":             round(curr_nsr, 2),
            "previous_nsr":            round(prev_nsr, 2),
            "nsr_growth":              round(nsr_growth, 2),
            "top_topics_with_sentiment": top_topics,
            "insight":                 insight,
        }

    # ── helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _sentiment_counts(df: pd.DataFrame) -> List[Dict]:
        """Return sentiment counts in fixed order: Neutral, Positive, Negative"""
        counts = df["Sentiment"].value_counts().to_dict()
        # Return in fixed order to match chart labels
        return [
            {"sentiment": "Neutral", "count": counts.get("Neutral", 0)},
            {"sentiment": "Positive", "count": counts.get("Positive", 0)},
            {"sentiment": "Negative", "count": counts.get("Negative", 0)},
        ]

    @staticmethod
    def _nsr(sentiment_list: List[Dict]) -> float:
        total = sum(s["count"] for s in sentiment_list)
        if total == 0:
            return 0.0
        pos = sum(s["count"] for s in sentiment_list if s["sentiment"] == "Positive")
        neg = sum(s["count"] for s in sentiment_list if s["sentiment"] == "Negative")
        pos_pct = pos / total * 100; neg_pct = neg / total * 100
        denom = pos_pct + neg_pct
        return ((pos_pct - neg_pct) / denom * 100) if denom > 0 else 0.0

    def _top_topics_with_sentiment(self, df: pd.DataFrame) -> List[Dict]:
        topic_sent = df.groupby(["Labels1", "Sentiment"]).size().reset_index(name="count")
        summary = (topic_sent.groupby("Labels1")["count"].sum()
                   .reset_index()
                   .sort_values("count", ascending=False)
                   .head(10))
        result = []
        for topic in summary["Labels1"]:
            sub = topic_sent[topic_sent["Labels1"] == topic]
            breakdown = {r["Sentiment"]: int(r["count"]) for _, r in sub.iterrows()}
            result.append({
                "topic":    topic,
                "total":    int(summary[summary["Labels1"] == topic]["count"].iloc[0]),
                "negative": breakdown.get("Negative", 0),
                "neutral":  breakdown.get("Neutral",  0),
                "positive": breakdown.get("Positive", 0),
            })
        return result

    def _generate_insight(self, *, week1_df: pd.DataFrame, brand: str,
                          week1_display: str, top_topics: List[Dict]) -> str:
        df_topics = week1_df[week1_df["Type"].isin(self.topic_types)].copy()
        if df_topics.empty:
            return (f"Phân tích sắc thái về {brand.upper()} trong giai đoạn {week1_display}. "
                    "Không có dữ liệu bài đăng chính (topics) để phân tích chi tiết.")

        df_topics["engagement"] = calculate_engagement(df_topics)
        df_top = df_topics.sort_values("engagement", ascending=False).head(5)
        context_text = "\n\n---\n\n".join([
            f"Labels1: {r['Labels1']}\nSentiment: {r['Sentiment']}\nTiêu đề: {r['Title']}\nNội dung: {r['Content']}\nURL: {r['UrlTopic']}"
            for _, r in df_top.iterrows()
        ])
        prompt = get_weekly_sentiment_insight_prompt(brand, week1_display, top_topics, context_text)
        insight = self.llm_client.generate_insight(prompt)
        
        # Truncate to 250 words if needed
        words = insight.split()
        if len(words) > 250:
            insight = ' '.join(words[:250]) + '...'
        
        return insight
