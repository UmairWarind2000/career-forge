import pdfplumber
import docx
import spacy
import re
from pathlib import Path

nlp = spacy.load("en_core_web_sm")


RESUME_KEYWORDS = [
    "experience", "education", "skills", "work", "employment",
    "university", "degree", "bachelor", "master", "project",
    "internship", "certification", "objective", "summary",
    "programming", "developer", "engineer", "graduate",
    "gpa", "cgpa", "references", "achievements", "languages",
    "framework", "database", "software", "technology"
]

def is_valid_resume(text: str) -> bool:
    """Check if extracted text actually looks like a resume."""
    if len(text.strip()) < 100:
        return False  # Too short to be a resume
    
    text_lower = text.lower()
    
    # Must contain at least 4 resume-related keywords
    matches = sum(1 for kw in RESUME_KEYWORDS if kw in text_lower)
    
    return matches >= 4

SKILLS_DATABASE = [
    "python", "javascript", "typescript", "java", "c++", "c#", "php", "ruby",
    "swift", "kotlin", "go", "rust", "scala", "r", "matlab",
    "react", "angular", "vue", "nextjs", "nodejs", "express", "django",
    "flask", "fastapi", "spring", "laravel", "asp.net",
    "html", "css", "sass", "tailwind", "bootstrap", "material ui",
    "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
    "firebase", "supabase", "dynamodb",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "git", "github", "gitlab", "bitbucket", "ci/cd", "jenkins",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
    "data analysis", "data visualization", "tableau", "power bi",
    "rest api", "graphql", "microservices", "agile", "scrum",
    "linux", "bash", "powershell", "figma", "photoshop",
    "communication", "teamwork", "leadership", "problem solving",
    "project management", "time management"
]

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF, handling images and various layouts."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Try to extract text using different methods
                page_text = page.extract_text()
                
                # If minimal text extracted, try alternative methods
                if not page_text or len(page_text.strip()) < 20:
                    # Try to extract from tables
                    for table in page.extract_tables() or []:
                        for row in table:
                            page_text = (page_text or "") + " ".join(
                                str(cell) if cell else "" for cell in row
                            ) + "\n"
                
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        # Log error but continue gracefully
        print(f"Warning: Error extracting PDF text: {e}")
    
    return text if text.strip() else ""

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found_skills = []
    for skill in SKILLS_DATABASE:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    return list(set(found_skills))

def extract_email(text: str) -> str:
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group() if match else None

def extract_phone(text: str) -> str:
    phone_pattern = r'(\+?[\d\s\-\(\)]{10,15})'
    match = re.search(phone_pattern, text)
    return match.group().strip() if match else None

def extract_education(text: str) -> list:
    education_keywords = [
        "bachelor", "master", "phd", "doctorate", "b.sc", "m.sc",
        "b.e", "m.e", "btech", "mtech", "b.tech", "m.tech",
        "university", "college", "institute", "degree"
    ]
    lines = text.split('\n')
    education = []
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in education_keywords):
            cleaned = line.strip()
            if cleaned and len(cleaned) > 5:
                education.append(cleaned)
    return education[:5]

def extract_experience(text: str) -> list:
    experience_keywords = [
        "experience", "worked", "developer", "engineer", "analyst",
        "manager", "intern", "internship", "position", "role"
    ]
    lines = text.split('\n')
    experience = []
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in experience_keywords):
            cleaned = line.strip()
            if cleaned and len(cleaned) > 10:
                experience.append(cleaned)
    return experience[:10]

def extract_name(text: str) -> str:
    doc = nlp(text[:500])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    lines = text.strip().split('\n')
    for line in lines[:3]:
        cleaned = line.strip()
        if cleaned and len(cleaned.split()) >= 2 and len(cleaned) < 50:
            return cleaned
    return "Unknown"

def parse_resume(file_path: str, file_extension: str) -> dict:
    if file_extension.lower() == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_extension.lower() in [".docx", ".doc"]:
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Use PDF or DOCX.")

    return {
        "raw_text": text,
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "total_skills_found": len(extract_skills(text))
    }