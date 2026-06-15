from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

SKILL_WEIGHTS = {
    "python": 1.5, "javascript": 1.5, "typescript": 1.4,
    "react": 1.4, "nodejs": 1.4, "nextjs": 1.3,
    "machine learning": 1.6, "deep learning": 1.6,
    "aws": 1.4, "docker": 1.4, "kubernetes": 1.3,
    "postgresql": 1.3, "mongodb": 1.3,
    "git": 1.2, "rest api": 1.2,
    "communication": 1.0, "teamwork": 1.0,
    "leadership": 1.1, "problem solving": 1.1
}

def get_skill_weight(skill: str) -> float:
    return SKILL_WEIGHTS.get(skill.lower(), 1.0)

def calculate_semantic_similarity(skill1: str, skill2: str) -> float:
    embeddings = model.encode([skill1, skill2])
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(similarity)

def find_similar_skills(
    user_skill: str,
    required_skills: list,
    threshold: float = 0.75
) -> list:
    similar = []
    for req_skill in required_skills:
        if user_skill.lower() == req_skill.lower():
            continue
        similarity = calculate_semantic_similarity(user_skill, req_skill)
        if similarity >= threshold:
            similar.append({
                "skill": req_skill,
                "similarity_score": round(similarity, 2)
            })
    return similar

def analyze_skill_gap(
    user_skills: list,
    required_skills: list
) -> dict:
    user_skills_lower = [s.lower() for s in user_skills]
    required_skills_lower = [s.lower() for s in required_skills]

    exactly_matched = []
    semantically_matched = []
    missing_skills = []

    for req_skill in required_skills_lower:
        if req_skill in user_skills_lower:
            exactly_matched.append(req_skill)
        else:
            is_semantic_match = False
            for user_skill in user_skills_lower:
                similarity = calculate_semantic_similarity(user_skill, req_skill)
                if similarity >= 0.78:
                    semantically_matched.append({
                        "required_skill": req_skill,
                        "matched_with": user_skill,
                        "similarity": round(similarity, 2)
                    })
                    is_semantic_match = True
                    break
            if not is_semantic_match:
                missing_skills.append(req_skill)

    total_required = len(required_skills_lower)
    if total_required == 0:
        return {
            "error": "No required skills found for this role"
        }

    exact_score = sum(
        get_skill_weight(s) for s in exactly_matched
    )
    semantic_score = sum(
        get_skill_weight(m["required_skill"]) * 0.8
        for m in semantically_matched
    )
    total_possible_score = sum(
        get_skill_weight(s) for s in required_skills_lower
    )

    raw_score = ((exact_score + semantic_score) / total_possible_score) * 100
    readiness_score = round(min(raw_score, 100), 1)

    if readiness_score >= 80:
        readiness_level = "Strong Match"
        readiness_color = "green"
        message = "You are highly qualified for this role. Apply with confidence."
    elif readiness_score >= 60:
        readiness_level = "Good Match"
        readiness_color = "blue"
        message = "You have most of the required skills. A little upskilling will make you job-ready."
    elif readiness_score >= 40:
        readiness_level = "Partial Match"
        readiness_color = "yellow"
        message = "You have a foundation but need to develop several key skills."
    else:
        readiness_level = "Needs Work"
        readiness_color = "red"
        message = "Significant upskilling needed but achievable with a focused learning plan."

    missing_with_priority = []
    for skill in missing_skills:
        weight = get_skill_weight(skill)
        priority = "high" if weight >= 1.4 else "medium" if weight >= 1.2 else "low"
        missing_with_priority.append({
            "skill": skill,
            "weight": weight,
            "priority": priority
        })

    missing_with_priority.sort(key=lambda x: x["weight"], reverse=True)

    return {
        "readiness_score": readiness_score,
        "readiness_level": readiness_level,
        "readiness_color": readiness_color,
        "message": message,
        "total_required_skills": total_required,
        "total_user_skills": len(user_skills_lower),
        "exactly_matched": exactly_matched,
        "semantically_matched": semantically_matched,
        "missing_skills": missing_with_priority,
        "match_breakdown": {
            "exact_matches": len(exactly_matched),
            "semantic_matches": len(semantically_matched),
            "missing": len(missing_skills)
        }
    }