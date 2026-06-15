from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from core.mongodb import get_mongo_db
from models.user import User
from services.gap_analyzer import analyze_skill_gap
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/gap", tags=["Skill Gap Analysis"])

class GapAnalysisRequest(BaseModel):
    target_role: str
    user_skills: Optional[list] = None

@router.post("/analyze")
async def analyze_gap(
    request: GapAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    mongo_db = get_mongo_db()

    # Get user skills from resume
    if request.user_skills:
        user_skills = request.user_skills
    else:
        resume = await mongo_db["resumes"].find_one(
            {"user_id": current_user.id},
            sort=[("uploaded_at", -1)]
        )
        if not resume:
            raise HTTPException(status_code=404, detail="No resume found.")
        user_skills = resume["parsed_data"]["skills"]

    # Get role-specific required skills from ROLE_SKILL_MAP directly
    from services.job_parser import ROLE_SKILL_MAP, GENERAL_SKILLS

    target_role_lower = request.target_role.lower()
    required_skills = None

    # Match role to skill map
    for key in ROLE_SKILL_MAP:
        if key in target_role_lower or target_role_lower in key:
            required_skills = ROLE_SKILL_MAP[key]
            break

    # Also check job postings in DB for additional skills
    if not required_skills:
        cursor = mongo_db["jobs"].find(
            {"title": {"$regex": request.target_role, "$options": "i"}}
        ).limit(10)
        jobs = await cursor.to_list(length=10)

        if jobs:
            skill_frequency = {}
            for job in jobs:
                for skill in job.get("required_skills", []):
                    skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
            required_skills = list(skill_frequency.keys())
        else:
            required_skills = GENERAL_SKILLS[:20]

    analysis = analyze_skill_gap(user_skills, required_skills)

    if "error" in analysis:
        raise HTTPException(status_code=400, detail=analysis["error"])

    # Save readiness score
    db.query(User).filter(User.id == current_user.id).update({
        "readiness_score": analysis["readiness_score"],
        "target_role": request.target_role
    })
    db.commit()

    result = {
        "user": current_user.full_name,
        "target_role": request.target_role,
        "user_skills": user_skills,
        "required_skills": required_skills,
        "analysis": analysis,
        "analyzed_at": datetime.utcnow().isoformat()
    }

    await mongo_db["gap_analyses"].insert_one({
        **result,
        "user_id": current_user.id
    })

    return result

@router.get("/history")
async def get_gap_history(
    current_user: User = Depends(get_current_user)
):
    mongo_db = get_mongo_db()

    cursor = mongo_db["gap_analyses"].find(
        {"user_id": current_user.id},
        sort=[("analyzed_at", -1)]
    ).limit(5)

    analyses = await cursor.to_list(length=5)
    for a in analyses:
        a["_id"] = str(a["_id"])

    return {"history": analyses}

@router.get("/score")
async def get_current_score(
    current_user: User = Depends(get_current_user)
):
    return {
        "user": current_user.full_name,
        "target_role": current_user.target_role,
        "readiness_score": current_user.readiness_score,
        "readiness_level": (
            "Strong Match" if current_user.readiness_score >= 80 else
            "Good Match" if current_user.readiness_score >= 60 else
            "Partial Match" if current_user.readiness_score >= 40 else
            "Needs Work"
        )
    }