"""
WeeklyReportOrchestrator – coordinates data loading, filtering, and parallel slide generation.
Single Responsibility: orchestrate; each slide class owns its own logic.
Open/Closed: add new slides by registering them, not modifying this class.

Public API:
    generate_report()              → build tất cả 12 slides
    generate_slides(keys, report)  → build một tập con slides, merge vào report có sẵn (nếu truyền vào)
"""
from __future__ import annotations

import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from typing import Any, Callable, Dict, List, Optional, Set

from core.config import (
    FILE_PATH, BRAND_NAME, TEXT_COLUMNS, METRIC_COLUMNS,
    TOPIC_TYPES, COMMENT_TYPES,
    LLM_MODEL, LLM_TEMPERATURE, LLM_SYSTEM_PROMPT,
)
from core.data_loader import DataLoader
from core.llm_client import LLMClient
from weekly_report.slides import (
    Slide01Overview, Slide02Trendline, Slide03Channels,
    Slide04TopSources, Slide05TopPosts, Slide06Sentiment,
    Slide07PositiveTopics, Slide08PositivePosts,
    Slide09NegativeTopics, Slide10NegativePosts,
    Slide11BrandComparison, Slide12BrandRanking,
    Slide13BrandTrendline, Slide14ChannelDistribution,
    Slide15TopicSentiment,
    Slide16TopCommentedPosts,
)

# Slides that call LLM (run in parallel); rest are data-only (run sequentially)
_LLM_SLIDES: Set[str] = {"slide_1", "slide_2", "slide_3", "slide_6", "slide_7", "slide_9", "slide_11", "slide_14", "slide_15"}
ALL_SLIDES: List[str] = [f"slide_{i}" for i in range(1, 17)]


class WeeklyReportOrchestrator:
    """
    Orchestrates the full 12-slide weekly report generation.

    Args:
        api_key:            LLM API key
        base_url:           LLM base URL
        file_path:          Path to Excel data file
        brand_name:         Primary brand (must match 'Topic' column)
        week1_end … week4_end: End datetime strings (YYYY-MM-DD HH:MM:SS) for each week window
        show_interactions:  Include interaction KPIs in slide 1 / 4 / 5
        competitor_brands:  Brands to include in slides 11 & 12 (None = all topics)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        file_path: str = None,
        brand_name: str = None,
        week1_end: str = None,
        week2_end: str = None,
        week3_end: str = None,
        week4_end: str = None,
        show_interactions: bool = True,
        competitor_brands: Optional[List[str]] = None,
        has_logo: bool = False,
    ):
        self.file_path        = file_path or FILE_PATH
        self.brand_name       = brand_name or BRAND_NAME
        self.week1_end        = week1_end
        self.week2_end        = week2_end
        self.week3_end        = week3_end
        self.week4_end        = week4_end
        self.show_interactions = show_interactions
        self.has_logo          = has_logo

        if competitor_brands:
            self.slide11_brands = [brand_name] + [b for b in competitor_brands if b != brand_name]
        else:
            self.slide11_brands = None

        self._data_loader = DataLoader(self.file_path, TEXT_COLUMNS, METRIC_COLUMNS)
        self._llm         = LLMClient(
            api_key=api_key, base_url=base_url,
            model=LLM_MODEL, temperature=LLM_TEMPERATURE,
            system_prompt=LLM_SYSTEM_PROMPT,
        )
        self._init_slides()
        self._ctx: Optional[Dict[str, Any]] = None  # cached after first _prepare_context()

    # ── slide wiring (OCP: extend here, not in generate_report) ──────────────
    def _init_slides(self):
        llm, tt, ct = self._llm, TOPIC_TYPES, COMMENT_TYPES
        self._s01 = Slide01Overview(llm, tt)
        self._s02 = Slide02Trendline(llm, tt)
        self._s03 = Slide03Channels(llm, tt)
        self._s04 = Slide04TopSources(tt, top_n=10)
        self._s05 = Slide05TopPosts(tt, top_n=10)
        self._s06 = Slide06Sentiment(llm, tt)
        self._s07 = Slide07PositiveTopics(llm, tt)
        self._s08 = Slide08PositivePosts(tt, ct, top_n=10)
        self._s09 = Slide09NegativeTopics(llm, tt)
        self._s10 = Slide10NegativePosts(tt, ct, top_n=10)
        self._s11 = Slide11BrandComparison(llm, tt)
        self._s12 = Slide12BrandRanking()
        self._s13 = Slide13BrandTrendline(tt)
        self._s14 = Slide14ChannelDistribution(llm, tt)
        self._s15 = Slide15TopicSentiment(llm, tt)
        self._s16 = Slide16TopCommentedPosts()

    # ── data preparation (cached after first call) ────────────────────────────
    def _prepare_context(self) -> Dict[str, Any]:
        """Load, filter, and slice data into weekly windows. Result is cached."""
        if self._ctx is not None:
            return self._ctx

        df_all = self._data_loader.preprocess()
        if "Topic" not in df_all.columns:
            raise ValueError("Column 'Topic' not found in data.")

        df = df_all[df_all["Topic"] == self.brand_name].copy()
        if df.empty:
            raise ValueError(f"No data found for brand '{self.brand_name}'.")
        self._data_loader.df = df

        w1e = pd.to_datetime(self.week1_end)
        w2e = pd.to_datetime(self.week2_end)
        w3e = pd.to_datetime(self.week3_end)
        w4e = pd.to_datetime(self.week4_end)
        # Fix: Use days=6 for 7-day inclusive range
        # Example: If w1e = 2026-04-06 23:59, then w1s = 2026-03-31 00:00 (7 days total)
        w1s = w1e - timedelta(days=6, hours=w1e.hour, minutes=w1e.minute, seconds=w1e.second)
        w1s = w1s.replace(hour=0, minute=0, second=0, microsecond=0)

        def _slice(src, end_dt):
            # Fix: Use proper 7-day inclusive range
            start_dt = end_dt - timedelta(days=6, hours=end_dt.hour, minutes=end_dt.minute, seconds=end_dt.second)
            start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            return src[(src["PublishedDate"] >= start_dt) &
                       (src["PublishedDate"] <= end_dt)].copy()

        week1_df = self._data_loader.filter_by_datetime_range(self.week1_end, days=7)
        week2_df = self._data_loader.filter_by_datetime_range(self.week2_end, days=7)
        week3_df = self._data_loader.filter_by_datetime_range(self.week3_end, days=7)
        week4_df = self._data_loader.filter_by_datetime_range(self.week4_end, days=7)

        if week1_df.empty:
            raise ValueError("No data for current week window.")
        
        # Calculate proper week start dates (7 days inclusive)
        def _week_start(end_dt):
            start = end_dt - timedelta(days=6, hours=end_dt.hour, minutes=end_dt.minute, seconds=end_dt.second)
            return start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        w2s = _week_start(w2e)
        w3s = _week_start(w3e)
        w4s = _week_start(w4e)

        self._ctx = dict(
            brand         = self.brand_name,
            si            = self.show_interactions,
            bf            = self.slide11_brands,
            w1e           = w1e,
            w1s           = w1s,
            week1_df      = week1_df,
            week2_df      = week2_df,
            week3_df      = week3_df,
            week4_df      = week4_df,
            week1_all     = _slice(df_all, w1e),
            week2_all     = _slice(df_all, w2e),
            week1_display = f"{w1s.strftime('%d/%m/%Y')} → {w1e.strftime('%d/%m/%Y')}",
            week2_display = f"{w2s.strftime('%d/%m/%Y')} → {w2e.strftime('%d/%m/%Y')}",
            week3_display = f"{w3s.strftime('%d/%m/%Y')} → {w3e.strftime('%d/%m/%Y')}",
            week4_display = f"{w4s.strftime('%d/%m/%Y')} → {w4e.strftime('%d/%m/%Y')}",
        )
        return self._ctx

    # ── slide registry: key → callable(ctx) ──────────────────────────────────
    def _build_registry(self, ctx: Dict[str, Any]) -> Dict[str, Callable[[], Dict]]:
        """
        Maps each slide key to a zero-argument callable.
        To add a new slide: add an entry here + wire the generator in _init_slides().
        """
        b   = ctx["brand"];  si = ctx["si"];  bf = ctx["bf"]
        w1  = ctx["week1_df"]; w2 = ctx["week2_df"]
        w3  = ctx["week3_df"]; w4 = ctx["week4_df"]
        wa1 = ctx["week1_all"]; wa2 = ctx["week2_all"]
        wd  = ctx["week1_display"]
        w1s = ctx["w1s"]; w1e = ctx["w1e"]

        return {
            "slide_1":  lambda: self._s01.generate(
                week1_df=w1, week2_df=w2, week3_df=w3, week4_df=w4,
                brand=b, week1_display=wd, show_interactions=si),
            "slide_2":  lambda: self._s02.generate(
                week1_df=w1, brand=b, week1_display=wd,
                week1_start_date=w1s.strftime("%Y-%m-%d"),
                week1_end_date=w1e.strftime("%Y-%m-%d")),
            "slide_3":  lambda: self._s03.generate(
                week1_df=w1, brand=b, week1_display=wd),
            "slide_4":  lambda: self._s04.generate(
                week1_df=w1, brand=b, week1_display=wd, show_interactions=si),
            "slide_5":  lambda: self._s05.generate(
                week1_df=w1, brand=b, week1_display=wd, show_interactions=si),
            "slide_6":  lambda: self._s06.generate(
                week1_df=w1, week2_df=w2, brand=b, week1_display=wd),
            "slide_7":  lambda: self._s07.generate(
                week1_df=w1, brand=b, week1_display=wd),
            "slide_8":  lambda: self._s08.generate(
                week1_df=w1, brand=b, week1_display=wd),
            "slide_9":  lambda: self._s09.generate(
                week1_df=w1, brand=b, week1_display=wd),
            "slide_10": lambda: self._s10.generate(
                week1_df=w1, brand=b, week1_display=wd),
            "slide_11": lambda: self._s11.generate(
                week1_df=wa1, week2_df=wa2, brand=b,
                week1_display=wd, brands_filter=bf),
            "slide_12": lambda: self._s12.generate(
                week1_df=wa1, week2_df=wa2, brand=b,
                week1_display=wd, brands_filter=bf),
            "slide_13": lambda: self._s13.generate(
                week1_df=wa1, brand=b, week1_display=wd,
                week1_start_date=w1s.strftime("%Y-%m-%d"),
                week1_end_date=w1e.strftime("%Y-%m-%d"),
                brands_filter=bf),
            "slide_14": lambda: self._s14.generate(
                week1_df=wa1, brand=b, week1_display=wd,
                brands_filter=bf),
            "slide_15": lambda: self._s15.generate(
                week1_df=wa1, week2_df=wa2, brand=b, week1_display=wd,
                brands_filter=bf),
            "slide_16": lambda: self._s16.generate(
                week1_df=wa1, brand=b, week1_display=wd,
                brands_filter=bf),
        }

    # ── public: build a subset of slides ─────────────────────────────────────
    def generate_slides(
        self,
        keys: List[str],
        existing_report: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build only the requested slides and return (or merge into) a report dict.

        Args:
            keys:            Slide keys to build, e.g. ["slide_1", "slide_6"].
                             Use the module-level ALL_SLIDES to build everything.
            existing_report: Optional report from a previous call.
                             New results overwrite matching keys; other keys are kept.

        Returns:
            Report dict: {report_metadata, slide_1, ..., slide_N}

        Examples:
            # Build two slides from scratch
            report = orch.generate_slides(["slide_1", "slide_2"])

            # Regenerate only slide_6 and patch into existing report
            report = orch.generate_slides(["slide_6"], existing_report=report)

            # Build everything
            report = orch.generate_slides(ALL_SLIDES)
        """
        invalid = set(keys) - set(ALL_SLIDES)
        if invalid:
            raise ValueError(f"Unknown slide keys: {invalid}. Valid keys: {ALL_SLIDES}")

        print(f"\n📊 Building slides: {keys}")
        ctx      = self._prepare_context()
        registry = self._build_registry(ctx)

        llm_keys  = [k for k in keys if k in _LLM_SLIDES]
        data_keys = [k for k in keys if k not in _LLM_SLIDES]
        results: Dict[str, Any] = {}

        # LLM slides → parallel
        if llm_keys:
            print(f"   🔀 Parallel (LLM): {llm_keys}")
            with ThreadPoolExecutor(max_workers=len(llm_keys)) as pool:
                futures = {pool.submit(registry[k]): k for k in llm_keys}
                for future in as_completed(futures):
                    k = futures[future]
                    try:
                        results[k] = future.result()
                        print(f"   ✅ {k}")
                    except Exception as exc:
                        print(f"   ❌ {k} failed: {exc}")
                        raise

        # Data-only slides → sequential (fast, no threads needed)
        if data_keys:
            print(f"   ⚡ Sequential (data): {data_keys}")
            for k in data_keys:
                results[k] = registry[k]()
                print(f"   ✅ {k}")

        metadata = {
            "brand":           ctx["brand"],
            "report_type":     "weekly",
            "week1_period":    ctx["week1_display"],
            "week2_period":    ctx["week2_display"],
            "week3_period":    ctx["week3_display"],
            "week4_period":    ctx["week4_display"],
            "generated_at":    pd.Timestamp.now().isoformat(),
            "generation_mode": "partial" if len(keys) < 16 else "parallel",
            "has_logo":        self.has_logo,
        }

        if existing_report:
            return {**existing_report, "report_metadata": metadata, **results}

        return {"report_metadata": metadata, **results}

    # ── public: build all 12 slides ───────────────────────────────────────────
    def generate_report(self) -> Dict[str, Any]:
        """Build the complete 16-slide report. Convenience wrapper over generate_slides."""
        print("\n" + "="*60)
        print("📊 STARTING WEEKLY REPORT GENERATION (PARALLEL MODE)")
        print("="*60)
        ctx = self._prepare_context()
        print(f"      W1: {ctx['week1_display']} ({len(ctx['week1_df'])} rows)")
        print(f"      W2: {ctx['week2_display']} ({len(ctx['week2_df'])} rows)")
        print(f"      W3: {ctx['week3_display']} ({len(ctx['week3_df'])} rows)")
        print(f"      W4: {ctx['week4_display']} ({len(ctx['week4_df'])} rows)")
        report = self.generate_slides(ALL_SLIDES)
        print("\n" + "="*60)
        print("✅ WEEKLY REPORT GENERATION COMPLETED!")
        print("="*60)
        return report
