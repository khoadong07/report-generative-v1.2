"""
Prompt templates for Weekly LLM-based insight generation
"""


def get_weekly_overview_insight_prompt(brand: str, week_display: str,
                                        weekly_comparison: list, context_text: str) -> str:
    """Generate prompt for weekly overview insight (Slide 1)"""
    comparison_text = "\n".join([f"- {w['week']}: {w['total_mentions']} lượt" for w in weekly_comparison])
    
    return f"""
Bạn là chuyên gia phân tích truyền thông và social listening.

BỐI CẢNH PHÂN TÍCH:
- Thương hiệu: {brand.upper()}
- Tuần khảo sát: {week_display}
- So sánh 4 tuần:
{comparison_text}

NHIỆM VỤ:
Viết một đoạn insight tóm tắt tình hình thảo luận trong tuần.

YÊU CẦU BẮT BUỘC:
- Viết đúng 5–6 câu, dạng văn xuôi
- Tổng số từ KHÔNG VƯỢT QUÁ 250 từ
- Câu đầu tiên mô tả quy mô & xu hướng so với các tuần trước
- Các câu sau mô tả các chủ đề chính và phản ứng cộng đồng
- Văn phong chuyên nghiệp, trung lập
- CRITICAL: Mỗi câu PHẢI kết thúc bằng [Nguồn: URL] với URL clickable
- Mỗi câu gắn DUY NHẤT 1 URL
- KHÔNG lặp URL
- KHÔNG gạch đầu dòng, KHÔNG tiêu đề
- URL PHẢI là hyperlink có thể click được

FORMAT BẮT BUỘC:
Câu 1 nội dung phân tích... [Nguồn: https://example.com/url1]
Câu 2 nội dung phân tích... [Nguồn: https://example.com/url2]
Câu 3 nội dung phân tích... [Nguồn: https://example.com/url3]

DỮ LIỆU (chứa URL trong trường UrlTopic):
{context_text}

LƯU Ý: Bạn PHẢI sử dụng URL từ dữ liệu được cung cấp. KHÔNG bỏ qua URL.
"""


def get_weekly_trendline_insight_prompt(brand: str, week_display: str,
                                         trendline_data: list, context_text: str) -> str:
    """Generate prompt for weekly trendline insight (Slide 2)"""
    return f"""
Bạn là chuyên gia phân tích xu hướng truyền thông.

BỐI CẢNH:
- Thương hiệu: {brand.upper()}
- Tuần phân tích: {week_display}

NHIỆM VỤ:
Phân tích xu hướng đề cập trong tuần, chỉ ra ngày có lượng thảo luận cao nhất và lý do.

YÊU CẦU BẮT BUỘC:
- 4–5 câu, văn xuôi
- CRITICAL: Mỗi câu PHẢI kết thúc bằng [Nguồn: URL] với URL clickable
- Mỗi URL chỉ dùng 1 lần
- Không gạch đầu dòng
- URL PHẢI là hyperlink có thể click được

FORMAT BẮT BUỘC:
Câu 1... [Nguồn: https://example.com/url1]
Câu 2... [Nguồn: https://example.com/url2]

DỮ LIỆU (chứa URL trong trường UrlTopic):
{context_text}

LƯU Ý: Bạn PHẢI sử dụng URL từ dữ liệu được cung cấp. KHÔNG bỏ qua URL.
"""


def get_weekly_channel_insight_prompt(brand: str, week_display: str,
                                       channel_data: str, top_sources: str,
                                       context_text: str) -> str:
    """Generate prompt for weekly channel insight (Slide 3)"""
    return f"""
Bạn là chuyên gia social listening & channel analysis.

BỐI CẢNH:
- Thương hiệu: {brand.upper()}
- Tuần phân tích: {week_display}

PHÂN BỔ THEO KÊNH:
{channel_data}

TOP NGUỒN:
{top_sources}

NHIỆM VỤ:
Viết insight phân tích sự phân bổ thảo luận theo kênh và nguồn nổi bật.

YÊU CẦU BẮT BUỘC:
- Viết 4–5 câu, văn xuôi
- Chỉ ra kênh chính và nguồn nổi bật
- CRITICAL: Mỗi câu PHẢI kết thúc bằng [Nguồn: URL] với URL clickable
- Mỗi URL chỉ dùng 1 lần
- Không gạch đầu dòng
- URL PHẢI là hyperlink có thể click được

FORMAT BẮT BUỘC:
Câu 1... [Nguồn: https://example.com/url1]
Câu 2... [Nguồn: https://example.com/url2]

DỮ LIỆU (chứa URL trong trường UrlTopic):
{context_text}

LƯU Ý: Bạn PHẢI sử dụng URL từ dữ liệu được cung cấp. KHÔNG bỏ qua URL.
"""


def get_weekly_sentiment_insight_prompt(brand: str, week_display: str,
                                          top_topics: list, context_text: str) -> str:
    """Generate prompt for weekly sentiment insight (Slide 6)"""
    topics_text = "\n".join([
        f"- {t['topic']}: {t['total']} lượt (Negative: {t['negative']}, Neutral: {t['neutral']}, Positive: {t['positive']})"
        for t in top_topics[:5]
    ])
    
    return f"""
Bạn là chuyên gia social listening & sentiment analysis.

BỐI CẢNH:
- Thương hiệu: {brand.upper()}
- Tuần phân tích: {week_display}

TOP CHỦ ĐỀ THEO SENTIMENT:
{topics_text}

NHIỆM VỤ:
Viết insight phân tích sắc thái và các chủ đề nổi bật.

YÊU CẦU BẮT BUỘC:
- Viết 5–6 câu, văn xuôi
- GIỚI HẠN TỐI ĐA: 180 từ
- Phân tích tỷ lệ sentiment và các chủ đề chính
- CRITICAL: Mỗi câu PHẢI kết thúc bằng [Nguồn: URL] với URL clickable
- Mỗi URL chỉ dùng 1 lần
- Không gạch đầu dòng
- URL PHẢI là hyperlink có thể click được

FORMAT BẮT BUỘC:
Câu 1... [Nguồn: https://example.com/url1]
Câu 2... [Nguồn: https://example.com/url2]

DỮ LIỆU (chứa URL trong trường UrlTopic):
{context_text}

LƯU Ý: Bạn PHẢI sử dụng URL từ dữ liệu được cung cấp. KHÔNG bỏ qua URL.
QUAN TRỌNG: Tổng số từ KHÔNG được vượt quá 180 từ.
"""


def get_weekly_positive_insight_prompt(brand: str, week_display: str,
                                         positive_topics: str, context_text: str) -> str:
    """Generate prompt for weekly positive insight (Slide 7)"""
    return f"""
Bạn là chuyên gia phân tích truyền thông tích cực.

BỐI CẢNH:
- Thương hiệu: {brand.upper()}
- Tuần phân tích: {week_display}

CHỦ ĐỀ TÍCH CỰC:
{positive_topics}

NHIỆM VỤ:
Viết insight phân tích các chủ đề tích cực về thương hiệu.

YÊU CẦU BẮT BUỘC:
- Viết 4–5 câu, văn xuôi
- Nêu rõ các chủ đề tích cực chính và dẫn chứng cụ thể
- CRITICAL: Mỗi câu PHẢI kết thúc bằng [Nguồn: URL] với URL clickable
- Mỗi URL chỉ dùng 1 lần
- Không gạch đầu dòng
- URL PHẢI là hyperlink có thể click được

FORMAT BẮT BUỘC:
Câu 1... [Nguồn: https://example.com/url1]
Câu 2... [Nguồn: https://example.com/url2]

DỮ LIỆU (chứa URL trong trường UrlTopic):
{context_text}

LƯU Ý: Bạn PHẢI sử dụng URL từ dữ liệu được cung cấp. KHÔNG bỏ qua URL.
"""


def get_weekly_negative_insight_prompt(brand: str, week_display: str,
                                         negative_topics: str, context_text: str) -> str:
    """Generate prompt for weekly negative insight (Slide 10)"""
    return f"""
Bạn là chuyên gia phân tích khủng hoảng truyền thông.

BỐI CẢNH:
- Thương hiệu: {brand.upper()}
- Tuần phân tích: {week_display}

CHỦ ĐỀ TIÊU CỰC:
{negative_topics}

NHIỆM VỤ:
Viết insight phân tích các chủ đề tiêu cực về thương hiệu.

YÊU CẦU BẮT BUỘC:
- Viết 4–5 câu, văn xuôi
- Nêu rõ các chủ đề tiêu cực chính và dẫn chứng cụ thể
- CRITICAL: Mỗi câu PHẢI kết thúc bằng [Nguồn: URL] với URL clickable
- Mỗi URL chỉ dùng 1 lần
- Không gạch đầu dòng
- URL PHẢI là hyperlink có thể click được

FORMAT BẮT BUỘC:
Câu 1... [Nguồn: https://example.com/url1]
Câu 2... [Nguồn: https://example.com/url2]

DỮ LIỆU (chứa URL trong trường UrlTopic):
{context_text}

LƯU Ý: Bạn PHẢI sử dụng URL từ dữ liệu được cung cấp. KHÔNG bỏ qua URL.
"""


def get_weekly_brand_comparison_insight_prompt(brand: str, week_display: str,
                                                 brand_comparison_data: str, context_text: str) -> str:
    """Generate prompt for weekly brand comparison insight (Slide 11)"""
    return f"""
Bạn là chuyên gia phân tích cạnh tranh thương hiệu và social listening.

BỐI CẢNH:
- Thương hiệu chính: {brand.upper()}
- Tuần phân tích: {week_display}

DỮ LIỆU SO SÁNH THƯƠNG HIỆU (tuần trước → tuần này):
{brand_comparison_data}

CONTEXT MẪU BÁO CÁO (để tham khảo chủ đề nổi bật):
{context_text}

NHIỆM VỤ:
Viết 1 đoạn văn xuôi phân tích chi tiết so sánh các thương hiệu, bao gồm:
1. Thương hiệu dẫn đầu với số liệu cụ thể và % tăng trưởng
2. Thương hiệu có tăng trưởng ấn tượng với số liệu và % tăng trưởng
3. Các chủ đề/sự kiện nổi bật được đề cập (dựa vào context mẫu)
4. Thương hiệu có mức tăng thấp nhất với số liệu và % tăng trưởng

YÊU CẦU BẮT BUỘC:
- GIỚI HẠN: Tối đa 200 từ, viết chi tiết, rõ ràng
- Văn xuôi liền mạch, KHÔNG chia đoạn, KHÔNG có tiêu đề
- Chỉ dùng số liệu từ dữ liệu được cung cấp, KHÔNG bịa thêm
- CRITICAL: Mỗi câu PHẢI kết thúc bằng [Nguồn: URL] với URL lấy từ context mẫu
- Mỗi URL chỉ dùng 1 lần, KHÔNG lặp URL
- Phân tích tất cả các thương hiệu trong dữ liệu, không bỏ sót
- Nêu rõ số liệu cụ thể (số lượt đề cập) và % tăng/giảm cho mỗi thương hiệu

FORMAT BẮT BUỘC:
Câu 1 về thương hiệu dẫn đầu với số liệu... [Nguồn: https://...] Câu 2 về thương hiệu tăng trưởng ấn tượng với số liệu... [Nguồn: https://...] Câu 3 về chủ đề/sự kiện nổi bật... [Nguồn: https://...] Câu 4 về thương hiệu khác... [Nguồn: https://...] Câu 5 về thương hiệu tăng thấp nhất... [Nguồn: https://...]

DỮ LIỆU MẪU (Title, Type, UrlTopic theo từng thương hiệu):
{context_text}

LƯU Ý: Chỉ dùng URL từ dữ liệu được cung cấp. KHÔNG bịa URL.
"""


def get_slide13_channel_insight_prompt(
    brand: str,
    week_display: str,
    group_name: str,
    topic_details: list,
) -> str:
    """Generate prompt for slide 13 channel insight – no URL citation required."""
    topics_text = ""
    for t in topic_details:
        topics_text += f"\nTopic: {t['label']} ({t['count']} lượt đề cập)\n"
        for i, s in enumerate(t.get("samples", []), 1):
            topics_text += f"  Mẫu {i}: {s}\n"

    return f"""
Bạn là chuyên gia phân tích truyền thông và social listening.

BỐI CẢNH:
- Thương hiệu chính: {brand.upper()}
- Tuần phân tích: {week_display}
- Kênh phân tích: {group_name}

DỮ LIỆU TOP 3 CHỦ ĐỀ NỔI BẬT TRÊN KÊNH {group_name.upper()}:
{topics_text}

NHIỆM VỤ:
Viết 1 đoạn văn ngắn gọn (tối đa 60 từ) tóm tắt các chủ đề nổi bật trên kênh {group_name} trong tuần {week_display}.

YÊU CẦU BẮT BUỘC:
- Đoạn văn liền mạch, không gạch đầu dòng
- Đề cập đến cả 3 topic với số liệu cụ thể
- Văn phong trung lập, súc tích, mô tả sự vụ cụ thể
- KHÔNG trích dẫn link, KHÔNG ghi nguồn
- Độ dài: TỐI ĐA 60 từ

VÍ DỤ:
Trên kênh Facebook, chủ đề Khuyến mãi hè dẫn đầu với 1,234 lượt đề cập, tập trung vào các chương trình giảm giá thu hút người dùng trẻ. Sản phẩm mới đứng thứ hai với 856 lượt, nhận phản hồi tích cực về thiết kế và tính năng. Dịch vụ khách hàng có 645 lượt thảo luận, chủ yếu về thời gian xử lý đơn hàng.
"""


def get_slide15_topic_sentiment_insight_prompt(
    brand: str,
    week_display: str,
    all_topics: list,
    bar_data: list,
    summary_table: dict,
) -> str:
    """Generate prompt for slide 15 – topic sentiment breakdown insight."""

    # Build sentiment summary text
    sent_lines = []
    for item in bar_data:
        segs = {s["sentiment"]: s for s in item["segments"]}
        pos = segs.get("Positive", {}).get("percent", 0)
        neu = segs.get("Neutral",  {}).get("percent", 0)
        neg = segs.get("Negative", {}).get("percent", 0)
        nsr = summary_table["nsr_week1"].get(item["topic"], 0)
        sent_lines.append(
            f"- {item['topic']}: {item['total']} buzz | "
            f"Positive {pos}% / Neutral {neu}% / Negative {neg}% | NSR {nsr:.1f}%"
        )

    # Build sample posts text (positive + negative)
    label_lines = []
    sample_lines = []
    for topic in all_topics:
        pos_posts = summary_table["positive_posts"].get(topic, [])
        neg_posts = summary_table["negative_posts"].get(topic, [])
        pos_preview = (" | ".join(p["text"][:60] for p in pos_posts[:2])) or "—"
        neg_preview = (" | ".join(p["text"][:60] for p in neg_posts[:2])) or "—"
        label_lines.append(
            f"- {topic}: Tích cực [{pos_preview}] | Tiêu cực [{neg_preview}]"
        )
        if pos_posts or neg_posts:
            sample_lines.append(f"\n[{topic}]")
            for p in pos_posts[:2]:
                sample_lines.append(f"  [Positive] {p['text'][:150]}")
            for p in neg_posts[:2]:
                sample_lines.append(f"  [Negative] {p['text'][:150]}")

    return f"""
Bạn là chuyên gia phân tích truyền thông và social listening.

BỐI CẢNH:
- Thương hiệu chính: {brand.upper()}
- Tuần phân tích: {week_display}

TỶ TRỌNG SENTIMENT THEO TOPIC:
{chr(10).join(sent_lines)}

CHỦ ĐỀ NỔI BẬT THEO SENTIMENT:
{chr(10).join(label_lines)}

MẪU NỘI DUNG TIÊU BIỂU:
{chr(10).join(sample_lines)}

NHIỆM VỤ:
Viết 1 đoạn văn ngắn gọn (tối đa 140 từ) phân tích sắc thái đề cập theo từng topic, chỉ ra topic nào có NSR cao/thấp nhất, chủ đề tích cực/tiêu cực nổi bật và hàm ý cho thương hiệu.

YÊU CẦU BẮT BUỘC:
- Đoạn văn liền mạch, không gạch đầu dòng, không tiêu đề
- Dùng số liệu cụ thể từ dữ liệu trên
- Văn phong chuyên nghiệp, trung lập
- Độ dài: TỐI ĐA 140 từ
- KHÔNG trích dẫn URL
"""
