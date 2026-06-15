import spacy
import re

nlp = spacy.load("en_core_web_sm")


ROLE_SKILL_MAP = {
    "mobile app developer": [
        "flutter", "dart", "react native", "swift", "kotlin", "java",
        "android", "ios", "xcode", "android studio", "firebase",
        "rest api", "sqlite", "redux", "mobx", "git", "figma",
        "push notifications", "app store", "play store", "mvvm",
        "bloc", "provider", "jetpack compose", "swiftui"
    ],
    "android developer": [
        "kotlin", "java", "android", "android studio", "jetpack compose",
        "mvvm", "rest api", "sqlite", "room", "retrofit", "firebase",
        "git", "play store", "material design", "coroutines"
    ],
    "ios developer": [
        "swift", "swiftui", "objective-c", "xcode", "cocoapods",
        "mvvm", "rest api", "core data", "firebase", "git",
        "app store", "uikit", "combine", "testflight"
    ],
    "frontend developer": [
        "html", "css", "javascript", "typescript", "react", "vue",
        "angular", "nextjs", "tailwind", "bootstrap", "sass",
        "rest api", "git", "figma", "responsive design", "webpack"
    ],
    "react developer": [
        "react", "javascript", "typescript", "nextjs", "redux",
        "html", "css", "tailwind", "rest api", "git",
        "react router", "react query", "jest", "webpack", "vite"
    ],
    "backend developer": [
        "python", "nodejs", "java", "php", "go", "django",
        "fastapi", "flask", "express", "spring", "postgresql",
        "mongodb", "redis", "docker", "rest api", "git",
        "aws", "mysql", "microservices", "authentication"
    ],
    "python developer": [
        "python", "django", "fastapi", "flask", "postgresql",
        "mongodb", "redis", "docker", "rest api", "git",
        "celery", "pandas", "numpy", "sqlalchemy", "pytest"
    ],
    "node.js developer": [
        "nodejs", "javascript", "typescript", "express", "nestjs",
        "mongodb", "postgresql", "redis", "docker", "rest api",
        "git", "graphql", "jwt", "aws", "microservices"
    ],
    "full stack developer": [
        "javascript", "typescript", "react", "nodejs", "express",
        "mongodb", "postgresql", "html", "css", "rest api",
        "docker", "git", "aws", "redis", "tailwind"
    ],
    "data scientist": [
        "python", "machine learning", "deep learning", "pandas",
        "numpy", "scikit-learn", "tensorflow", "pytorch",
        "sql", "data visualization", "statistics", "r",
        "jupyter", "matplotlib", "seaborn", "git"
    ],
    "machine learning engineer": [
        "python", "machine learning", "deep learning", "tensorflow",
        "pytorch", "scikit-learn", "pandas", "numpy", "nlp",
        "computer vision", "docker", "git", "mlops", "aws", "kubeflow"
    ],
    "data analyst": [
        "python", "sql", "excel", "pandas", "numpy",
        "data visualization", "tableau", "power bi", "statistics",
        "r", "matplotlib", "seaborn", "git", "postgresql"
    ],
    "devops engineer": [
        "docker", "kubernetes", "aws", "azure", "gcp",
        "terraform", "jenkins", "ci/cd", "linux", "bash",
        "ansible", "git", "prometheus", "grafana", "nginx"
    ],
    "cloud engineer": [
        "aws", "azure", "gcp", "terraform", "docker",
        "kubernetes", "ci/cd", "linux", "networking",
        "security", "git", "python", "bash", "cloudformation"
    ],
    "cybersecurity engineer": [
        "networking", "linux", "python", "penetration testing",
        "firewalls", "security", "siem", "incident response",
        "cryptography", "ethical hacking", "bash", "wireshark",
        "metasploit", "owasp", "vulnerability assessment"
    ],
    "ui/ux designer": [
        "figma", "adobe xd", "sketch", "prototyping", "wireframing",
        "user research", "usability testing", "html", "css",
        "design systems", "typography", "color theory", "interaction design"
    ],
    "database administrator": [
        "postgresql", "mysql", "mongodb", "oracle", "sql server",
        "redis", "sql", "database design", "backup", "performance tuning",
        "replication", "indexing", "linux", "python", "bash"
    ],
    "software engineer": [
        "python", "java", "javascript", "c++", "data structures",
        "algorithms", "git", "rest api", "docker", "sql",
        "testing", "agile", "design patterns", "linux"
    ],
    "ai engineer": [
        "python", "machine learning", "deep learning", "nlp",
        "tensorflow", "pytorch", "transformers", "langchain",
        "vector databases", "docker", "fastapi", "git", "aws"
    ],
    "blockchain developer": [
        "solidity", "ethereum", "web3.js", "smart contracts",
        "javascript", "python", "hardhat", "truffle", "metamask",
        "defi", "nft", "git", "cryptography", "nodejs"
    ],
    "game developer": [
        "unity", "unreal engine", "c#", "c++", "game design",
        "3d modeling", "physics engines", "opengl", "directx",
        "animation", "python", "git", "blender", "vr/ar"
    ],
    "embedded systems engineer": [
        "c", "c++", "embedded c", "arduino", "raspberry pi",
        "rtos", "microcontrollers", "uart", "spi", "i2c",
        "linux", "python", "pcb design", "debugging", "firmware"
    ]
}

# Flat list for general extraction when no role is specified
GENERAL_SKILLS = list(set(
    skill for skills in ROLE_SKILL_MAP.values() for skill in skills
))

def extract_skills_for_role(text: str, role: str = None) -> list:
    """Extract skills relevant to a specific role."""
    text_lower = text.lower()
    
    if role:
        # Find the best matching role key
        role_lower = role.lower()
        skill_list = None
        
        # Try exact match first
        if role_lower in ROLE_SKILL_MAP:
            skill_list = ROLE_SKILL_MAP[role_lower]
        else:
            # Try partial match
            for key in ROLE_SKILL_MAP:
                if key in role_lower or role_lower in key:
                    skill_list = ROLE_SKILL_MAP[key]
                    break
        
        # Fall back to general if no role match
        if not skill_list:
            skill_list = GENERAL_SKILLS
    else:
        skill_list = GENERAL_SKILLS
    
    found = [skill for skill in skill_list if skill in text_lower]
    return list(set(found))

def extract_skills_from_text(text: str) -> list:
    """General skill extraction (no role filter)."""
    return extract_skills_for_role(text, role=None)

def extract_experience_level(text: str) -> str:
    if not text:
        return "not specified"
    text_lower = text.lower()
    if any(word in text_lower for word in ["senior", "sr.", "lead", "principal"]):
        return "senior"
    elif any(word in text_lower for word in ["junior", "jr.", "entry", "graduate", "fresher"]):
        return "junior"
    elif any(word in text_lower for word in ["mid", "intermediate", "associate"]):
        return "mid"
    return "not specified"

def extract_job_type(text: str) -> str:
    if not text:
        return "full-time"
    text_lower = text.lower()
    if "part-time" in text_lower or "part time" in text_lower:
        return "part-time"
    elif "contract" in text_lower:
        return "contract"
    elif "internship" in text_lower or "intern" in text_lower:
        return "internship"
    elif "remote" in text_lower:
        return "remote"
    return "full-time"

def parse_job_description(
    title: str,
    description: str,
    company: str = None,
    location: str = None
) -> dict:
    skills = extract_skills_from_text(description)
    experience_level = extract_experience_level(title + " " + description)
    job_type = extract_job_type(description)

    sentences = description.split('.') if description else []
    summary = '. '.join(sentences[:3]) + '.' if len(sentences) >= 3 else description

    return {
        "title": title,
        "company": company or "Unknown",
        "location": location or "Not specified",
        "required_skills": skills,
        "total_skills": len(skills),
        "experience_level": experience_level,
        "job_type": job_type,
        "summary": summary[:500] if summary else "",
        "full_description": description
    }