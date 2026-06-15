import httpx
import os
from dotenv import load_dotenv
import time

load_dotenv()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

TECH_KEYWORDS = [
    "software", "developer", "engineer", "programmer", "frontend",
    "backend", "fullstack", "full stack", "devops", "cloud", "data",
    "machine learning", "ai", "artificial intelligence", "python",
    "javascript", "react", "node", "java", "android", "ios", "mobile",
    "web", "database", "cybersecurity", "network", "system", "it ",
    "information technology", "computer", "tech", "coding", "api",
    "microservices", "kubernetes", "docker", "aws", "azure", "gcp",
    "nlp", "deep learning", "blockchain", "embedded", "firmware",
]

_cache = {}
CACHE_TTL = 30 * 60

def get_cached(key):
    if key in _cache:
        data, timestamp = _cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return data
    return None

def set_cached(key, data):
    _cache[key] = (data, time.time())

def is_tech_job(title: str, description: str = "") -> bool:
    text = (title + " " + description).lower()
    return any(keyword in text for keyword in TECH_KEYWORDS)

async def fetch_via_jsearch(query, location, page, remote_only, employment_type):
    url = "https://jsearch.p.rapidapi.com/search"
    params = {
        "query": f"{query} in {location}",
        "page": str(page),
        "num_pages": "1",
        "date_posted": "month",
    }
    if remote_only:
        params["remote_jobs_only"] = "true"
    if employment_type:
        params["employment_types"] = employment_type

    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params, headers=headers)
        data = response.json()

    jobs = data.get("data", [])
    tech_jobs = []
    for job in jobs:
        title = job.get("job_title", "")
        desc = job.get("job_description", "")[:500]
        if is_tech_job(title, desc):
            tech_jobs.append(format_job_jsearch(job))

    return tech_jobs

async def fetch_via_adzuna(query, location, page):
    country = "gb"
    if "pakistan" in location.lower():
        country = "gb"
    elif "usa" in location.lower() or "united states" in location.lower():
        country = "us"
    elif "uk" in location.lower():
        country = "gb"

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 10,
        "what": query,
        "content-type": "application/json",
        "sort_by": "date",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, params=params)
        data = response.json()

    jobs = data.get("results", [])
    tech_jobs = []
    for job in jobs:
        title = job.get("title", "")
        desc = job.get("description", "")[:500]
        if is_tech_job(title, desc):
            tech_jobs.append(format_job_adzuna(job))

    return tech_jobs

def format_job_jsearch(job: dict) -> dict:
    return {
        "id": job.get("job_id", ""),
        "title": job.get("job_title", "Unknown"),
        "company": job.get("employer_name", "Unknown Company"),
        "location": f"{job.get('job_city', '')} {job.get('job_country', '')}".strip(),
        "employment_type": job.get("job_employment_type", "Full-time"),
        "is_remote": job.get("job_is_remote", False),
        "description": job.get("job_description", "")[:800],
        "required_skills": extract_skills_from_desc(job.get("job_description", "")),
        "salary_min": job.get("job_min_salary"),
        "salary_max": job.get("job_max_salary"),
        "salary_currency": job.get("job_salary_currency", "USD"),
        "posted_at": job.get("job_posted_at_datetime_utc", ""),
        "apply_link": job.get("job_apply_link", "https://linkedin.com/jobs"),
        "company_logo": job.get("employer_logo", ""),
        "source": "LinkedIn/Indeed",
        "highlights": {
            "qualifications": job.get("job_highlights", {}).get("Qualifications", [])[:4],
            "benefits": job.get("job_highlights", {}).get("Benefits", [])[:3],
            "responsibilities": job.get("job_highlights", {}).get("Responsibilities", [])[:4],
        }
    }

def format_job_adzuna(job: dict) -> dict:
    return {
        "id": job.get("id", ""),
        "title": job.get("title", "Unknown"),
        "company": job.get("company", {}).get("display_name", "Unknown Company"),
        "location": job.get("location", {}).get("display_name", ""),
        "employment_type": "Full-time",
        "is_remote": "remote" in job.get("title", "").lower(),
        "description": job.get("description", "")[:800],
        "required_skills": extract_skills_from_desc(job.get("description", "")),
        "salary_min": job.get("salary_min"),
        "salary_max": job.get("salary_max"),
        "salary_currency": "GBP",
        "posted_at": job.get("created", ""),
        "apply_link": job.get("redirect_url", ""),
        "company_logo": "",
        "source": "Adzuna",
        "highlights": {
            "qualifications": [],
            "benefits": [],
            "responsibilities": [],
        }
    }

def extract_skills_from_desc(description: str) -> list:
    from services.job_parser import extract_skills_from_text
    return extract_skills_from_text(description[:1000])[:10]

async def fetch_live_jobs(
    query: str = "software developer",
    location: str = "Pakistan",
    page: int = 1,
    num_pages: int = 1,
    employment_type: str = None,
    remote_only: bool = False
) -> dict:
    cache_key = f"{query}_{location}_{page}_{employment_type}_{remote_only}"
    cached = get_cached(cache_key)
    if cached:
        print("[CACHE] Returning cached jobs")
        return cached

    tech_jobs = []

    # Try JSearch first
    if JSEARCH_API_KEY:
        try:
            print(f"[API] Fetching from JSearch for: {query} in {location}")
            tech_jobs = await fetch_via_jsearch(
                query, location, page, remote_only, employment_type
            )
            if tech_jobs:
                print(f"[OK] JSearch returned {len(tech_jobs)} tech jobs")
            else:
                print("[INFO] JSearch returned 0 jobs - checking Adzuna...")
        except Exception as e:
            print(f"[ERROR] JSearch API Error: {str(e)}")
            import traceback
            traceback.print_exc()

    # Fallback to Adzuna
    if not tech_jobs and ADZUNA_APP_ID and ADZUNA_APP_KEY:
        try:
            print(f"[API] Fetching from Adzuna for: {query} in {location}")
            tech_jobs = await fetch_via_adzuna(query, location, page)
            if tech_jobs:
                print(f"[OK] Adzuna returned {len(tech_jobs)} tech jobs")
            else:
                print("[INFO] Adzuna returned 0 jobs - using sample data")
        except Exception as e:
            print(f"[ERROR] Adzuna API Error: {str(e)}")
            import traceback
            traceback.print_exc()
    elif not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("[WARN] Adzuna credentials not configured")

    # Final fallback to sample data
    if not tech_jobs:
        print(f"[FALLBACK] Using sample data for: {query}")
        return get_sample_jobs(query)

    result = {
        "total": len(tech_jobs),
        "page": page,
        "jobs": tech_jobs,
        "source": "live"
    }
    set_cached(cache_key, result)
    return result


def get_sample_jobs(query: str = "") -> dict:
    jobs = [
        {
            "id": "sample_1",
            "title": "Senior React Developer",
            "company": "TechCorp Pakistan",
            "location": "Lahore, Pakistan",
            "employment_type": "Full-time",
            "is_remote": False,
            "description": "We are looking for a Senior React Developer with 3+ years experience in React.js, TypeScript, and modern frontend development practices.",
            "required_skills": ["react", "javascript", "typescript", "html", "css"],
            "salary_min": 150000,
            "salary_max": 250000,
            "salary_currency": "PKR",
            "posted_at": "2024-01-15T00:00:00Z",
            "apply_link": "https://linkedin.com/jobs",
            "company_logo": "",
            "source": "Sample Data",
            "highlights": {
                "qualifications": ["3+ years React", "TypeScript knowledge"],
                "benefits": ["Health insurance", "Remote options"],
                "responsibilities": ["Build React components", "Code reviews"]
            }
        },
        {
            "id": "sample_2",
            "title": "Python Backend Developer",
            "company": "StartupXYZ",
            "location": "Karachi, Pakistan",
            "employment_type": "Full-time",
            "is_remote": True,
            "description": "Join our growing team as a Python Backend Developer. Experience with FastAPI, PostgreSQL, and Docker required.",
            "required_skills": ["python", "fastapi", "postgresql", "docker", "git"],
            "salary_min": 120000,
            "salary_max": 200000,
            "salary_currency": "PKR",
            "posted_at": "2024-01-14T00:00:00Z",
            "apply_link": "https://linkedin.com/jobs",
            "company_logo": "",
            "source": "Sample Data",
            "highlights": {
                "qualifications": ["2+ years Python", "FastAPI or Django"],
                "benefits": ["Remote work", "Flexible hours"],
                "responsibilities": ["Build REST APIs", "Database design"]
            }
        },
        {
            "id": "sample_3",
            "title": "Full Stack Developer",
            "company": "Digital Agency",
            "location": "Islamabad, Pakistan",
            "employment_type": "Full-time",
            "is_remote": False,
            "description": "Full Stack Developer with React, Node.js, MongoDB for building scalable web applications.",
            "required_skills": ["react", "nodejs", "mongodb", "javascript", "docker"],
            "salary_min": 130000,
            "salary_max": 220000,
            "salary_currency": "PKR",
            "posted_at": "2024-01-13T00:00:00Z",
            "apply_link": "https://linkedin.com/jobs",
            "company_logo": "",
            "source": "Sample Data",
            "highlights": {
                "qualifications": ["React + Node experience", "MongoDB"],
                "benefits": ["Annual bonus", "Learning budget"],
                "responsibilities": ["Frontend + backend dev"]
            }
        },
        {
            "id": "sample_4",
            "title": "Machine Learning Engineer",
            "company": "AI Labs Pakistan",
            "location": "Remote",
            "employment_type": "Full-time",
            "is_remote": True,
            "description": "ML Engineer with Python, TensorFlow, PyTorch, and production ML deployment experience.",
            "required_skills": ["python", "machine learning", "tensorflow", "pytorch", "pandas"],
            "salary_min": 200000,
            "salary_max": 350000,
            "salary_currency": "PKR",
            "posted_at": "2024-01-12T00:00:00Z",
            "apply_link": "https://linkedin.com/jobs",
            "company_logo": "",
            "source": "Sample Data",
            "highlights": {
                "qualifications": ["ML deployment", "Python expertise"],
                "benefits": ["Stock options", "Remote first"],
                "responsibilities": ["Train ML models", "MLOps"]
            }
        },
        {
            "id": "sample_5",
            "title": "DevOps Engineer",
            "company": "CloudSystems",
            "location": "Lahore, Pakistan",
            "employment_type": "Full-time",
            "is_remote": False,
            "description": "DevOps Engineer with AWS, Docker, Kubernetes, and CI/CD pipeline experience.",
            "required_skills": ["aws", "docker", "kubernetes", "ci/cd", "linux"],
            "salary_min": 180000,
            "salary_max": 300000,
            "salary_currency": "PKR",
            "posted_at": "2024-01-11T00:00:00Z",
            "apply_link": "https://linkedin.com/jobs",
            "company_logo": "",
            "source": "Sample Data",
            "highlights": {
                "qualifications": ["AWS certification", "K8s experience"],
                "benefits": ["Certification support", "Health coverage"],
                "responsibilities": ["Cloud infra", "CI/CD pipelines"]
            }
        },
    ]
    return {"total": len(jobs), "page": 1, "jobs": jobs, "source": "sample"}