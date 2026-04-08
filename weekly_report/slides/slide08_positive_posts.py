"""
Slide 08 – Top positive posts (topic-type rows with Sentiment=Positive)
Input:  week1_df, brand, week1_display
Output: {title, subtitle, table_rows: [{stt, content, published_date, channel,
                                         site_name, positive_comments, url}]}
"""
from typing import Any, Dict, List
import pandas as pd

from core.data_loader import calculate_engagement
from weekly_report.slides.base import SlideGenerator


class Slide08PositivePosts(SlideGenerator):
    """Top positive posts ranked by engagement."""

    def __init__(self, topic_types: List[str], comment_types: List[str], top_n: int = 10):
        self.topic_types   = topic_types
        self.comment_types = comment_types
        self.top_n = top_n

    def generate(self, *, week1_df: pd.DataFrame, brand: str,
                 week1_display: str) -> Dict[str, Any]:

        # Lấy các bài đăng (topic) có sentiment tích cực
        df_topics = week1_df[
            (week1_df["Sentiment"].str.strip().str.lower() == "positive") &
            (week1_df["Type"].isin(self.topic_types))
        ].copy()

        if df_topics.empty:
            return {
                "title":      f"TOP CÁC BÀI ĐĂNG TÍCH CỰC VỀ {brand.upper()}",
                "subtitle":   f"Top 10 bài đăng nhận được phản hồi tích cực từ cộng đồng",
                "table_rows": [],
            }

        # Calculate engagement for all topics
        df_topics["_engagement"] = calculate_engagement(df_topics)

        # Đếm số lượng comments tích cực cho mỗi bài đăng
        topic_data = []
        for _, topic_row in df_topics.iterrows():
            topic_id = topic_row.get("Id")
            
            # Đếm comments tích cực cho topic này
            positive_comments_count = 0
            if topic_id and pd.notna(topic_id):
                # Filter comments thuộc topic này và có sentiment positive
                positive_comments = week1_df[
                    (week1_df["ParentId"] == topic_id) &
                    (week1_df["Type"].isin(self.comment_types)) &
                    (week1_df["Sentiment"].str.strip().str.lower() == "positive")
                ]
                positive_comments_count = len(positive_comments)
            
            topic_data.append({
                "topic_row": topic_row,
                "positive_comments_count": positive_comments_count,
                "engagement": topic_row["_engagement"]
            })
        
        # Sort theo số lượng bình luận tích cực (cao đến thấp), 
        # nếu bằng nhau thì sort theo engagement
        topic_data_sorted = sorted(
            topic_data, 
            key=lambda x: (x["positive_comments_count"], x["engagement"]), 
            reverse=True
        )
        
        # Lấy top N
        top_topics = topic_data_sorted[:self.top_n]
        
        # Build table rows
        table_rows = []
        for i, item in enumerate(top_topics, 1):
            topic_row = item["topic_row"]
            
            # Ưu tiên: Content -> Title -> Description
            content_text = (
                topic_row.get("Content") or 
                topic_row.get("Title") or 
                topic_row.get("Description") or 
                ""
            )
            
            table_rows.append({
                "stt":               i,
                "content":           str(content_text).strip(),
                "published_date":    str(topic_row.get("PublishedDate", "")),
                "channel":           str(topic_row.get("Channel", "")),
                "site_name":         str(topic_row.get("SiteName", "")),
                "positive_comments": item["positive_comments_count"],
                "url":               str(topic_row.get("UrlTopic", "")),
            })

        return {
            "title":      f"Top các bài đăng tích cực về {brand.upper()}",
            "subtitle":   f"Top 10 bài đăng nhận được phản hồi tích cực từ cộng đồng",
            "table_rows": table_rows,
        }
