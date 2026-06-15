from fastapi import APIRouter, Depends, Query
from core.deps import get_current_user
from models.user import User
from services.jobs_fetcher import fetch_live_jobs
from typing import Optional
import os

router = APIRouter(prefix="/live-jobs", tags=["Live Job Listings"])

@router.get("/search")
async def search_live_jobs(
    query: str = Query("software developer", description="Job title or keyword"),
    location: str = Query("Pakistan", description="Job location"),
    page: int = Query(1, ge=1),
    remote_only: bool = Query(False),
    employment_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    results = await fetch_live_jobs(
        query=query,
        location=location,
        page=page,
        remote_only=remote_only,
        employment_type=employment_type
    )
    return results

@router.get("/status")
async def get_api_status(current_user: User = Depends(get_current_user)):
    """Check if external APIs are properly configured"""
    jsearch_key = os.getenv("JSEARCH_API_KEY")
    adzuna_id = os.getenv("ADZUNA_APP_ID")
    adzuna_key = os.getenv("ADZUNA_APP_KEY")
    
    return {
        "jsearch_configured": bool(jsearch_key),
        "jsearch_key_preview": f"{jsearch_key[:10]}...{jsearch_key[-5:]}" if jsearch_key else "NOT SET",
        "adzuna_configured": bool(adzuna_id and adzuna_key),
        "adzuna_id_preview": f"{adzuna_id[:5]}...{adzuna_id[-3:]}" if adzuna_id else "NOT SET",
        "status": "ℹ️ If both APIs show 'NOT SET', real-time jobs will use sample data fallback"
    }

@router.get("/tech-categories")
async def get_tech_categories(
    current_user: User = Depends(get_current_user)
):
    return {
        "categories": [
            { "label": "Frontend", "query": "frontend developer", "icon": "🎨" },
            { "label": "Backend", "query": "backend developer", "icon": "⚙️" },
            { "label": "Full Stack", "query": "full stack developer", "icon": "🔧" },
            { "label": "Mobile", "query": "mobile developer", "icon": "📱" },
            { "label": "Data Science", "query": "data scientist", "icon": "📊" },
            { "label": "Machine Learning", "query": "machine learning engineer", "icon": "🤖" },
            { "label": "DevOps", "query": "devops engineer", "icon": "☁️" },
            { "label": "Cybersecurity", "query": "cybersecurity engineer", "icon": "🔒" },
            { "label": "AI Engineer", "query": "ai engineer", "icon": "🧠" },
            { "label": "Cloud", "query": "cloud engineer aws", "icon": "⛅" },
            { "label": "Python", "query": "python developer", "icon": "🐍" },
            { "label": "React", "query": "react developer", "icon": "⚛️" },
        ]
    }