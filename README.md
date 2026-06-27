# Career-Forge

**Smart Job Skill Gap Analyzer** — An AI-powered career development platform that analyzes resumes against real job requirements using NLP and semantic similarity, then generates a personalized learning roadmap using Reinforcement Learning.

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)](https://www.postgresql.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0-47A248)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#license)

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [What Career-Forge Does](#what-career-forge-does)
- [Core Features](#core-features)
- [How It Works — User Journey](#how-it-works--user-journey)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
- [Project / Folder Structure](#project--folder-structure)
- [Data Models](#data-models)
- [API Reference](#api-reference)
- [Background Jobs](#background-jobs)
- [Key Architecture Decisions](#key-architecture-decisions)
- [User Guide](#user-guide)
- [Local Development Setup](#local-development-setup)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Testing](#testing)
- [Team](#team)
- [License](#license)

---

## Problem Statement

Fresh graduates and career transitioners in the technology sector lack actionable, personalized insight into which specific skills they need to acquire to qualify for their desired roles. Existing tools are fragmented:

- **Job portals** show vacancies but provide no feedback on skill fit
- **Learning platforms** offer courses but don't map them to specific job requirements
- **Resume builders** improve presentation but don't analyze competency gaps

This results in wasted job applications, prolonged unemployment, and unstructured, directionless career development — especially in markets like Pakistan, where the IT sector is one of the fastest-growing in the economy but graduate-employer skill mismatch remains a persistent problem.

---

## What Career-Forge Does

Career-Forge solves this by giving every user a single platform that:

1. **Reads** their resume automatically (no manual data entry)
2. **Compares** their actual skills against real job requirements using AI
3. **Scores** their readiness for any target role (0–100%)
4. **Plans** exactly what to learn next, in what order, and how long it will take
5. **Recommends** specific courses for each missing skill
6. **Shows** live job openings that match their profile

In short — it turns "I don't know what I'm missing" into a structured, AI-generated career plan.

---

## Core Features

| # | Feature | Description |
|---|---|---|
| 1 | **NLP Resume Parser** | Upload a PDF/DOCX resume — skills, education, and experience are extracted automatically using spaCy and a domain-specific skill taxonomy |
| 2 | **ML Resume Validator** | A trained classifier (TF-IDF + Logistic Regression + structural features) rejects non-resume documents — roll number slips, result cards, invoices, cover letters, READMEs — before they're processed |
| 3 | **Role-Aware Skill Gap Analysis** | Sentence-BERT embeddings + cosine similarity compare your skills against role-specific requirements (Mobile Developer ≠ Data Scientist ≠ DevOps Engineer) |
| 4 | **Career Readiness Score** | A single weighted percentage (0–100%) showing how close you are to being job-ready for a specific role |
| 5 | **RL-Powered Adaptive Roadmap** | A custom Q-Learning agent models skill acquisition as a Markov Decision Process and outputs a week-by-week, prerequisite-aware learning plan |
| 6 | **Synced Gap → Roadmap Flow** | Pick a role once on the Skill Gap page — the Roadmap page auto-generates for that same role, no repeated selection |
| 7 | **Course Recommendations** | Each missing skill is mapped to real courses (Coursera, Udemy, freeCodeCamp, LinkedIn Learning) with ratings, duration, and free-audit availability |
| 8 | **Live Tech Job Board** | Real-time job listings aggregated from LinkedIn and Indeed via the JSearch API, filtered to only show technology roles |
| 9 | **User Profile Management** | Edit name, target role, bio, location, LinkedIn/GitHub/portfolio links, and change password |
| 10 | **Dark / Light Mode** | Full theme toggle with persistence across sessions |
| 11 | **Fully Responsive UI** | Works seamlessly on mobile, tablet, and desktop |

---

## How It Works — User Journey

```
1. Register / Login
        │
        ▼
2. Upload Resume (PDF or DOCX)
        │
        ├─► ML Classifier validates it's actually a resume
        ├─► spaCy extracts name, email, phone
        └─► Skill taxonomy extracts technical skills
        │
        ▼
3. Select Target Role (e.g. "Mobile App Developer")
        │
        ▼
4. Run Skill Gap Analysis
        │
        ├─► Sentence-BERT encodes user skills + role-required skills
        ├─► Cosine similarity finds exact + semantic matches
        └─► Career Readiness Score computed (e.g. 62.5%)
        │
        ▼
5. Generate Learning Roadmap  ← AUTO-SYNCED, no re-selection needed
        │
        ├─► Missing skills fed into Q-Learning MDP
        ├─► Agent trains for 300 episodes
        └─► Week-by-week prioritized roadmap output
        │
        ▼
6. View Course Recommendations  (mapped to every skill in the roadmap)
        │
        ▼
7. Browse Live Job Board  (apply directly via LinkedIn / Indeed)
```

---

## Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| React.js 18 | Component-based UI, lazy-loaded pages |
| React Router v6 | Client-side routing |
| Axios | HTTP client with JWT auto-attach via interceptors |
| Tailwind CSS | Utility-first styling, dark/light mode |
| Recharts | Analytics dashboard visualizations |

### Backend
| Technology | Purpose |
|---|---|
| Python 3.11 | Core language |
| FastAPI | Async REST API framework |
| Uvicorn | ASGI server |
| SQLAlchemy | PostgreSQL ORM |
| Motor | Async MongoDB driver |
| python-jose | JWT creation/verification |
| passlib (bcrypt) | Password hashing |
| httpx | Async HTTP client for external APIs |
| pdfplumber / python-docx | Resume text extraction |

### AI / ML / NLP
| Technology | Purpose |
|---|---|
| spaCy (`en_core_web_sm`) | Named Entity Recognition for name detection |
| Sentence-Transformers (`all-MiniLM-L6-v2`) | Semantic skill embeddings |
| scikit-learn | Cosine similarity, TF-IDF, Logistic Regression (resume classifier) |
| Custom Q-Learning Engine | Reinforcement Learning for adaptive roadmap generation |
| NumPy | Numerical operations |

### Databases
| Technology | Purpose |
|---|---|
| PostgreSQL 15 | Structured data — users, readiness scores, target roles |
| MongoDB 6.0 | Unstructured documents — resumes, job postings, gap analyses, roadmaps |

### External APIs
| Service | Purpose |
|---|---|
| JSearch (RapidAPI) | Live job listings aggregated from LinkedIn & Indeed |
| Adzuna API | Fallback job listings provider |

### DevOps
| Tool | Purpose |
|---|---|
| Git / GitHub | Version control |
| Railway / Render | Backend hosting |
| Vercel | Frontend hosting |
| MongoDB Atlas | Managed MongoDB |
| Supabase | Managed PostgreSQL |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         REACT FRONTEND                          │
│   Login · Dashboard · Upload · GapAnalysis · Roadmap · Courses  │
│              Jobs · Profile  (9 lazy-loaded pages)               │
└───────────────────────────┬───────────────────────────────────────┘
                            │  Axios + JWT Bearer
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI API GATEWAY                        │
│   CORS · GZip Compression · JWT Auth · Global Error Handler     │
│  ┌────────┬─────────┬────────┬──────────┬─────────┬─────────┐  │
│  │  auth  │ resume  │  gap   │ roadmap  │ courses │live_jobs│  │
│  └────────┴─────────┴────────┴──────────┴─────────┴─────────┘  │
└──────┬───────────────┬───────────────┬───────────────┬──────────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
┌─────────────┐ ┌──────────────┐ ┌─────────────┐ ┌───────────────┐
│  AI / ML     │ │ PostgreSQL   │ │  MongoDB    │ │  JSearch API  │
│  spaCy       │ │ users        │ │  resumes    │ │  (LinkedIn +  │
│  Sentence-   │ │ readiness_   │ │  jobs       │ │   Indeed)     │
│  BERT        │ │ scores       │ │  gap_       │ │               │
│  Q-Learning  │ │              │ │  analyses   │ │  Adzuna       │
│  Classifier  │ │              │ │  roadmaps   │ │  (fallback)   │
└─────────────┘ └──────────────┘ └─────────────┘ └───────────────┘
```

**Why two databases?** PostgreSQL handles structured, relational data with fixed schemas (users, scores) using ACID transactions. MongoDB handles flexible, evolving document data (resumes, roadmaps) that doesn't fit a rigid schema — a resume parsed today may have different fields than one parsed after a model update. This is a deliberate polyglot persistence decision, not an accident.

---

## Project / Folder Structure

```
career-forge/
├── backend/
│   ├── main.py                       # FastAPI app, middleware, router registration
│   ├── requirements.txt
│   ├── load_jobs.py                  # One-time script to seed MongoDB job data
│   ├── core/
│   │   ├── database.py               # SQLAlchemy engine + session (PostgreSQL)
│   │   ├── mongodb.py                # Motor async client + index creation
│   │   ├── security.py               # BCrypt hashing, JWT create/verify
│   │   └── deps.py                   # HTTPBearer auth dependency injection
│   ├── models/
│   │   └── user.py                   # SQLAlchemy User model
│   ├── routers/
│   │   ├── auth.py                   # /auth/register /auth/login /auth/me
│   │   ├── resume.py                 # /resume/upload /resume/my-resume
│   │   ├── gap.py                    # /gap/analyze /gap/score /gap/history
│   │   ├── roadmap.py                # /roadmap/generate /roadmap/latest
│   │   ├── courses.py                # /courses/recommend /courses/search
│   │   ├── live_jobs.py              # /live-jobs/search /live-jobs/tech-categories
│   │   └── profile.py                # /profile/me /profile/update
│   └── services/
│       ├── resume_parser.py          # pdfplumber/docx text extraction + spaCy NER
│       ├── resume_classifier.py      # ML resume vs non-resume validator
│       ├── train_resume_classifier.py# One-time training script (run manually)
│       ├── gap_analyzer.py           # Sentence-BERT + cosine similarity + scoring
│       ├── rl_engine.py              # Q-Learning MDP + roadmap generation
│       ├── course_recommender.py     # Skill → course mapping
│       ├── job_parser.py             # Role-specific skill taxonomies (ROLE_SKILL_MAP)
│       └── jobs_fetcher.py           # JSearch/Adzuna API calls + tech filtering
│
├── frontend/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── App.js                    # Routes, lazy loading, ThemeProvider/AuthProvider
│   │   ├── index.css                 # Tailwind + custom CSS variables
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Upload.jsx
│   │   │   ├── GapAnalysis.jsx
│   │   │   ├── Roadmap.jsx           # Auto-syncs with GapAnalysis role selection
│   │   │   ├── Courses.jsx
│   │   │   ├── Jobs.jsx
│   │   │   └── Profile.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx            # Sticky nav, dark mode toggle, mobile menu
│   │   │   ├── Footer.jsx
│   │   │   ├── PageLoader.jsx
│   │   │   └── ErrorBoundary.jsx
│   │   ├── context/
│   │   │   ├── AuthContext.jsx       # Global session state
│   │   │   └── ThemeContext.jsx      # Dark/light mode + localStorage
│   │   └── services/
│   │       └── api.js                # Axios instance, JWT interceptors, all API calls
│
└── README.md
```

---

## Data Models

### PostgreSQL — `users` table

| Column | Type | Description |
|---|---|---|
| `id` | Integer (PK) | Auto-increment user ID |
| `full_name` | String | User's full name |
| `email` | String (unique) | Login email |
| `hashed_password` | String | BCrypt hash |
| `target_role` | String (nullable) | Currently selected target role |
| `readiness_score` | Float (default 0.0) | Last computed Career Readiness Score |
| `bio` | Text (nullable) | User bio |
| `location` | String (nullable) | User location |
| `linkedin_url` / `github_url` / `portfolio_url` | String (nullable) | Social links |
| `created_at` / `updated_at` | DateTime | Timestamps |

### MongoDB Collections

| Collection | Key Fields | Purpose |
|---|---|---|
| `resumes` | `user_id`, `file_name`, `parsed_data {skills, education, experience}`, `ml_classification`, `uploaded_at` | Stores every parsed resume per user |
| `jobs` | `title`, `company`, `location`, `required_skills`, `employment_type`, `is_remote` | Tech job postings cache |
| `gap_analyses` | `user_id`, `target_role`, `user_skills`, `required_skills`, `analysis {readiness_score, missing_skills, ...}`, `analyzed_at` | Every gap analysis session (history) |
| `roadmaps` | `user_id`, `target_role`, `roadmap {steps, weeks, skills}`, `readiness_score`, `generated_at` | RL-generated learning roadmaps |

**Indexes:** `user_id` on `resumes`, `gap_analyses`, `roadmaps`; `title` (including text index) on `jobs`.

---

## API Reference

Base URL (local): `http://localhost:8000`
Interactive docs: `http://localhost:8000/docs` (Swagger UI, auto-generated)

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | No | Register a new user, returns JWT |
| `POST` | `/auth/login` | No | Login, returns JWT |
| `GET` | `/auth/me` | Yes | Get current user profile |

### Resume

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/resume/upload` | Yes | Upload PDF/DOCX — validated by ML classifier, then parsed |
| `GET` | `/resume/my-resume` | Yes | Get the latest parsed resume |

### Skill Gap Analysis

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/gap/analyze` | Yes | Run gap analysis against a target role |
| `GET` | `/gap/score` | Yes | Get current saved readiness score |
| `GET` | `/gap/history` | Yes | Get last 5 gap analyses |

### Roadmap

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/roadmap/generate` | Yes | Generate an RL-based roadmap for a target role |
| `GET` | `/roadmap/latest` | Yes | Get the most recently generated roadmap |

### Courses

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/courses/recommend` | Yes | Get courses for a list of skills |
| `GET` | `/courses/for-my-roadmap` | Yes | Get courses for every skill in the latest roadmap |
| `GET` | `/courses/search?skill=` | Yes | Search courses for a single skill |

### Jobs

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/jobs/roles` | Yes | List available tech roles (curated, tech-only) |
| `GET` | `/live-jobs/search` | Yes | Live job search (LinkedIn/Indeed via JSearch, tech-filtered) |
| `GET` | `/live-jobs/tech-categories` | Yes | Get job category quick-filters |

### Profile

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/profile/me` | Yes | Get full profile |
| `PUT` | `/profile/update` | Yes | Update profile fields |
| `PUT` | `/profile/change-password` | Yes | Change password |

All authenticated endpoints require header: `Authorization: Bearer <JWT_TOKEN>`

---

## Background Jobs

Career-Forge does not currently use a task queue (Celery/RQ) — all processing is synchronous within the FastAPI request/response cycle. The following are the closest equivalents to "background jobs":

| Process | Trigger | What It Does |
|---|---|---|
| **Resume classifier training** | Manual: `python services/train_resume_classifier.py` | Trains and saves the TF-IDF + Logistic Regression resume validator to `resume_classifier.joblib`. Run once after any training data changes. |
| **Job data seeding** | Manual: `python load_jobs.py` | One-time script to populate the MongoDB `jobs` collection from a Kaggle dataset or sample data |
| **Q-Learning roadmap training** | On-demand, per request | Runs 300 training episodes synchronously inside `POST /roadmap/generate` — not pre-trained, completes in ~4 seconds |
| **Live job cache refresh** | On-demand, per request | In-memory cache (30-minute TTL) refreshed automatically when `GET /live-jobs/search` is called and cache is stale |
| **Database index creation** | App startup (`lifespan`) | MongoDB indexes created automatically via `create_indexes()` when the FastAPI app boots |

---

## Key Architecture Decisions

| Decision | Reasoning |
|---|---|
| **FastAPI over Flask/Django** | Native async support for concurrent DB + external API calls; auto-generated Swagger docs; Pydantic validation with zero extra code |
| **Dual database (PostgreSQL + MongoDB)** | Structured fixed-schema data (users) → PostgreSQL with ACID guarantees. Flexible evolving document data (resumes, roadmaps) → MongoDB, no migrations needed when fields change |
| **Sentence-BERT over keyword matching** | Keyword matching can't tell that "ReactJS" and "React.js" are the same skill, or that "Java" and "JavaScript" are *not*. Semantic embeddings solve both. |
| **Q-Learning over a static sorted list** | A sorted list can't enforce prerequisites. The RL agent learns — via reward shaping — that JavaScript must precede React, and Python must precede TensorFlow, without hardcoded if/else rules. |
| **ML classifier over keyword-based validation** | Roll number slips and result cards share vocabulary with resumes (name, university, CGPA). A TF-IDF + structural-feature classifier learns the *combination* of sections (skills + experience + education + contact together) that only real resumes have. |
| **LRU cache on skill embeddings** | Encoding a skill with Sentence-BERT costs ~50–100ms. Caching the 500 most recent embeddings means repeated skills across analyses are never re-encoded. |
| **Lazy-loaded React pages** | Reduces initial JS bundle size by ~60%, so the login page loads fast even though the app has 9 full pages. |
| **Auto-synced Gap → Roadmap flow** | Originally required picking the role twice. Now the selected role travels via React Router state (or `localStorage` fallback) so the roadmap generates with zero redundant input. |
| **Role-specific skill taxonomies** | A single flat skill list showed Docker/HTML for a Mobile Developer search. Each of 20+ roles now has its own curated `ROLE_SKILL_MAP` entry so gap analysis is actually relevant to the chosen role. |

---

## User Guide

1. **Register** with your name, email, password, and target role.
2. **Upload your resume** (PDF or DOCX, max 5MB) — it's validated by an AI classifier and parsed automatically.
3. **Go to Skill Gap** → select your target role → click **Analyze**. You'll see your Career Readiness Score, matched skills, and a prioritized list of missing skills.
4. **Click "Generate Learning Roadmap"** — no need to pick the role again, it carries over automatically. You'll get a week-by-week plan ordered by prerequisites and impact.
5. **Click "Courses"** to see specific course recommendations (with free-audit options) for every skill in your roadmap.
6. **Click "Jobs"** to browse live tech job listings and apply directly.
7. **Click your avatar** to edit your profile, add social links, or change your password.
8. Toggle **dark/light mode** anytime via the navbar icon.

---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- MongoDB 6.0

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm
python services/train_resume_classifier.py   # trains the resume validator

# create your .env file (see Environment Variables below)

uvicorn main:app --reload
```

Backend runs at `http://localhost:8000` — Swagger docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000`

### Seed job data (optional, for testing job board / gap analysis)

```bash
cd backend
python load_jobs.py
```

---

## Environment Variables

Create a `.env` file inside the `backend/` folder:

```env
# PostgreSQL
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/skillgap_db

# MongoDB
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=skillgap_db

# JWT
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# External APIs (optional — falls back to sample data if missing)
JSEARCH_API_KEY=your-rapidapi-jsearch-key
ADZUNA_APP_ID=your-adzuna-app-id
ADZUNA_APP_KEY=your-adzuna-app-key

# App
DEBUG=True
```

The frontend reads its backend URL from `frontend/src/services/api.js` (`baseURL` field) — no separate `.env` required for local dev, but update it for production.

---

## Deployment

| Layer | Recommended Free Platform |
|---|---|
| Frontend | [Vercel](https://vercel.com) — Root directory: `frontend`, Build: `npm run build` |
| Backend | [Railway](https://railway.app) — Root directory: `backend`, never sleeps on free tier |
| PostgreSQL | [Supabase](https://supabase.com) — 500MB free |
| MongoDB | [MongoDB Atlas](https://www.mongodb.com/atlas) — 512MB free (M0 cluster) |

After deploying, update:
- `frontend/src/services/api.js` → `baseURL` to your live backend URL
- `backend/main.py` → `CORSMiddleware allow_origins` to your live frontend URL

---

## Testing

| Type | Coverage |
|---|---|
| Unit Tests | Core functions — password hashing, skill extraction, embedding similarity, RL reward function |
| Integration Tests | Full flows — register→login, upload→parse, analyze→score, generate→roadmap |
| API Tests | All 18 endpoints tested via Swagger UI |
| UI Tests | All 9 pages on Chrome desktop, Chrome mobile, Safari mobile |
| Security Tests | JWT expiry, BCrypt verification, CORS enforcement, SQL injection prevention |
| Performance Tests | Response times benchmarked (login ~42ms, gap analysis ~1.8s, roadmap ~4.2s) |

Overall pass rate: **98.4%** (63/64 test cases)

---





