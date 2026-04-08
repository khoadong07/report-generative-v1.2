# Weekly Report Generator v1.2

Production-ready codebase for generating weekly HTML reports with brand analysis.

## Overview

This is a standalone version of the weekly report generator, extracted from the main codebase for production use. It generates comprehensive weekly reports with 16 slides covering various aspects of brand analysis.

## Features

- **16 Slides**: Complete weekly report with overview, sentiment analysis, trends, and competitive analysis
- **HTML Templates**: Professional slide templates with Chart.js visualizations
- **LLM Integration**: AI-powered insights using OpenAI/Anthropic
- **Multi-brand Support**: Compare brand performance against competitors
- **Flexible Data Input**: Supports CSV data with configurable date ranges

## Project Structure

```
weekly_report_v1.2/
├── weekly_report/          # Core report generation logic
│   ├── slides/            # Individual slide generators (slide01-slide16)
│   ├── orchestrator.py    # Main orchestration logic
│   ├── prompts.py         # LLM prompt templates
│   └── app.py            # Report generation entry point
├── html/                  # HTML slide templates (slide1-16.html)
├── core/                  # Shared utilities
│   ├── data_loader.py    # Data loading and processing
│   └── llm_client.py     # LLM client wrapper
├── interfaces/            # API interfaces
│   └── app_weekly.py     # FastAPI application
├── merge_slides.py        # HTML template merging logic
├── app_template_html.py   # Main application entry point
├── output/               # Generated reports output directory
└── requirements.txt      # Python dependencies
```

## Installation

1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Configuration

Edit `.env` file:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
LLM_PROVIDER=openai  # or anthropic

# Model Selection
OPENAI_MODEL=gpt-4-turbo-preview
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Data Configuration
DATA_PATH=path/to/your/data.csv
```

## Usage

### Command Line

Generate a weekly report:

```bash
python app_template_html.py \
  --data_path data/weekly_data.csv \
  --brand "BIDV" \
  --competitors "Vietcombank,VietinBank,Techcombank" \
  --week1_start "2024-03-01" \
  --week1_end "2024-03-07" \
  --week2_start "2024-02-23" \
  --week2_end "2024-02-29"
```

### API Server

Start the FastAPI server:

```bash
uvicorn interfaces.app_weekly:app --host 0.0.0.0 --port 8000
```

API endpoint:
```
POST /api/weekly-report
```

Request body:
```json
{
  "data_path": "data/weekly_data.csv",
  "brand": "BIDV",
  "competitors": ["Vietcombank", "VietinBank"],
  "week1_start": "2024-03-01",
  "week1_end": "2024-03-07",
  "week2_start": "2024-02-23",
  "week2_end": "2024-02-29"
}
```

## Slides Overview

1. **Slide 1**: Overview - Total mentions, engagement metrics
2. **Slide 2**: Trendline - 4-week comparison
3. **Slide 3**: Channel Distribution - Platform breakdown
4. **Slide 4**: Top Sources - Most active discussion sources
5. **Slide 5**: Top Posts - Highest engagement posts
6. **Slide 6**: Sentiment Analysis - NSR and sentiment breakdown
7. **Slide 7**: Positive Topics - Top positive discussion topics
8. **Slide 8**: Positive Posts - Posts with positive engagement
9. **Slide 9**: Negative Topics - Top negative discussion topics
10. **Slide 10**: Negative Posts - Posts with negative comments
11. **Slide 11**: Brand Comparison - Multi-brand metrics
12. **Slide 12**: Competitor Analysis - Detailed competitor breakdown
13. **Slide 13**: Brand Trendline - Daily trends with top posts
14. **Slide 14**: Multi-brand Channels - Channel distribution comparison
15. **Slide 15**: Topic Sentiment - Sentiment by topic/brand
16. **Slide 16**: Top Commented Posts - Most discussed posts

## Data Format

Input CSV should contain:

- `Topic`: Brand/topic name
- `Type`: Post type (Topic, Comment)
- `Title`: Post title
- `Content`: Post content
- `Sentiment`: Sentiment (Positive, Neutral, Negative)
- `PublishedDay`: Publication date (YYYY-MM-DD)
- `UrlTopic`: Post URL
- `Channel`: Platform/channel name
- `SiteName`: Source website name
- `Comments`: Comment count
- `Reactions`: Reaction count
- `Shares`: Share count
- `Views`: View count
- `Labels1`: Primary label/category

## Output

Generated files in `output/` directory:
- `slide1_merged.html` through `slide16_merged.html`
- `merged_report.html` (combined report)

## Version History

### v1.2 (Current)
- Slide 13: Removed insight, added top 5 posts with highest comments
- Slide 13: Legend moved to bottom with horizontal layout
- Improved chart layouts with 15% Y-axis padding
- Enhanced table spacing and readability

### v1.1
- Multi-brand support for slides 11-16
- Improved sentiment analysis
- Better error handling

### v1.0
- Initial production release
- 16 slides with complete analysis

## Support

For issues or questions, please contact the development team.

## License

Proprietary - Internal use only
