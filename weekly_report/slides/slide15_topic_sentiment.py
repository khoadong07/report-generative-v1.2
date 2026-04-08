"""
Slide 15 – PHÂN TÍCH SẮC THÁI THẢO LUẬN CỦA CÁC THƯƠNG HIỆU theo Topic (multi-brand sentiment breakdown)
Input:  week1_all_df, week2_all_df, brand, week1_display, brands_filter
Output: {title, insight, stacked_bar_chart, sentiment_legend, summary_table}

Layout (3 hàng):
  Row 1 – Title + Insight (LLM)
  Row 2 – Stacked bar chart (Positive / Neutral / Negative) + legend
  Row 3 – Summary table:
    Thương hiệu \ NSR | Biến động (pct change vs tuần trước) | Bài đăng tích cực (URL) | Bài đăng tiêu cực (URL)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd

from core.llm_client import LLMClient
from weekly_report.slides.base import SlideGenerator, InsightMixin
from weekly_report.prompts import get_slide15_topic_sentiment_insight_prompt

# ── Fixed sentiment colors ────────────────────────────────────────────────────
SENTIMENT_COLORS: Dict[str, str] = {
    "Positive": "#2A9D5C",   # green
    "Neutral":  "#ADB5BD",   # grey
    "Negative": "#E63946",   # red
}
SENTIMENT_ORDER = ["Positive", "Neutral", "Negative"]

# Number of sample posts to extract per sentiment
_SAMPLE_N = 1


class Slide15TopicSentiment(SlideGenerator, InsightMixin):
    """Sentiment breakdown by Topic with LLM insight and summary table."""

    def __init__(self, llm_client: LLMClient, topic_types: List[str]):
        self.llm_client = llm_client
        self.topic_types = topic_types

    def generate(
        self,
        *,
        week1_df: pd.DataFrame,
        week2_df: pd.DataFrame,
        brand: str,
        week1_display: str,
        brands_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        all_topics = self._resolve_brands(week1_df, week2_df, brands_filter)

        df1 = week1_df.copy()
        df2 = week2_df.copy()

        # Normalise Sentiment column
        for df in (df1, df2):
            df["_sentiment"] = df["Sentiment"].fillna("Neutral").str.strip().str.capitalize()
            df["_sentiment"] = df["_sentiment"].apply(
                lambda s: s if s in SENTIMENT_COLORS else "Neutral"
            )

        # ── Stacked bar chart data ────────────────────────────────────────────
        bar_data: List[Dict] = []
        for topic in all_topics:
            df1_t = df1[df1["Topic"] == topic]
            total = len(df1_t)
            counts = df1_t["_sentiment"].value_counts().to_dict()

            segments: List[Dict] = []
            for sent in SENTIMENT_ORDER:
                count = int(counts.get(sent, 0))
                pct = round(count / total * 100, 1) if total > 0 else 0.0
                segments.append({
                    "sentiment": sent,
                    "count":     count,
                    "percent":   pct,
                    "color":     SENTIMENT_COLORS[sent],
                    "show_label": pct >= 5,
                })

            bar_data.append({
                "topic":    topic,
                "total":    total,
                "segments": segments,
            })

        bar_data.sort(key=lambda x: x["total"], reverse=True)

        # ── Summary table ─────────────────────────────────────────────────────
        summary_table = self._build_summary_table(df1, df2, all_topics)

        # ── LLM insight ───────────────────────────────────────────────────────
        insight = self._generate_insight(
            df=df1,
            brand=brand,
            week1_display=week1_display,
            all_topics=all_topics,
            bar_data=bar_data,
            summary_table=summary_table,
        )

        return {
            "title":   "PHÂN TÍCH SẮC THÁI THẢO LUẬN CỦA CÁC THƯƠNG HIỆU",
            "subtitle": "",
            "insight": insight,
            "stacked_bar_chart": {
                "title": f"Tỷ trọng sentiment theo Topic – {brand.upper()}",
                "data":  bar_data,
            },
            "sentiment_legend": [
                {"sentiment": s, "color": SENTIMENT_COLORS[s]} for s in SENTIMENT_ORDER
            ],
            "summary_table": summary_table,
        }

    @staticmethod
    def _resolve_brands(w1, w2, brands_filter):
        if brands_filter:
            all_vals = set(w1["Topic"].values) | set(w2["Topic"].values)
            return [b for b in brands_filter if b in all_vals]
        return sorted(set(w1["Topic"].dropna()) | set(w2["Topic"].dropna()))

    # ── Summary table builder ─────────────────────────────────────────────────
    def _build_summary_table(
        self, df1: pd.DataFrame, df2: pd.DataFrame, all_topics: List[str]
    ) -> Dict[str, Any]:
        """
        Columns:
          - Thương hiệu
          - NSR tuần trước (week2)
          - NSR tuần này (week1)
          - Biến động (week1 - week2)
          - Bài đăng tích cực
          - Bài đăng tiêu cực
        
        NSR formula (consistent with slide 6):
          NSR = ((pos_pct - neg_pct) / (pos_pct + neg_pct)) * 100
          where pos_pct and neg_pct are percentages relative to total posts
        """
        nsr_week1_map: Dict[str, float] = {}
        nsr_week2_map: Dict[str, float] = {}
        nsr_change_map: Dict[str, float] = {}
        positive_posts_map: Dict[str, List[Dict]] = {}
        negative_posts_map: Dict[str, List[Dict]] = {}

        for topic in all_topics:
            df1_t = df1[df1["Topic"] == topic]
            df2_t = df2[df2["Topic"] == topic]

            total1 = len(df1_t)
            total2 = len(df2_t)

            # NSR week1 (tuần này) - using same formula as slide 6
            # NSR = ((pos_pct - neg_pct) / (pos_pct + neg_pct)) * 100
            pos_count1 = int((df1_t["_sentiment"] == "Positive").sum())
            neg_count1 = int((df1_t["_sentiment"] == "Negative").sum())
            if total1 > 0:
                pos_pct1 = pos_count1 / total1 * 100
                neg_pct1 = neg_count1 / total1 * 100
                denom1 = pos_pct1 + neg_pct1
                nsr1 = round(((pos_pct1 - neg_pct1) / denom1 * 100), 1) if denom1 > 0 else 0.0
            else:
                nsr1 = 0.0
            nsr_week1_map[topic] = nsr1

            # NSR week2 (tuần trước) - using same formula as slide 6
            pos_count2 = int((df2_t["_sentiment"] == "Positive").sum())
            neg_count2 = int((df2_t["_sentiment"] == "Negative").sum())
            if total2 > 0:
                pos_pct2 = pos_count2 / total2 * 100
                neg_pct2 = neg_count2 / total2 * 100
                denom2 = pos_pct2 + neg_pct2
                nsr2 = round(((pos_pct2 - neg_pct2) / denom2 * 100), 1) if denom2 > 0 else 0.0
            else:
                nsr2 = 0.0
            nsr_week2_map[topic] = nsr2

            # Biến động NSR = NSR tuần này - NSR tuần trước
            nsr_change = round(nsr1 - nsr2, 1)
            nsr_change_map[topic] = nsr_change

            # Bài đăng tích cực – top _SAMPLE_N posts with URL
            df_pos = df1_t[df1_t["_sentiment"] == "Positive"]
            positive_posts_map[topic] = _extract_posts(df_pos, _SAMPLE_N)

            # Bài đăng tiêu cực – top _SAMPLE_N posts with URL
            df_neg = df1_t[df1_t["_sentiment"] == "Negative"]
            negative_posts_map[topic] = _extract_posts(df_neg, _SAMPLE_N)

        # Mark highest NSR
        max_nsr_topic = max(nsr_week1_map, key=lambda t: nsr_week1_map[t]) if nsr_week1_map else None

        return {
            "topics":          all_topics,
            "nsr_week1":       nsr_week1_map,
            "nsr_week2":       nsr_week2_map,
            "nsr_change":      nsr_change_map,
            "max_nsr_topic":   max_nsr_topic,
            "positive_posts":  positive_posts_map,
            "negative_posts":  negative_posts_map,
        }

    # ── LLM insight ───────────────────────────────────────────────────────────
    def _generate_insight(self, *, df, brand, week1_display,
                          all_topics, bar_data, summary_table) -> str:
        prompt = get_slide15_topic_sentiment_insight_prompt(
            brand=brand,
            week_display=week1_display,
            all_topics=all_topics,
            bar_data=bar_data,
            summary_table=summary_table,
        )
        try:
            return self.llm_client.generate_insight(prompt)
        except Exception as e:
            print(f"Warning: LLM insight failed for slide 15: {e}")
            lines = []
            for topic in all_topics:
                nsr = summary_table["NSR"].get(topic, 0)
                pct = summary_table["pct_change"].get(topic, 0)
                lines.append(f"- {topic}: NSR {nsr:+.1f}%, biến động {pct:+.1f}%")
            return "\n".join(lines)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _extract_posts(df: pd.DataFrame, n: int) -> List[Dict]:
    """Extract up to n posts, picking highest-engagement ones, with text and URL."""
    if df.empty:
        return []
    # Sort by TotalEngagement or Comments descending to get most impactful post
    for col in ("TotalEngagement", "Comments", "Reactions"):
        if col in df.columns:
            df = df.sort_values(col, ascending=False)
            break
    posts = []
    for _, row in df.head(n).iterrows():
        text = str(row.get("Title") or row.get("Content") or "").strip()
        posts.append({
            "text": text[:300],
            "url":  str(row.get("UrlTopic", "") or ""),
        })
    return posts
