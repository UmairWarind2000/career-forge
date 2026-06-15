from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from core.mongodb import get_mongo_db
from models.user import User
from services.rl_engine import generate_learning_roadmap
from services.gap_analyzer import analyze_skill_gap
from services.course_recommender import get_courses_for_skill
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/roadmap", tags=["Learning Roadmap"])

class RoadmapRequest(BaseModel):
    target_role: str
    user_skills: Optional[list] = None

@router.post("/generate")
async def generate_roadmap(
    request: RoadmapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a personalized roadmap based on the latest gap analysis.
    Roadmap is ordered from basic to advanced skills and includes courses.
    """
    mongo_db = get_mongo_db()
    from services.job_parser import ROLE_SKILL_MAP, GENERAL_SKILLS

    # Try to get the latest gap analysis
    latest_gap = await mongo_db["gap_analyses"].find_one(
        {"user_id": current_user.id},
        sort=[("analyzed_at", -1)]
    )

    # If gap analysis exists and is for the requested role, use it
    # Otherwise, create a new gap analysis
    if latest_gap and latest_gap.get("target_role", "").lower() == request.target_role.lower():
        user_skills = latest_gap.get("user_skills", [])
        required_skills = latest_gap.get("required_skills", [])
        gap_analysis = latest_gap.get("analysis", {})
        missing_skills_data = gap_analysis.get("missing_skills", [])
    else:
        # Get user skills
        if request.user_skills:
            user_skills = request.user_skills
        else:
            resume = await mongo_db["resumes"].find_one(
                {"user_id": current_user.id},
                sort=[("uploaded_at", -1)]
            )
            if not resume:
                raise HTTPException(
                    status_code=404,
                    detail="No resume found. Please upload your resume first."
                )
            user_skills = resume["parsed_data"]["skills"]

        # Get required skills for the target role
        # Priority: 1) ROLE_SKILL_MAP, 2) Jobs DB, 3) GENERAL_SKILLS fallback
        target_role_lower = request.target_role.lower()
        required_skills = None

        # Try to match from ROLE_SKILL_MAP first
        for key in ROLE_SKILL_MAP:
            if key in target_role_lower or target_role_lower in key:
                required_skills = ROLE_SKILL_MAP[key]
                break

        # If not found, try jobs database
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
                # Fallback to general skills
                required_skills = GENERAL_SKILLS[:20]

        # Run gap analysis
        gap_analysis = analyze_skill_gap(user_skills, required_skills)
        missing_skills_data = gap_analysis.get("missing_skills", [])

    # Extract missing skills in priority order
    # Sort by: high priority first, then by weight/difficulty
    missing_skills = [
        item["skill"] for item in sorted(
            missing_skills_data,
            key=lambda x: (
                0 if x.get("priority") == "high" else 1 if x.get("priority") == "medium" else 2,
                -x.get("weight", 0)  # Higher weight = more important
            )
        )
    ]

    if not missing_skills:
        return {
            "user": current_user.full_name,
            "target_role": request.target_role,
            "message": "Congratulations! You have all required skills for this role.",
            "roadmap": {"roadmap": []},
            "generated_at": datetime.utcnow().isoformat()
        }

    # Generate roadmap based on MISSING SKILLS only
    roadmap = generate_learning_roadmap(
        missing_skills, user_skills, request.target_role
    )

    # Enhance roadmap items with courses
    roadmap_items = roadmap.get("roadmap", [])
    enhanced_roadmap = []
    total_courses = 0
    free_courses = 0

    for item in roadmap_items:
        skill = item.get("skill", "")
        if not skill:
            enhanced_roadmap.append(item)
            continue

        courses = get_courses_for_skill(skill, max_courses=3)
        free_for_skill = sum(1 for c in courses if c.get("free_audit"))
        
        enhanced_item = {
            **item,
            "recommended_courses": courses,
            "free_courses_available": free_for_skill
        }
        
        enhanced_roadmap.append(enhanced_item)
        total_courses += len(courses)
        free_courses += free_for_skill

    # Update roadmap with enhanced items
    roadmap_with_courses = {**roadmap, "roadmap": enhanced_roadmap}

    result = {
        "user": current_user.full_name,
        "target_role": request.target_role,
        "current_skills": user_skills,
        "readiness_score": gap_analysis.get("readiness_score", 0),
        "readiness_level": gap_analysis.get("readiness_level", "Unknown"),
        "missing_skills": missing_skills,
        "missing_skills_count": len(missing_skills),
        "roadmap": roadmap_with_courses,
        "course_summary": {
            "total_courses": total_courses,
            "free_courses": free_courses
        },
        "generated_at": datetime.utcnow().isoformat()
    }

    await mongo_db["roadmaps"].insert_one({
        **result,
        "user_id": current_user.id
    })

    return result

@router.get("/latest")
async def get_latest_roadmap(
    current_user: User = Depends(get_current_user)
):
    mongo_db = get_mongo_db()

    roadmap = await mongo_db["roadmaps"].find_one(
        {"user_id": current_user.id},
        sort=[("generated_at", -1)]
    )

    if not roadmap:
        raise HTTPException(
            status_code=404,
            detail="No roadmap found. Please generate one first."
        )

    roadmap["_id"] = str(roadmap["_id"])
    return roadmap


@router.get("/comprehensive-plan")
async def get_comprehensive_learning_plan(
    current_user: User = Depends(get_current_user)
):
    """
    Returns a comprehensive learning plan combining:
    - Gap analysis results
    - Personalized roadmap based on missing skills
    - Course recommendations for each skill in the roadmap
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

    # Get latest roadmap
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
    
    # Enhance roadmap items with courses
    enhanced_roadmap = []
    total_courses = 0
    free_courses = 0

    for item in roadmap_items:
        skill = item.get("skill", "")
        if not skill:
            continue

        courses = get_courses_for_skill(skill, max_courses=3)
        free_for_skill = sum(1 for c in courses if c.get("free_audit"))
        
        enhanced_item = {
            **item,
            "recommended_courses": courses,
            "free_courses_available": free_for_skill
        }
        
        enhanced_roadmap.append(enhanced_item)
        total_courses += len(courses)
        free_courses += free_for_skill

    # Extract missing skills from gap analysis
    missing_skills = gap_analysis.get("analysis", {}).get("missing_skills", [])

    return {
        "user": current_user.full_name,
        "target_role": gap_analysis.get("target_role"),
        "gap_analysis": {
            "readiness_score": gap_analysis.get("analysis", {}).get("readiness_score"),
            "readiness_level": gap_analysis.get("analysis", {}).get("readiness_level"),
            "readiness_message": gap_analysis.get("analysis", {}).get("message"),
            "total_missing_skills": len(missing_skills),
            "missing_skills": [
                {
                    "skill": s.get("skill"),
                    "priority": s.get("priority"),
                    "weight": s.get("weight")
                }
                for s in missing_skills
            ]
        },
        "learning_roadmap": {
            "total_steps": len(enhanced_roadmap),
            "total_estimated_weeks": sum(
                item.get("estimated_weeks", 0) for item in enhanced_roadmap
            ),
            "steps": enhanced_roadmap
        },
        "course_recommendations": {
            "total_courses": total_courses,
            "free_courses": free_courses,
            "by_skill": [
                {
                    "skill": item.get("skill"),
                    "priority": item.get("priority"),
                    "courses": item.get("recommended_courses", [])
                }
                for item in enhanced_roadmap
            ]
        },
        "generated_at": roadmap_doc.get("generated_at"),
        "analyzed_at": gap_analysis.get("analyzed_at")
    }