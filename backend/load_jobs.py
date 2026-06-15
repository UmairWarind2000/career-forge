import pandas as pd
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from services.job_parser import parse_job_description
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

async def load_jobs():
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB_NAME]

    print("Reading CSV file...")
    try:
        df = pd.read_csv("../data/job_postings.csv")
    except FileNotFoundError:
        print("CSV not found. Creating sample job data instead...")
        df = create_sample_data()

    df = df.head(500)
    print(f"Processing {len(df)} job postings...")

    await db["jobs"].drop()

    jobs_to_insert = []
    for index, row in df.iterrows():
        title = str(row.get("title", row.get("job_title", "Software Developer")))
        description = str(row.get("description", row.get("job_description", "")))
        company = str(row.get("company_name", row.get("company", "Unknown")))
        location = str(row.get("location", "Remote"))

        if len(description) < 20:
            continue

        parsed = parse_job_description(title, description, company, location)
        if parsed["total_skills"] > 0:
            jobs_to_insert.append(parsed)

    if jobs_to_insert:
        await db["jobs"].insert_many(jobs_to_insert)
        print(f"Successfully loaded {len(jobs_to_insert)} jobs into MongoDB")
    else:
        print("No valid jobs found. Loading sample data...")
        sample_jobs = get_sample_jobs()
        await db["jobs"].insert_many(sample_jobs)
        print(f"Loaded {len(sample_jobs)} sample jobs")

    client.close()

def create_sample_data():
    import pandas as pd
    data = {
        "title": ["Frontend Developer", "Backend Developer", "Full Stack Developer",
                  "Data Scientist", "DevOps Engineer", "Machine Learning Engineer",
                  "React Developer", "Python Developer", "Node.js Developer"],
        "description": [
            "We need a frontend developer with React, JavaScript, HTML, CSS, Tailwind. Experience with REST API, Git required. Agile environment.",
            "Backend developer needed. Python, Django, PostgreSQL, MongoDB, Redis, Docker, AWS. REST API design experience required.",
            "Full stack developer with React, Node.js, Express, MongoDB, PostgreSQL, Docker, Git, AWS. Agile team.",
            "Data scientist with Python, machine learning, deep learning, pandas, numpy, scikit-learn, tensorflow, data visualization, SQL.",
            "DevOps engineer with AWS, Docker, Kubernetes, Terraform, CI/CD, Jenkins, Linux, Bash, Git.",
            "ML engineer with Python, pytorch, tensorflow, machine learning, deep learning, NLP, computer vision, pandas, numpy.",
            "React developer with JavaScript, TypeScript, React, NextJS, HTML, CSS, Tailwind, REST API, Git.",
            "Python developer with Python, Django, FastAPI, PostgreSQL, Redis, Docker, Git, REST API.",
            "Node.js developer with JavaScript, TypeScript, NodeJS, Express, MongoDB, PostgreSQL, Docker, AWS, Git."
        ],
        "company_name": ["TechCorp", "StartupXYZ", "BigTech", "DataCo", "CloudSys",
                        "AI Labs", "WebAgency", "PyShop", "NodeWorks"],
        "location": ["Remote", "New York", "San Francisco", "London", "Remote",
                    "Boston", "Remote", "Austin", "Seattle"]
    }
    return pd.DataFrame(data)

def get_sample_jobs():
    return [
        {
            "title": "Frontend Developer",
            "company": "TechCorp",
            "location": "Remote",
            "required_skills": ["react", "javascript", "html", "css", "tailwind", "rest api", "git"],
            "total_skills": 7,
            "experience_level": "mid",
            "job_type": "remote",
            "summary": "Frontend developer role requiring React and modern web technologies.",
            "full_description": "We need a frontend developer with React, JavaScript, HTML, CSS, Tailwind."
        },
        {
            "title": "Backend Developer",
            "company": "StartupXYZ",
            "location": "New York",
            "required_skills": ["python", "django", "postgresql", "mongodb", "redis", "docker", "aws"],
            "total_skills": 7,
            "experience_level": "mid",
            "job_type": "full-time",
            "summary": "Backend developer with Python and cloud experience needed.",
            "full_description": "Backend developer needed with Python, Django, PostgreSQL, MongoDB."
        },
        {
            "title": "Full Stack Developer",
            "company": "BigTech",
            "location": "San Francisco",
            "required_skills": ["react", "nodejs", "express", "mongodb", "postgresql", "docker", "git", "aws"],
            "total_skills": 8,
            "experience_level": "mid",
            "job_type": "full-time",
            "summary": "Full stack developer for our growing engineering team.",
            "full_description": "Full stack developer with React, Node.js, MongoDB, PostgreSQL, Docker."
        },
        {
            "title": "Data Scientist",
            "company": "DataCo",
            "location": "London",
            "required_skills": ["python", "machine learning", "pandas", "numpy", "scikit-learn", "tensorflow", "data visualization"],
            "total_skills": 7,
            "experience_level": "mid",
            "job_type": "full-time",
            "summary": "Data scientist to build ML models for our platform.",
            "full_description": "Data scientist with Python, machine learning, pandas, tensorflow required."
        },
        {
            "title": "React Developer",
            "company": "WebAgency",
            "location": "Remote",
            "required_skills": ["react", "javascript", "typescript", "nextjs", "html", "css", "rest api", "git"],
            "total_skills": 8,
            "experience_level": "junior",
            "job_type": "remote",
            "summary": "React developer for building modern web applications.",
            "full_description": "React developer with JavaScript, TypeScript, NextJS, HTML, CSS required."
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudSys",
            "location": "Remote",
            "required_skills": ["aws", "docker", "kubernetes", "terraform", "ci/cd", "linux", "git"],
            "total_skills": 7,
            "experience_level": "senior",
            "job_type": "remote",
            "summary": "DevOps engineer to manage our cloud infrastructure.",
            "full_description": "DevOps engineer with AWS, Docker, Kubernetes, Terraform, CI/CD required."
        },
        {
            "title": "Python Developer",
            "company": "PyShop",
            "location": "Austin",
            "required_skills": ["python", "fastapi", "postgresql", "redis", "docker", "git", "rest api"],
            "total_skills": 7,
            "experience_level": "mid",
            "job_type": "full-time",
            "summary": "Python developer to build and maintain backend services.",
            "full_description": "Python developer with FastAPI, PostgreSQL, Redis, Docker required."
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Labs",
            "location": "Boston",
            "required_skills": ["python", "pytorch", "tensorflow", "machine learning", "deep learning", "nlp", "pandas", "numpy"],
            "total_skills": 8,
            "experience_level": "senior",
            "job_type": "full-time",
            "summary": "ML engineer to develop and deploy machine learning models.",
            "full_description": "ML engineer with Python, PyTorch, TensorFlow, NLP experience required."
        }
    ]

if __name__ == "__main__":
    asyncio.run(load_jobs())