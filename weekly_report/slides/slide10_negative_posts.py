"""
Slide 10 – Top negative posts (topic-type rows with Sentiment=Negative)
Input:  week1_df, brand, week1_display
Output: {title, subtitle, table_rows: [{stt, content, published_date, channel,
                                         site_name, negative_comments, url}]}
"""
from typing import Any, Dict, List
import pandas as pd

from core.data_loader import calculate_engagement
from weekly_report.slides.base import SlideGenerator


class Slide10NegativePosts(SlideGenerator):
    """Top negative posts ranked by negative comments count."""

    def __init__(self, topic_types: List[str], comment_types: List[str], top_n: int = 10):
        self.topic_types   = topic_types
        self.comment_types = comment_types
        self.top_n = top_n

    def generate(self, *, week1_df: pd.DataFrame, brand: str,
                 week1_display: str) -> Dict[str, Any]:

        # Lấy các bài đăng (topic) có sentiment tiêu cực
        df_topics = week1_df[
            (week1_df["Sentiment"].str.strip().str.lower() == "negative") &
            (week1_df["Type"].isin(self.topic_types))
        ].copy()

        if df_topics.empty:
            return {
                "title":      f"Top các bài đăng tiêu cực về {brand.upper()}",
                "subtitle":   f"Top 10 bài đăng nhận được phản hồi tiêu cực từ cộng đồng",
                "table_rows": [],
            }

        # Calculate engagement for all topics
        df_topics["_engagement"] = calculate_engagement(df_topics)

        # Đếm số lượng comments tiêu cực cho mỗi bài đăng
        topic_data = []
        for _, topic_row in df_topics.iterrows():
            topic_id = topic_row.get("Id")
            
            # Đếm comments tiêu cực cho topic này
            negative_comments_count = 0
            if topic_id and pd.notna(topic_id):
                # Chuyển topic_id về string để so sánh (vì ParentId có thể là string)
                topic_id_str = str(topic_id).strip()
                
                # Filter comments thuộc topic này và có sentiment negative
                # Lọc theo ParentId khớp với Id của topic
                negative_comments = week1_df[
                    (week1_df["ParentId"].notna()) &
                    (week1_df["ParentId"].astype(str).str.strip() == topic_id_str) &
                    (week1_df["Type"].isin(self.comment_types)) &
                    (week1_df["Sentiment"].notna()) &
                    (week1_df["Sentiment"].str.strip().str.lower() == "negative")
                ]
                negative_comments_count = len(negative_comments)
                
                # Debug: In ra thông tin để kiểm tra
                if negative_comments_count > 0:
                    print(f"DEBUG - Topic ID: {topic_id_str}, Negative comments: {negative_comments_count}")
            
            topic_data.append({
                "topic_row": topic_row,
                "negative_comments_count": negative_comments_count,
                "engagement": topic_row["_engagement"]
            })
        
        # Sort theo số lượng bình luận tiêu cực (cao đến thấp), 
        # nếu bằng nhau thì sort theo engagement
        topic_data_sorted = sorted(
            topic_data, 
            key=lambda x: (-x["negative_comments_count"], -x["engagement"])
        )
        
        # Debug: In ra top 10 để kiểm tra
        print(f"\nDEBUG - Top 10 negative posts:")
        for i, item in enumerate(topic_data_sorted[:10], 1):
            print(f"  {i}. Negative comments: {item['negative_comments_count']}, Engagement: {item['engagement']:.2f}")
        
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
                "negative_comments": item["negative_comments_count"],
                "url":               str(topic_row.get("UrlTopic", "")),
            })

        return {
            "title":      f"TOP CÁC BÀI ĐĂNG TIÊU CỰC VỀ {brand.upper()}",
            "subtitle":   f"Top 10 bài đăng nhận được phản hồi tiêu cực từ cộng đồng",
            "table_rows": table_rows,
        }
