from fastapi import APIRouter, Depends, HTTPException, Query
from core.deps import get_current_user
from core.mongodb import get_mongo_db
from models.user import User
from typing import Optional

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/search")
async def search_jobs(
    role: Optional[str] = Query(None, description="Job title to search"),
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user)
):
    mongo_db = get_mongo_db()

    query = {}
    if role:
        query["title"] = {"$regex": role, "$options": "i"}

    cursor = mongo_db["jobs"].find(query).limit(limit)
    jobs = await cursor.to_list(length=limit)

    for job in jobs:
        job["_id"] = str(job["_id"])

    return {
        "total": len(jobs),
        "jobs": jobs
    }

# backend/routers/jobs.py

# Hardcoded clean tech roles list — no more random roles from job postings
TECH_ROLES = [
    "Mobile App Developer",
    "Android Developer",
    "iOS Developer",
    "Frontend Developer",
    "React Developer",
    "Backend Developer",
    "Python Developer",
    "Node.js Developer",
    "Full Stack Developer",
    "Data Scientist",
    "Machine Learning Engineer",
    "Data Analyst",
    "AI Engineer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Cybersecurity Engineer",
    "Software Engineer",
    "UI/UX Designer",
    "Database Administrator",
    "Blockchain Developer",
    "Game Developer",
    "Embedded Systems Engineer",
]

@router.get("/roles")
async def get_available_roles(
    current_user: User = Depends(get_current_user)
):
    return {"roles": sorted(TECH_ROLES)}


@router.get("/{job_title}/skills")
async def get_skills_for_role(
    job_title: str,
    current_user: User = Depends(get_current_user)
):
    from services.job_parser import ROLE_SKILL_MAP

    role_lower = job_title.lower()
    skills = None

    for key in ROLE_SKILL_MAP:
        if key in role_lower or role_lower in key:
            skills = ROLE_SKILL_MAP[key]
            break

    if not skills:
        raise HTTPException(
            status_code=404,
            detail=f"No skill data found for role: {job_title}"
        )

    return {
        "role": job_title,
        "required_skills": [
            {"skill": s, "percentage": 80}
            for s in skills
        ],
        "total_skills": len(skills)
    }