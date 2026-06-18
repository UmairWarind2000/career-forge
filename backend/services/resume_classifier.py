# backend/services/resume_classifier.py
import joblib
import os
import logging
import re

logger = logging.getLogger(__name__)

_model = None
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'resume_classifier.joblib')

# Resume validation keywords
RESUME_INDICATORS = {
    "strong": [
        "experience", "education", "skills", "work experience",
        "employment", "professional experience", "technical skills",
        "bachelor", "master", "degree", "university", "college",
        "project", "certification", "internship", "achievement"
    ],
    "weak": [
        "phone", "email", "linkedin", "github", "contact",
        "objective", "summary", "profile", "about"
    ]
}

def count_resume_keywords(text: str) -> tuple:
    """Count resume-related keywords. Returns (strong_count, weak_count)"""
    text_lower = text.lower()
    strong = sum(1 for kw in RESUME_INDICATORS["strong"] if kw in text_lower)
    weak = sum(1 for kw in RESUME_INDICATORS["weak"] if kw in text_lower)
    return strong, weak

def get_model():
    global _model
    if _model is None:
        if os.path.exists(MODEL_PATH):
            _model = joblib.load(MODEL_PATH)
            logger.info("Resume classifier model loaded successfully")
        else:
            logger.warning("Model not found. Run: python services/train_resume_classifier.py")
    return _model

def is_resume(text: str) -> dict:
    """
    Hybrid approach: ML model + keyword validation
    to determine if a document is a resume.

    Returns:
        {
            "is_resume": bool,
            "confidence": float (0.0 to 1.0),
            "label": "Resume" or "Not a Resume"
        }
    """
    model = get_model()

    if not text or len(text.strip()) < 30:
        return {
            "is_resume": False,
            "confidence": 1.0,
            "label": "Not a Resume",
            "reason": "Document is too short"
        }

    if model is None:
        logger.warning("ML model not available — skipping classification, treating as resume.")
        return {"is_resume": True, "label": "resume", "confidence": 1.0}

    try:
        prediction  = model.predict([text])[0]
        probability = model.predict_proba([text])[0]
        
        # Get probability for both classes
        prob_not_resume = probability[0]
        prob_resume = probability[1]
        
        # Keyword-based validation
        strong_kws, weak_kws = count_resume_keywords(text)
        total_kws = strong_kws + weak_kws
        
        # ML prediction with threshold
        ml_says_resume = prob_resume >= 0.515
        
        # Hybrid decision logic:
        # 1. If ML says resume AND has strong resume keywords → Accept
        # 2. If ML unsure (45-55%) but has 3+ strong keywords → Accept
        # 3. If ML says non-resume AND has weak keywords only → Reject
        # 4. Otherwise use ML prediction
        
        if ml_says_resume and strong_kws >= 2:
            is_resume_pred = True
            confidence = prob_resume
        elif 0.45 <= prob_resume <= 0.55 and strong_kws >= 3:
            # Borderline ML prediction but strong keywords indicate resume
            is_resume_pred = True
            confidence = 0.52 + (strong_kws * 0.02)  # Boost confidence
        elif not ml_says_resume and total_kws >= 5:
            # ML says non-resume but lots of resume keywords
            is_resume_pred = True
            confidence = 0.52 + (strong_kws * 0.01)
        else:
            is_resume_pred = ml_says_resume
            confidence = prob_resume
        
        confidence = min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]

        return {
            "is_resume": is_resume_pred,
            "confidence": round(confidence, 3),
            "label": "Resume" if is_resume_pred else "Not a Resume",
            "reason": None
        }

    except Exception as e:
        logger.error(f"Classifier error: {e}")
        return {
            "is_resume": False,
            "confidence": 0.0,
            "label": "Not a Resume",
            "reason": str(e)
        }