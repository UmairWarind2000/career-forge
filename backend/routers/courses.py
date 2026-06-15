from fastapi import APIRouter, Depends, HTTPException, Query
from core.deps import get_current_user
from core.mongodb import get_mongo_db
from models.user import User
from services.course_recommender import (
    get_courses_for_skill,
    recommend_courses_for_roadmap
)
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/courses", tags=["Course Recommendations"])

class CourseRequest(BaseModel):
    skills: List[str]

@router.post("/recommend")
async def recommend_courses(
    request: CourseRequest,
    current_user: User = Depends(get_current_user)
):
    if not request.skills:
        raise HTTPException(
            status_code=400,
            detail="Please provide at least one skill"
        )

    recommendations = []
    for skill in request.skills:
        courses = get_courses_for_skill(skill)
        recommendations.append({
            "skill": skill,
            "courses": courses
        })

    return {
        "user": current_user.full_name,
        "total_skills": len(request.skills),
        "recommendations": recommendations
    }

@router.get("/for-my-roadmap")
async def get_courses_for_my_roadmap(
    current_user: User = Depends(get_current_user)
):
    mongo_db = get_mongo_db()

    roadmap_doc = await mongo_db["roadmaps"].find_one(
        {"user_id": current_user.id},
        sort=[("generated_at", -1)]
    )

    if not roadmap_doc:
        raise HTTPException(
            status_code=404,
            detail="No roadmap found. Please generate a roadmap first."
        )

    roadmap_items = roadmap_doc.get("roadmap", {}).get("roadmap", [])

    if not roadmap_items:
        raise HTTPException(
            status_code=404,
            detail="Roadmap is empty."
        )

    recommendations = recommend_courses_for_roadmap(roadmap_items)

    free_courses = sum(
        1 for r in recommendations
        for c in r["courses"] if c.get("free_audit")
    )
    total_courses = sum(len(r["courses"]) for r in recommendations)

    return {
        "user": current_user.full_name,
        "target_role": roadmap_doc.get("target_role"),
        "total_skills_in_roadmap": len(roadmap_items),
        "total_courses_recommended": total_courses,
        "free_courses_available": free_courses,
        "recommendations": recommendations
    }

@router.get("/search")
async def search_courses(
    skill: str = Query(..., description="Skill to search courses for"),
    current_user: User = Depends(get_current_user)
):
    courses = get_courses_for_skill(skill, max_courses=5)
    return {
        "skill": skill,
        "total": len(courses),
        "courses": courses
    }

@router.get("/personalized-by-gap")
async def get_personalized_courses_by_gap(
    current_user: User = Depends(get_current_user)
):
    """
    Get course recommendations based on the latest gap analysis.
    This ensures recommendations are personalized to the specific skill gaps.
    """
    mongo_db = get_mongo_db()

    # Get latest gap analysis
    gap_analysis = await mongo_db["gap_analyses"].find_one(
        {"user_id": current_user.id},
        sort=[("analyzed_at", -1)]
    )

    if not gap_analysis:
        raise HTTPException(
            status_code=404,
            detail="No gap analysis found. Please run a gap analysis first."
        )

    # Extract missing skills with their priorities
    missing_skills = gap_analysis.get("analysis", {}).get("missing_skills", [])
    
    if not missing_skills:
        return {
            "user": current_user.full_name,
            "target_role": gap_analysis.get("target_role"),
            "message": "No missing skills! You are fully qualified for this role.",
            "recommendations": [],
            "total_courses": 0,
            "free_courses": 0
        }

    # Get courses for each missing skill, organized by priority
    recommendations = []
    total_courses = 0
    free_courses_count = 0

    # Sort by priority: high → medium → low
    priority_order = {"high": 0, "medium": 1, "low": 2}
    sorted_missing_skills = sorted(
        missing_skills,
        key=lambda x: priority_order.get(x.get("priority", "medium"), 1)
    )

    for skill_data in sorted_missing_skills:
        skill = skill_data.get("skill", "")
        priority = skill_data.get("priority", "medium")
        
        if not skill:
            continue

        courses = get_courses_for_skill(skill, max_courses=5)
        free_count = sum(1 for c in courses if c.get("free_audit"))
        
        recommendations.append({
            "skill": skill,
            "priority": priority,
            "courses": courses,
            "free_courses_for_skill": free_count
        })
        
        total_courses += len(courses)
        free_courses_count += free_count

    return {
        "user": current_user.full_name,
        "target_role": gap_analysis.get("target_role"),
        "readiness_score": gap_analysis.get("analysis", {}).get("readiness_score"),
        "readiness_level": gap_analysis.get("analysis", {}).get("readiness_level"),
        "total_missing_skills": len(missing_skills),
        "total_courses_recommended": total_courses,
        "free_courses_available": free_courses_count,
        "recommendations": recommendations
    }