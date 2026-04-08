"""
Slide 01 – Weekly KPI Overview + 4-week comparison
Input:  week1_df … week4_df (pd.DataFrame), brand, week1_display, show_interactions
Output: {title, subtitle, current_week_metrics, weekly_comparison, insight, show_interactions}
"""
from typing import Any, Dict, List
import pandas as pd

from core.data_loader import calculate_percentage_change, calculate_engagement
from core.llm_client import LLMClient
from weekly_report.slides.base import SlideGenerator, InsightMixin
from weekly_report.prompts import get_weekly_overview_insight_prompt


class Slide01Overview(SlideGenerator, InsightMixin):
    """Generate weekly overview slide with KPIs and 4-week comparison."""

    def __init__(self, llm_client: LLMClient, topic_types: List[str]):
        self.llm_client = llm_client
        self.topic_types = topic_types

    # ── public ────────────────────────────────────────────────────────────────
    def generate(self, *, week1_df: pd.DataFrame, week2_df: pd.DataFrame,
                 week3_df: pd.DataFrame, week4_df: pd.DataFrame,
                 brand: str, week1_display: str,
                 show_interactions: bool = True) -> Dict[str, Any]:

        current_week_metrics = (
            self._metrics_with_interactions(week1_df, week2_df)
            if show_interactions
            else self._metrics_basic(week1_df, week2_df)
        )

        weekly_comparison = self._build_weekly_comparison(
            week1_df, week2_df, week3_df, week4_df, show_interactions,
            total_mentions=current_week_metrics[-1]["value"] if not show_interactions else len(week1_df)
        )

        insight = self._generate_insight(
            week1_df=week1_df, brand=brand,
            week1_display=week1_display, weekly_comparison=weekly_comparison
        )

        return {
            "title": f"TỔNG QUAN LƯỢNG ĐỀ CẬP CỦA {brand.upper()}",
            "subtitle": f"Tổng quan lược đề cập trong tuần",
            "current_week_metrics": current_week_metrics,
            "weekly_comparison": weekly_comparison,
            "insight": insight,
            "show_interactions": show_interactions,
        }

    # ── private helpers ───────────────────────────────────────────────────────
    def _metrics_with_interactions(self, w1: pd.DataFrame, w2: pd.DataFrame) -> List[Dict]:
        def _chg(a, b): return calculate_percentage_change(a, b)

        def _col(df, col): return int(df[col].sum()) if col in df.columns else 0

        total = len(w1);          prev_total = len(w2)
        
        # Always calculate engagement from Reactions + Shares + Comments
        eng_cols = [c for c in ["Reactions","Shares","Comments"] if c in w1.columns]
        eng   = int(w1[eng_cols].sum().sum()) if eng_cols else 0
        p_eng = int(w2[eng_cols].sum().sum()) if eng_cols else 0
        views  = _col(w1, "Views");     p_views = _col(w2, "Views")
        react  = _col(w1, "Reactions"); p_react = _col(w2, "Reactions")
        shr    = _col(w1, "Shares");    p_shr   = _col(w2, "Shares")
        cmt    = _col(w1, "Comments");  p_cmt   = _col(w2, "Comments")
        
        # Build full metrics list
        metrics = [
            {"label": "Tổng đề cập",    "value": total, "change_percent": _chg(total, prev_total)},
            {"label": "Tổng tương tác", "value": eng,   "change_percent": _chg(eng,   p_eng)},
        ]
        
        # Add Views if available
        if "Views" in w1.columns:
            metrics.append({"label": "Tổng lượt xem", "value": views, "change_percent": _chg(views, p_views)})
        
        # Add breakdown metrics (Reactions, Shares, Comments)
        if "Reactions" in w1.columns:
            metrics.append({"label": "Lượt reactions", "value": react, "change_percent": _chg(react, p_react)})
        if "Shares" in w1.columns:
            metrics.append({"label": "Lượt chia sẻ", "value": shr, "change_percent": _chg(shr, p_shr)})
        if "Comments" in w1.columns:
            metrics.append({"label": "Lượt bình luận", "value": cmt, "change_percent": _chg(cmt, p_cmt)})
        
        return metrics

    def _metrics_basic(self, w1: pd.DataFrame, w2: pd.DataFrame) -> List[Dict]:
        def _cnt(df, suffix): return len(df[df["Type"].str.endswith(suffix, na=False)])
        def _chg(a, b): return calculate_percentage_change(a, b)

        posts1 = _cnt(w1, "Topic"); posts2 = _cnt(w2, "Topic")
        cmts1  = _cnt(w1, "Comment"); cmts2 = _cnt(w2, "Comment")
        total1 = posts1 + cmts1;    total2 = posts2 + cmts2

        return [
            {"label": "Tổng bài đăng",  "value": posts1, "change_percent": _chg(posts1, posts2)},
            {"label": "Tổng bình luận", "value": cmts1,  "change_percent": _chg(cmts1,  cmts2)},
            {"label": "Tổng thảo luận", "value": total1, "change_percent": _chg(total1, total2)},
        ]

    def _build_weekly_comparison(self, w1, w2, w3, w4,
                                  show_interactions: bool,
                                  total_mentions: int) -> List[Dict]:
        def _count(df):
            if show_interactions:
                return len(df)
            posts = len(df[df["Type"].str.endswith("Topic",   na=False)])
            cmts  = len(df[df["Type"].str.endswith("Comment", na=False)])
            return posts + cmts

        m4 = _count(w4); m3 = _count(w3); m2 = _count(w2)
        m1 = total_mentions if not show_interactions else len(w1)

        return [
            {"week": "3 tuần trước",  "total_mentions": m4, "growth_rate": None},
            {"week": "2 tuần trước",  "total_mentions": m3, "growth_rate": calculate_percentage_change(m3, m4)},
            {"week": "Tuần trước",    "total_mentions": m2, "growth_rate": calculate_percentage_change(m2, m3)},
            {"week": "Tuần hiện tại", "total_mentions": m1, "growth_rate": calculate_percentage_change(m1, m2)},
        ]

    def _generate_insight(self, *, week1_df: pd.DataFrame, brand: str,
                          week1_display: str, weekly_comparison: List[Dict]) -> str:
        print("         → Extracting top topics for insight...")
        df_topics = week1_df[week1_df["Type"].isin(self.topic_types)].copy()
        if df_topics.empty:
            return (f"Trong giai đoạn {week1_display}, {brand.upper()} có {len(week1_df)} lượt đề cập. "
                    "Không có dữ liệu bài đăng chính (topics) để phân tích chi tiết.")

        df_topics["engagement"] = calculate_engagement(df_topics)
        df_top = df_topics.sort_values("engagement", ascending=False).head(5)
        context_text = "\n\n---\n\n".join([
            f"Tiêu đề: {r['Title']}\nMô tả: {r['Description']}\nNội dung: {r['Content']}\nURL: {r['UrlTopic']}"
            for _, r in df_top.iterrows()
        ])
        prompt = get_weekly_overview_insight_prompt(brand, week1_display, weekly_comparison, context_text)
        return self.llm_client.generate_insight(prompt)
