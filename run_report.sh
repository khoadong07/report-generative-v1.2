#!/bin/bash

# Weekly Report Generator v1.2 - Production Run Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Weekly Report Generator v1.2 ===${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please copy .env.example to .env and configure it"
    exit 1
fi

# Default values
DATA_PATH=${DATA_PATH:-"data/weekly_data.csv"}
BRAND=${BRAND:-"BIDV"}
COMPETITORS=${COMPETITORS:-"Vietcombank,VietinBank,Techcombank"}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --data)
            DATA_PATH="$2"
            shift 2
            ;;
        --brand)
            BRAND="$2"
            shift 2
            ;;
        --competitors)
            COMPETITORS="$2"
            shift 2
            ;;
        --week1-start)
            WEEK1_START="$2"
            shift 2
            ;;
        --week1-end)
            WEEK1_END="$2"
            shift 2
            ;;
        --week2-start)
            WEEK2_START="$2"
            shift 2
            ;;
        --week2-end)
            WEEK2_END="$2"
            shift 2
            ;;
        --help)
            echo "Usage: ./run_report.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --data PATH              Path to data CSV file"
            echo "  --brand NAME             Brand name to analyze"
            echo "  --competitors LIST       Comma-separated list of competitors"
            echo "  --week1-start DATE       Week 1 start date (YYYY-MM-DD)"
            echo "  --week1-end DATE         Week 1 end date (YYYY-MM-DD)"
            echo "  --week2-start DATE       Week 2 start date (YYYY-MM-DD)"
            echo "  --week2-end DATE         Week 2 end date (YYYY-MM-DD)"
            echo ""
            echo "Example:"
            echo "  ./run_report.sh --brand BIDV --week1-start 2024-03-01 --week1-end 2024-03-07"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if data file exists
if [ ! -f "$DATA_PATH" ]; then
    echo -e "${RED}Error: Data file not found: $DATA_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}Configuration:${NC}"
echo "  Data: $DATA_PATH"
echo "  Brand: $BRAND"
echo "  Competitors: $COMPETITORS"
if [ ! -z "$WEEK1_START" ]; then
    echo "  Week 1: $WEEK1_START to $WEEK1_END"
    echo "  Week 2: $WEEK2_START to $WEEK2_END"
fi
echo ""

# Build command
CMD="python app_template_html.py --data_path \"$DATA_PATH\" --brand \"$BRAND\" --competitors \"$COMPETITORS\""

if [ ! -z "$WEEK1_START" ]; then
    CMD="$CMD --week1_start \"$WEEK1_START\" --week1_end \"$WEEK1_END\""
    CMD="$CMD --week2_start \"$WEEK2_START\" --week2_end \"$WEEK2_END\""
fi

echo -e "${GREEN}Running report generation...${NC}"
echo ""

# Run the command
eval $CMD

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=== Report generated successfully! ===${NC}"
    echo -e "Output files are in: ${YELLOW}output/${NC}"
    echo ""
    echo "Generated slides:"
    ls -1 output/slide*_merged.html 2>/dev/null | sed 's/^/  - /'
else
    echo ""
    echo -e "${RED}=== Report generation failed ===${NC}"
    exit 1
fi
