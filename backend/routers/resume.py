from services.resume_classifier import is_resume
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from core.mongodb import get_mongo_db
from models.user import User
from services.resume_parser import parse_resume
import os
import shutil
from pathlib import Path
from datetime import datetime


router = APIRouter(prefix="/resume", tags=["Resume"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Step 1 — MIME type check
    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are accepted."
        )

    # Step 2 — File size check (max 5MB)
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be under 5MB."
        )
    await file.seek(0)  # Reset after reading

    # Step 3 — Save file
    file_extension = Path(file.filename).suffix.lower()
    file_name = f"resume_{current_user.id}_{int(datetime.now().timestamp())}{file_extension}"
    file_path = UPLOAD_DIR / file_name

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 4 — Parse
    try:
        parsed_data = parse_resume(str(file_path), file_extension)
    except Exception as e:
        os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    # Step 5 — ML Resume Validation
    result = is_resume(parsed_data["raw_text"])

    if not result["is_resume"]:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"The uploaded document does not appear to be a resume "
                   f"(AI confidence: {round(result['confidence'] * 100, 1)}%). "
                   f"Please upload your CV or resume document only."
        )

    # Step 6 — Store in MongoDB
    mongo_db = get_mongo_db()
    resume_document = {
        "user_id": current_user.id,
        "user_email": current_user.email,
        "file_name": file_name,
        "original_file_name": file.filename,
        "parsed_data": parsed_data,
        "ml_classification": {
            "label": result["label"],
            "confidence": result["confidence"],
        },
        "uploaded_at": datetime.utcnow().isoformat()
    }
    await mongo_db["resumes"].insert_one(resume_document)

    # Step 7 — Update user's updated_at timestamp
    db.query(User).filter(User.id == current_user.id).update({
        "updated_at": datetime.utcnow()
    })
    db.commit()

    # Step 8 — Return success response
    return {
        "message": "Resume uploaded and parsed successfully",
        "data": {
            "name": parsed_data.get("name"),
            "email": parsed_data.get("email"),
            "phone": parsed_data.get("phone"),
            "skills_found": parsed_data.get("skills", []),
            "total_skills": parsed_data.get("total_skills_found", 0),
            "education": parsed_data.get("education", []),
            "experience": parsed_data.get("experience", [])
        }
    }


@router.get("/my-resume")
async def get_my_resume(
    current_user: User = Depends(get_current_user)
):
    mongo_db = get_mongo_db()
    resume = await mongo_db["resumes"].find_one(
        {"user_id": current_user.id},
        sort=[("uploaded_at", -1)]
    )

    if not resume:
        raise HTTPException(status_code=404, detail="No resume found. Please upload one.")

    resume["_id"] = str(resume["_id"])
    return resume