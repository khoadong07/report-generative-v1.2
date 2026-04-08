#!/usr/bin/env python3
"""
FastAPI Server for Slide Prompt Generation
Supports both daily and weekly report generation
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
import json
from datetime import datetime, timedelta, date, time
from pathlib import Path
from dotenv import load_dotenv
import traceback
from typing import Optional
from pydantic import BaseModel

# Add parent directory to Python path for imports
import sys
sys.path.insert(0, '/app')

# Load environment variables
load_dotenv()

# Import local modules
from generators.daily.generate_slide_prompt import generate_complete_prompt
from generators.weekly.generate_slide_prompt_weekly import generate_complete_prompt as generate_weekly_prompt
from generators.daily.report_generator import ReportGenerator
from generators.weekly.report_generator_weekly import WeeklyReportGenerator

# Configuration
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

if not API_KEY or not BASE_URL:
    raise ValueError("Missing API_KEY or BASE_URL in environment variables")

# FastAPI app
app = FastAPI(
    title="Slide Prompt Generator API",
    description="API for generating daily and weekly slide prompts from Excel data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    api_configured: bool

class ReportResponse(BaseModel):
    success: bool
    report_type: str
    brand_name: str
    prompt: str
    data: dict
    generated_at: str

class DailyReportResponse(ReportResponse):
    report_window: dict
    show_interactions: bool

class WeeklyReportResponse(ReportResponse):
    weeks: dict
    show_interactions: bool

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        api_configured=bool(API_KEY and BASE_URL)
    )

@app.post("/api/generate-daily", response_model=DailyReportResponse)
async def generate_daily_report(
    file: UploadFile = File(..., description="Excel file (.xlsx or .xls)"),
    brand_name: str = Form(..., description="Brand name"),
    report_date: Optional[str] = Form(None, description="Report date (YYYY-MM-DD, defaults to today)"),
    report_time: Optional[str] = Form("15:00", description="Report time (HH:MM, defaults to 15:00)"),
    show_interactions: Optional[bool] = Form(True, description="Show interaction metrics (defaults to true)")
):
    """
    Generate daily report (24h window)
    
    - **file**: Excel file containing the data
    - **brand_name**: Brand name to filter data
    - **report_date**: Report date in YYYY-MM-DD format (optional, defaults to today)
    - **report_time**: Report time in HH:MM format (optional, defaults to 15:00)
    - **show_interactions**: Show interaction metrics for slides 5&6 (optional, defaults to true)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only Excel files (.xlsx, .xls) are allowed"
            )
        
        # Parse date and time
        if report_date is None:
            report_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            parsed_date = datetime.strptime(report_date, '%Y-%m-%d').date()
            parsed_time = datetime.strptime(report_time, '%H:%M').time()
            report_datetime = datetime.combine(parsed_date, parsed_time)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
        
        # Calculate compare datetime (24h before)
        compare_datetime = report_datetime - timedelta(hours=24)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Generate report
            generator = ReportGenerator(
                api_key=API_KEY,
                base_url=BASE_URL,
                file_path=tmp_path,
                brand_name=brand_name,
                report_date=report_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                compare_date=compare_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                show_interactions=show_interactions  # Pass the new parameter
            )
            
            report_data = generator.generate_report()
            prompt_text = generate_complete_prompt(report_data)
            
            return DailyReportResponse(
                success=True,
                report_type="daily",
                brand_name=brand_name,
                report_window={
                    "start": compare_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    "end": report_datetime.strftime("%Y-%m-%d %H:%M:%S")
                },
                show_interactions=show_interactions,
                prompt=prompt_text,
                data=report_data,
                generated_at=datetime.now().isoformat()
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/generate-weekly", response_model=WeeklyReportResponse)
async def generate_weekly_report(
    file: UploadFile = File(..., description="Excel file (.xlsx or .xls)"),
    brand_name: str = Form(..., description="Brand name (from 'Topic' column)"),
    report_date: Optional[str] = Form(None, description="End date of current week (YYYY-MM-DD, defaults to today)"),
    report_time: Optional[str] = Form("15:00", description="Report time (HH:MM, defaults to 15:00)"),
    show_interactions: Optional[bool] = Form(True, description="Show interaction metrics (defaults to true)")
):
    """
    Generate weekly report (4 weeks comparison)
    
    - **file**: Excel file containing the data
    - **brand_name**: Brand name from 'Topic' column to filter data
    - **report_date**: End date of current week in YYYY-MM-DD format (optional, defaults to today)
    - **report_time**: Report time in HH:MM format (optional, defaults to 15:00)
    - **show_interactions**: Whether to show interaction metrics (optional, defaults to true)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only Excel files (.xlsx, .xls) are allowed"
            )
        
        # Parse date and time
        if report_date is None:
            report_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            parsed_date = datetime.strptime(report_date, '%Y-%m-%d').date()
            parsed_time = datetime.strptime(report_time, '%H:%M').time()
            report_datetime = datetime.combine(parsed_date, parsed_time)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid date/time format: {str(e)}")
        
        # Calculate 4 weeks
        week1_end = report_datetime
        week1_start = week1_end - timedelta(days=7)
        
        week2_end = week1_start
        week2_start = week2_end - timedelta(days=7)
        
        week3_end = week2_start
        week3_start = week3_end - timedelta(days=7)
        
        week4_end = week3_start
        week4_start = week4_end - timedelta(days=7)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Generate weekly report
            generator = WeeklyReportGenerator(
                api_key=API_KEY,
                base_url=BASE_URL,
                file_path=tmp_path,
                brand_name=brand_name,
                week1_end=week1_end.strftime("%Y-%m-%d %H:%M:%S"),
                week2_end=week2_end.strftime("%Y-%m-%d %H:%M:%S"),
                week3_end=week3_end.strftime("%Y-%m-%d %H:%M:%S"),
                week4_end=week4_end.strftime("%Y-%m-%d %H:%M:%S"),
                show_interactions=show_interactions
            )
            
            report_data = generator.generate_report()
            prompt_text = generate_weekly_prompt(report_data)
            
            return WeeklyReportResponse(
                success=True,
                report_type="weekly",
                brand_name=brand_name,
                weeks={
                    "week1": {"start": week1_start.strftime("%Y-%m-%d %H:%M:%S"), "end": week1_end.strftime("%Y-%m-%d %H:%M:%S")},
                    "week2": {"start": week2_start.strftime("%Y-%m-%d %H:%M:%S"), "end": week2_end.strftime("%Y-%m-%d %H:%M:%S")},
                    "week3": {"start": week3_start.strftime("%Y-%m-%d %H:%M:%S"), "end": week3_end.strftime("%Y-%m-%d %H:%M:%S")},
                    "week4": {"start": week4_start.strftime("%Y-%m-%d %H:%M:%S"), "end": week4_end.strftime("%Y-%m-%d %H:%M:%S")}
                },
                show_interactions=show_interactions,
                prompt=prompt_text,
                data=report_data,
                generated_at=datetime.now().isoformat()
            )
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/info")
async def api_info():
    """Get API information and available endpoints"""
    return {
        "api_name": "Slide Prompt Generator API",
        "version": "1.0.0",
        "description": "FastAPI server for generating slide prompts from Excel data",
        "endpoints": {
            "health": {
                "method": "GET",
                "path": "/health",
                "description": "Health check endpoint"
            },
            "generate_daily": {
                "method": "POST",
                "path": "/api/generate-daily",
                "description": "Generate daily report (24h window)",
                "parameters": {
                    "file": "Excel file (required)",
                    "brand_name": "Brand name (required)",
                    "report_date": "Report date YYYY-MM-DD (optional, default: today)",
                    "report_time": "Report time HH:MM (optional, default: 15:00)",
                    "show_interactions": "Show interaction metrics for slides 5&6 true/false (optional, default: true)"
                }
            },
            "generate_weekly": {
                "method": "POST",
                "path": "/api/generate-weekly",
                "description": "Generate weekly report (4 weeks comparison)",
                "parameters": {
                    "file": "Excel file (required)",
                    "brand_name": "Brand name from Topic column (required)",
                    "report_date": "End date of current week YYYY-MM-DD (optional, default: today)",
                    "report_time": "Report time HH:MM (optional, default: 15:00)",
                    "show_interactions": "Show interaction metrics true/false (optional, default: true)"
                }
            }
        },
        "supported_file_types": [".xlsx", ".xls"],
        "api_configured": bool(API_KEY and BASE_URL),
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        }
    }

if __name__ == '__main__':
    import uvicorn
    
    port = int(os.getenv('PORT', 8000))
    
    print(f"🚀 Starting Slide Prompt Generator API on port {port}")
    print(f"📊 Daily endpoint: POST /api/generate-daily")
    print(f"📅 Weekly endpoint: POST /api/generate-weekly")
    print(f"❤️ Health check: GET /health")
    print(f"ℹ️ API info: GET /api/info")
    print(f"📚 API docs: http://localhost:{port}/docs")
    print(f"📖 ReDoc: http://localhost:{port}/redoc")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )