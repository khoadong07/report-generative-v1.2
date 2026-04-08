"""
Configuration file for report generation
"""

import os
from pathlib import Path

# =====================
# DATA CONFIG
# =====================
# Get the directory where this config file is located
CONFIG_DIR = Path(__file__).parent.parent

# Default to file in test directory if exists, otherwise use the original path
DEFAULT_FILE = CONFIG_DIR / "Nestle_Gerber_15h_labeled.xlsx"
FILE_PATH = str(DEFAULT_FILE) if DEFAULT_FILE.exists() else "/content/Nestle_Gerber_15h_labeled.xlsx"

# =====================
# DATE CONFIG
# =====================
REPORT_DATE = "2026-02-01"
COMPARE_DATE = "2026-01-31"
LOOKBACK_DAYS = 6  # For trendline analysis

# =====================
# BRAND CONFIG
# =====================
BRAND_NAME = "Nestlé"

# =====================
# ANALYSIS CONFIG
# =====================
TOP_N_TOPICS = 6  # Number of top topics to analyze
TOP_N_ATTRIBUTES = 6  # Number of top attributes to analyze
TOP_N_PEAK_TOPICS = 3  # Number of topics to analyze for peak day

# =====================
# TOPIC TYPES
# =====================
TOPIC_TYPES = [
    "fbPageTopic",
    "fbGroupTopic", 
    "fbUserTopic",
    "forumTopic",
    "youtubeTopic",
    "tiktokTopic",
    "linkedinTopic",
    "ecommerceTopic",
    "threadsTopic",
    "snsTopic"
]

COMMENT_TYPES = [
    "fbPageComment",
    "fbGroupComment",
    "fbUserComment",
    "forumComment",
    "newsComment",
    "youtubeComment",
    "tiktokComment",
    "snsComment",
    "linkedinComment",
    "ecommerceComment",
    "threadsComment"
]

# =====================
# LLM CONFIG
# =====================
LLM_MODEL = "google/gemma-3-27b-it"
LLM_TEMPERATURE = 0.2
LLM_SYSTEM_PROMPT = "Bạn là chuyên gia crisis & executive insight."

# =====================
# DATA COLUMNS
# =====================
TEXT_COLUMNS = ["Title", "Content", "Description"]
METRIC_COLUMNS = ["Reactions", "Shares", "Comments", "Views", "Interactions"]
REQUIRED_COLUMNS = ["PublishedDate", "Type", "Sentiment", "Labels", "UrlTopic"]
