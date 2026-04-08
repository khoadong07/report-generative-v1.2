"""
Slide 14 – Phân bố đề cập trên các kênh truyền thông (multi-brand stacked bar)
Input:  week1_all_df, brand, week1_display, brands_filter
Output: {title, subtitle, insight_sections, stacked_bar_chart, channel_legend}

Channel groups (fixed colors):
  Fanpage  → fbPageComment, fbPageTopic
  Facebook → fbUserTopic, fbGroupTopic, fbGroupComment, fbUserComment
  Tiktok   → tiktokComment, tiktokTopic
  Youtube  → youtubeComment, youtubeTopic
  News     → newsTopic
  Others   → everything else
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd

from core.llm_client import LLMClient
from weekly_report.slides.base import SlideGenerator, InsightMixin
from weekly_report.prompts import get_slide13_channel_insight_prompt

# ── Fixed channel group definitions ──────────────────────────────────────────
CHANNEL_GROUPS: Dict[str, List[str]] = {
    "Fanpage":  ["fbPageComment", "fbPageTopic"],
    "Facebook": ["fbUserTopic", "fbGroupTopic", "fbGroupComment", "fbUserComment"],
    "Tiktok":   ["tiktokComment", "tiktokTopic"],
    "Youtube":  ["youtubeComment", "youtubeTopic"],
    "News":     ["newsTopic"],
}

CHANNEL_COLORS: Dict[str, str] = {
    "Fanpage":  "#1877F2",   # Facebook blue
    "Facebook": "#42B72A",   # Facebook green
    "Tiktok":   "#010101",   # TikTok black
    "Youtube":  "#FF0000",   # YouTube red
    "News":     "#F4A261",   # warm orange
    "Others":   "#ADB5BD",   # neutral grey
}

# Groups to analyse in insight (order matters for display)
INSIGHT_GROUPS = ["Facebook", "News", "Fanpage"]


def _assign_channel_group(type_val: str) -> str:
    """Map a raw Type value to its channel group name."""
    for group, types in CHANNEL_GROUPS.items():
        if type_val in types:
            return group
    return "Others"


class Slide14ChannelDistribution(SlideGenerator, InsightMixin):
    """Multi-brand stacked-bar channel distribution slide."""

    def __init__(self, llm_client: LLMClient, topic_types: List[str]):
        self.llm_client = llm_client
        self.topic_types = topic_types

    def generate(
        self,
        *,
        week1_df: pd.DataFrame,
        brand: str,
        week1_display: str,
        brands_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:

        all_brands = (
            [b for b in brands_filter if b in week1_df["Topic"].values]
            if brands_filter
            else sorted(week1_df["Topic"].dropna().unique().tolist())
        )

        # Assign channel group to every row
        df = week1_df.copy()
        df["_channel_group"] = df["Type"].fillna("").apply(_assign_channel_group)

        # ── Stacked bar chart data ────────────────────────────────────────────
        all_groups = list(CHANNEL_COLORS.keys())  # fixed order
        bar_data: List[Dict] = []

        for b in all_brands:
            df_b = df[df["Topic"] == b]
            total = len(df_b)
            group_counts = df_b["_channel_group"].value_counts().to_dict()

            segments: List[Dict] = []
            for g in all_groups:
                count = int(group_counts.get(g, 0))
                pct = round(count / total * 100, 1) if total > 0 else 0.0
                segments.append({
                    "group":   g,
                    "count":   count,
                    "percent": pct,
                    "color":   CHANNEL_COLORS[g],
                    "show_label": pct >= 20,   # hide label if < 20%
                })

            bar_data.append({
                "topic":    b,
                "total":    total,
                "segments": segments,
            })

        # Sort by total descending
        bar_data.sort(key=lambda x: x["total"], reverse=True)

        # ── Insight sections (3 groups: Facebook, News, Fanpage) ─────────────
        insight_sections = self._build_insight_sections(df, brand, week1_display, all_brands)

        # ── Legend (fixed, always all 6 groups) ──────────────────────────────
        legend = [{"group": g, "color": CHANNEL_COLORS[g]} for g in all_groups]

        return {
            "title":    "PHÂN BỔ ĐỀ CẬP TRÊN CÁC KÊNH TRUYỀN THÔNG",
            "subtitle": f"",
            "insight_sections": insight_sections,
            "stacked_bar_chart": {
                "title": f"Phân bổ đề cập của {brand.upper()} và đối thủ trên các kênh truyền thông",
                "data":  bar_data,
            },
            "channel_legend": legend,
        }

    # ── Insight builder ───────────────────────────────────────────────────────
    def _build_insight_sections(
        self,
        df: pd.DataFrame,
        brand: str,
        week1_display: str,
        all_brands: List[str],
    ) -> List[Dict]:
        """
        Build 3 insight sections: Facebook, News, Fanpage.
        Each section: top-3 topics by mention count, 2 sample posts per topic,
        LLM summary 15-20 words per topic (no URL citation).
        """
        sections = []
        for group_name in INSIGHT_GROUPS:
            group_types = CHANNEL_GROUPS.get(group_name, [])
            df_group = df[df["_channel_group"] == group_name].copy()

            if df_group.empty:
                sections.append({
                    "group":  group_name,
                    "color":  CHANNEL_COLORS[group_name],
                    "topics": [],
                    "summary": f"Không có dữ liệu từ kênh {group_name} trong giai đoạn này.",
                })
                continue

            # Top-3 topics (Labels1) by mention count across all brands
            topic_counts = (
                df_group["Labels1"]
                .fillna("Không xác định")
                .replace("", "Không xác định")
                .value_counts()
                .head(3)
            )

            topic_details: List[Dict] = []
            for topic_label, count in topic_counts.items():
                df_topic = df_group[
                    df_group["Labels1"].fillna("Không xác định").replace("", "Không xác định") == topic_label
                ]
                # 2 sample posts: prefer topic types, then any
                samples_df = df_topic[df_topic["Type"].isin(self.topic_types)].head(2)
                if len(samples_df) < 2:
                    samples_df = df_topic.head(2)

                samples = []
                for _, row in samples_df.iterrows():
                    raw = str(row.get("Title") or row.get("Content") or "").strip()
                    samples.append(raw[:300])  # cap raw text for LLM

                topic_details.append({
                    "label":   topic_label,
                    "count":   int(count),
                    "samples": samples,
                })

            # LLM summarise each topic
            summary_text = self._summarise_topics(
                group_name, topic_details, brand, week1_display
            )

            sections.append({
                "group":   group_name,
                "color":   CHANNEL_COLORS[group_name],
                "topics":  topic_details,
                "summary": summary_text,
            })

        return sections

    def _summarise_topics(
        self,
        group_name: str,
        topic_details: List[Dict],
        brand: str,
        week1_display: str,
    ) -> str:
        prompt = get_slide13_channel_insight_prompt(
            brand=brand,
            week_display=week1_display,
            group_name=group_name,
            topic_details=topic_details,
        )
        try:
            return self.llm_client.generate_insight(prompt)
        except Exception as e:
            print(f"Warning: LLM insight failed for {group_name}: {e}")
            lines = []
            for t in topic_details:
                lines.append(f"- {t['label']}: {t['count']} lượt đề cập")
            return "\n".join(lines)

    def _generate_insight(self, **kwargs) -> str:
        """Required by InsightMixin – delegated to _summarise_topics."""
        return self._summarise_topics(**kwargs)
