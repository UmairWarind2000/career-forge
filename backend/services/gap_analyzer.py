# backend/services/gap_analyzer.py

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
    embeddings = model.encode([skill1, skill2], show_progress_bar=False)
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(similarity)

def find_similar_skills(
    user_skill: str,
    required_skills: list,
    threshold: float = 0.75
) -> list:
    if not required_skills:
        return []

    # Encode user skill + all required skills in one batch
    all_skills = [user_skill] + [s for s in required_skills if s.lower() != user_skill.lower()]
    embeddings = model.encode(all_skills, batch_size=64, show_progress_bar=False)

    user_embedding = embeddings[0]
    req_embeddings = embeddings[1:]
    similarities = cosine_similarity([user_embedding], req_embeddings)[0]

    similar = []
    for i, req_skill in enumerate(all_skills[1:]):
        similarity = float(similarities[i])
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

    total_required = len(required_skills_lower)
    if total_required == 0:
        return {
            "error": "No required skills found for this role"
        }

    # Separate exact matches before encoding — no embeddings needed for these
    exact_match_set = set(user_skills_lower) & set(required_skills_lower)
    skills_needing_embedding = [s for s in required_skills_lower if s not in exact_match_set]

    exactly_matched = [s for s in required_skills_lower if s in exact_match_set]
    semantically_matched = []
    missing_skills = []

    if skills_needing_embedding:
        # Encode ALL remaining user + required skills in two batches (not per pair)
        all_skills = user_skills_lower + skills_needing_embedding
        all_embeddings = model.encode(all_skills, batch_size=64, show_progress_bar=False)

        user_embeddings = all_embeddings[:len(user_skills_lower)]
        req_embeddings = all_embeddings[len(user_skills_lower):]

        # Full similarity matrix in one shot: shape (n_required, n_user)
        sim_matrix = cosine_similarity(req_embeddings, user_embeddings)

        for i, req_skill in enumerate(skills_needing_embedding):
            best_idx = int(np.argmax(sim_matrix[i]))
            best_score = float(sim_matrix[i][best_idx])

            if best_score >= 0.78:
                semantically_matched.append({
                    "required_skill": req_skill,
                    "matched_with": user_skills_lower[best_idx],
                    "similarity": round(best_score, 2)
                })
            else:
                missing_skills.append(req_skill)

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