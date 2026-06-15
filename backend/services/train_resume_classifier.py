import joblib
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import FunctionTransformer
from sklearn.pipeline import FeatureUnion
import re

# ═══════════════════════════════════════════════════════════════════════════
# FEATURE ENGINEERING
# These features capture the STRUCTURE of a resume, not just its words.
# A roll number slip has name + university but NOT skills + experience.
# A result card has CGPA + university but NOT contact + projects.
# Only a resume has ALL sections together.
# ═══════════════════════════════════════════════════════════════════════════

RESUME_SECTION_PATTERNS = [
    r'\b(skills?|technical skills?|core competencies|expertise)\b',
    r'\b(experience|work experience|employment|work history|professional experience)\b',
    r'\b(education|academic|qualification|degree|university|college|institute)\b',
    r'\b(project|projects|personal projects|academic projects|final year project)\b',
    r'\b(certification|certifications?|certificate|certified)\b',
    r'\b(objective|summary|professional summary|career objective|profile)\b',
    r'\b(reference|references|available upon request)\b',
    r'\b(internship|intern|trainee)\b',
    r'\b(achievement|accomplishment|award|honour|honor)\b',
    r'\b(language|languages|english|urdu)\b',
]

NON_RESUME_PATTERNS = [
    # Roll number slips
    r'\b(roll no|roll number|exam roll|seat no|seat number|admit card|hall ticket)\b',
    r'\b(examination|mid term|final exam|paper|theory|practical|date sheet)\b',
    r'\b(room no|room number|venue|center|centre|invigila)\b',
    # Result cards / transcripts
    r'\b(transcript|grade sheet|marks sheet|result card|semester result)\b',
    r'\b(credit hours?|credit hour|gpa points?|grade points?|letter grade)\b',
    r'\b(passing marks|total marks|obtained marks|max marks|minimum marks)\b',
    r'\b(subject code|course code|course title|credit|fail|pass|absent)\b',
    r'\b(controller of examination|registrar|academic affairs)\b',
    # Invoices / receipts
    r'\b(invoice|bill|receipt|payment due|amount due|tax|gst|vat|subtotal)\b',
    r'\b(pay to|payable|bank account|iban|swift|payment terms)\b',
    # Contracts / agreements
    r'\b(agreement|contract|whereas|hereinafter|party of the first|indemnify|liability)\b',
    r'\b(clause|section \d|article \d|schedule [a-z]|annexure)\b',
    # News / articles
    r'\b(according to|reported|announced|government|minister|billion|million rupees)\b',
    r'\b(published|editor|journalist|correspondent|bureau)\b',
    # Recipes
    r'\b(ingredient|tablespoon|teaspoon|cup of|bake|boil|fry|cook for|preheat|oven)\b',
    # Manuals / documentation
    r'\b(installation|getting started|how to use|user manual|chapter \d|warranty)\b',
    r'\b(endpoint|payload|request body|response|api documentation|swagger)\b',
    # Business proposals / reports
    r'\b(executive summary|market opportunity|use of funds|roi|profit margin)\b',
    r'\b(revenue forecast|break even|investment return|valuation)\b',
    # Assignment / academic report
    r'\b(literature review|methodology|hypothesis|research question|conclusion of study)\b',
    r'\b(references cited|bibliography|ibid|et al|doi|isbn)\b',
    # Cover letter
    r'\b(dear hiring manager|dear sir|to whom it may concern|i am writing to apply)\b',
    r'\b(please find attached|looking forward to hearing|sincerely yours)\b',
    # GitHub README / tech docs
    r'\b(installation|npm install|pip install|clone the repo|pull request|fork)\b',
    r'\b(getting started|prerequisites|usage|contributing|license|mit license)\b',
]

CONTACT_PATTERN = re.compile(
    r'(\+\d{1,3}[\s\-]?\d{3,5}[\s\-]?\d{4,10}|'   # phone
    r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b|'  # email
    r'linkedin\.com/in/|github\.com/)',              # linkedin / github
    re.IGNORECASE
)

TECH_SKILL_PATTERN = re.compile(
    r'\b(python|javascript|typescript|react|node|angular|vue|java|kotlin|swift|'
    r'flutter|dart|django|fastapi|flask|express|spring|docker|kubernetes|aws|azure|gcp|'
    r'postgresql|mongodb|mysql|redis|git|html|css|tensorflow|pytorch|scikit|linux|bash|'
    r'c\+\+|c#|php|ruby|go|rust|scala|r programming|matlab|figma|xcode|android studio)\b',
    re.IGNORECASE
)

def extract_structural_features(texts):
    """
    Extract hand-crafted features that capture resume STRUCTURE.
    Returns a 2D numpy array of features for each document.
    """
    features = []
    for text in texts:
        text_lower = text.lower()
        feat = []

        # Feature 1: How many resume section headers are present? (0-10)
        section_count = sum(
            1 for pat in RESUME_SECTION_PATTERNS
            if re.search(pat, text_lower)
        )
        feat.append(section_count)

        # Feature 2: Ratio of resume sections to total (0.0 - 1.0)
        feat.append(section_count / len(RESUME_SECTION_PATTERNS))

        # Feature 3: How many non-resume patterns are present? (0-N)
        non_resume_count = sum(
            1 for pat in NON_RESUME_PATTERNS
            if re.search(pat, text_lower)
        )
        feat.append(non_resume_count)

        # Feature 4: Contact info present? (0 or 1)
        has_contact = 1 if CONTACT_PATTERN.search(text) else 0
        feat.append(has_contact)

        # Feature 5: Tech skill count (0-N)
        tech_skills = len(set(TECH_SKILL_PATTERN.findall(text_lower)))
        feat.append(tech_skills)

        # Feature 6: Has skills AND experience together? (key signal)
        has_skills = 1 if re.search(r'\b(skills?|technical skills?)\b', text_lower) else 0
        has_experience = 1 if re.search(r'\b(experience|work history|employment)\b', text_lower) else 0
        feat.append(has_skills * has_experience)  # 1 only if BOTH present

        # Feature 7: Has education section? (0 or 1)
        has_education = 1 if re.search(r'\b(education|degree|university|bachelor|master|bscs|bsit|bsee)\b', text_lower) else 0
        feat.append(has_education)

        # Feature 8: Resume structure score (skills + experience + education + contact)
        resume_score = has_skills + has_experience + has_education + has_contact
        feat.append(resume_score)

        # Feature 9: Strong non-resume signal (invoice/roll slip/result card)
        strong_non_resume = 1 if non_resume_count >= 3 else 0
        feat.append(strong_non_resume)

        # Feature 10: Document length (short docs unlikely to be resumes)
        word_count = len(text.split())
        feat.append(min(word_count / 200, 1.0))  # normalize to 0-1

        # Feature 11: Has CGPA/GPA score pattern (common in result cards too)
        # Disambiguate: result cards have ONLY cgpa, resumes mention it in education
        has_cgpa = 1 if re.search(r'\b(cgpa|gpa|grade point)\b', text_lower) else 0
        feat.append(has_cgpa)

        # Feature 12: Exam-specific patterns (strong roll-slip signal)
        has_exam_patterns = 1 if re.search(
            r'\b(roll no|seat no|admit card|exam center|date sheet|invigila|theory paper|practical exam)\b',
            text_lower
        ) else 0
        feat.append(has_exam_patterns)

        # Feature 13: Result card specific (marks, grades)
        has_result_patterns = 1 if re.search(
            r'\b(obtained marks|total marks|credit hours|letter grade|grade [a-f]\+?|pass|fail)\b',
            text_lower
        ) else 0
        feat.append(has_result_patterns)

        # Feature 14: Has name-like pattern at top (common in resumes)
        first_200 = text[:200]
        lines = [l.strip() for l in first_200.split('\n') if l.strip()]
        top_line_short = 1 if lines and 2 <= len(lines[0].split()) <= 5 else 0
        feat.append(top_line_short)

        # Feature 15: Final discriminator — resume score minus non-resume score
        feat.append(resume_score - min(non_resume_count, 4))

        features.append(feat)

    return np.array(features, dtype=float)


# ═══════════════════════════════════════════════════════════════════════════
# TRAINING DATA
# ═══════════════════════════════════════════════════════════════════════════

resume_samples = [
"""Muhammad Umair Rasheed
Software Engineer
umair@email.com | +92-300-1234567
github.com/umair | linkedin.com/in/umair
Bachelor of Information Technology — KFUEIT — 2022-2026
Skills:
Python, FastAPI, React.js, PostgreSQL, Docker, Git
Experience:
Software Intern — Tech Company — 2024
Built REST APIs using FastAPI and PostgreSQL.
Integrated frontend with React.js.
Projects:
Career-Forge — AI-powered skill gap analyzer.
""",

"""Ali Raza
Backend Developer
Email: ali.raza@gmail.com | Phone: 0321-1234567
Education: BSCS — COMSATS University — 2019-2023
Experience:
Backend Developer at Startup ABC, 2023-Present
Worked with Django and FastAPI.
Designed authentication systems using JWT.
Built scalable APIs with PostgreSQL.
Technical Skills:
Python, Docker, Redis, Linux, Git, PostgreSQL
Projects:
Online Shopping Platform, Blog REST API
""",

"""Sara Ahmed
Machine Learning Engineer | sara@email.com
MSc Data Science — IBA Karachi — 2020-2022
Experience:
ML Engineer at Data Solutions (2022-Present)
Built NLP models using transformers.
Worked with TensorFlow and PyTorch.
Deployed ML pipelines on AWS.
Skills:
Python, TensorFlow, PyTorch, NLP, Docker, scikit-learn
Certifications:
DeepLearning.AI Specialization
""",

"""John Smith | Full Stack Developer
john.smith@gmail.com | linkedin.com/in/johnsmith
Education:
BSc Computer Science — University of London — 2018-2022
Technical Skills:
Frontend: React.js, TypeScript, HTML5, CSS3, Tailwind CSS
Backend: Node.js, Express, Python, FastAPI
Databases: PostgreSQL, MongoDB, Redis
Experience:
Senior Frontend Developer - ABC Corp, 2022-Present
Improved page load time by 40% using lazy loading.
Projects:
E-Commerce Platform, Real-time Chat Application
""",

"""CURRICULUM VITAE
Fatima Noor — Frontend Developer
fatima.noor@email.com | +92-311-9876543
Objective: Seeking a frontend developer position.
Education:
BS Software Engineering — FAST University — 2019-2023 — CGPA: 3.4
Skills:
HTML, CSS, JavaScript, React, Redux, Git, Figma
Experience:
Frontend Intern — XYZ Company — Summer 2022
Built reusable UI components using React.js.
Projects:
E-commerce website, Admin dashboard, Portfolio site
References available upon request.
""",

"""Hamza Ali | Software Engineer
hamza@email.com | github.com/hamzaali
Career Objective: To contribute to innovative software solutions.
Education:
BSIT — KFUEIT — 2020-2024
Technical Skills:
Python, PostgreSQL, Docker, AWS, Linux, Git, FastAPI
Experience:
Backend Developer — Tech Startup — 2024
Developed REST APIs and implemented JWT authentication.
Optimized database queries improving performance by 30%.
Certification:
AWS Certified Developer
Projects: Inventory Management System, Task Tracker API
""",

"""Ayesha Khan — UI/UX Designer
ayesha@design.com | Portfolio: ayesha.design
Education:
BDes Visual Communication — Indus Valley School — 2018-2022
Skills:
Figma, Adobe XD, Sketch, Prototyping, Wireframing
HTML, CSS (basic), User Research, Usability Testing
Experience:
Senior Product Designer — DesignHub — 2022-Present
Redesigned mobile app increasing retention by 35%.
Conducted 50+ user interviews.
Projects:
Banking App Redesign, Healthcare Dashboard, E-Commerce UI
""",

"""Bilal Hassan — DevOps Engineer
bilal.hassan@email.com
Education: BE Software Engineering — NED University — 2015-2019
Skills:
AWS, Kubernetes, Terraform, Jenkins, Docker, Ansible, Linux, Bash, Git
Experience:
Senior DevOps Engineer — Cloud Systems — 2021-Present
Managed deployment pipelines for 50+ microservices.
Reduced deployment failures by 35%.
Certifications:
AWS Solutions Architect Professional
Certified Kubernetes Administrator (CKA)
""",

"""Usman Tariq — Python Developer
usman@email.com | github.com/usmandev
Education:
BS Computer Science — COMSATS Islamabad — 2019-2023
Technical Skills:
Django, FastAPI, PostgreSQL, Redis, Docker, Git, Linux, Python
Experience:
Backend Developer at Startup ABC — 2023-Present
Designed RESTful APIs and database schemas.
Implemented caching with Redis reducing load by 40%.
Projects:
URL Shortener Service, E-Learning API, Authentication Microservice
""",

"""Zainab Raza — Cybersecurity Engineer
zainab@security.com
Education:
BS Information Security — Air University — 2017-2021
Skills:
Penetration Testing, Wireshark, Metasploit, Burp Suite, Kali Linux
Python, Bash, Networking, OWASP, Nessus
Certifications:
CEH — Certified Ethical Hacker
CompTIA Security+
Experience:
Security Analyst — CyberSec Firm — 2021-2024
Conducted 100+ penetration tests for enterprise clients.
References: Available upon request
""",

"""Ahmed Khan — Android Developer
ahmed.khan@email.com | +92-333-5678901
Objective: Seeking Android developer position.
Education:
BSCS — FAST NUCES — 2019-2023 — GPA: 3.2/4.0
Technical Skills:
Kotlin, Java, Android, Android Studio, Firebase, Retrofit, Git
Room Database, Coroutines, MVVM Architecture
Experience:
Mobile App Intern — Mobile Solutions — Summer 2022
Developed 3 Android apps published on Play Store.
Integrated REST APIs and Firebase authentication.
Projects:
E-Commerce App (1000+ downloads), Task Manager App
Languages: English (Fluent), Urdu (Native)
""",

"""Mariam Siddiqui
Data Analyst | mariam@data.com
Education:
BS Statistics — Karachi University — 2018-2022
Skills:
Python, R, SQL, Pandas, NumPy, Tableau, Power BI
Matplotlib, Seaborn, Excel, PostgreSQL
Experience:
Data Analyst — Analytics Corp — 2022-Present
Analyzed datasets of 1M+ records.
Built interactive dashboards reducing reporting time by 50%.
Projects:
Sales Forecasting Model, Customer Segmentation Analysis
Certifications:
Google Data Analytics Certificate
IBM Data Science Professional Certificate
""",

    """RESUME - Iqra Hassan
    Email: iqra.hassan@email.com | Phone: 0321-9876543
    OBJECTIVE: Seeking Quality Assurance Engineer position
    EDUCATION
    Bachelor of Science in Computer Science - Bahria University - 2020-2024 - CGPA 3.6
    TECHNICAL SKILLS
    Testing Tools: Selenium, TestNG, Jira, Postman, LoadRunner
    Languages: Java, Python, SQL
    Testing Types: Manual Testing, Automation Testing, API Testing, Performance Testing
    WORK EXPERIENCE
    QA Engineer - Software Company - 2023-Present
    - Executed test cases for web and mobile applications
    - Automated 200+ test scripts using Selenium
    - Reported and tracked 500+ bugs in Jira
    - Improved test coverage by 35%
    CERTIFICATIONS
    ISTQB Certified Tester
    Selenium Master Course""",

    """Hassan Khan | Solutions Architect
    LinkedIn: linkedin.com/in/hassankhan | GitHub: github.com/hkhan
    PROFESSIONAL SUMMARY
    Solutions Architect with 7 years designing scalable cloud infrastructure.
    Expertise in AWS, microservices, and system design.
    EDUCATION
    Master of Computer Science - LUMS - 2018-2020
    Bachelor of Science in Computer Science - FAST - 2014-2018
    CORE COMPETENCIES
    Cloud Platforms: AWS (EC2, S3, Lambda, RDS), Azure, Google Cloud
    Architecture: Microservices, Serverless, High Availability, Disaster Recovery
    Languages: Python, Java, Go, JavaScript
    DevOps Tools: Docker, Kubernetes, Terraform, Jenkins, GitLab CI/CD
    Databases: PostgreSQL, MongoDB, DynamoDB, Redis
    PROFESSIONAL EXPERIENCE
    Lead Solutions Architect - Cloud Systems Inc - 2021-Present
    Designed and deployed microservices architecture for 500K users
    Implemented multi-region AWS infrastructure with 99.99% uptime
    Solutions Architect - Tech Solutions - 2018-2021
    Designed solutions for 20+ enterprise clients
    ACHIEVEMENTS
    AWS Solutions Architect Professional Certification
    Published 5 articles on cloud architecture in IEEE
    Speaker at PyCon Pakistan 2023""",

    """Dr. Aisha Khan
    Professor of Computer Science | aisha.khan@university.edu
    EDUCATION
    Ph.D. in Computer Science - Stanford University - 2015
    Dissertation: Machine Learning for Natural Language Processing
    M.Sc. in Computer Science - University of Cambridge - 2011
    B.S. in Computer Science - FAST NUCES - 2009
    ACADEMIC POSITIONS
    Assistant Professor - XYZ University - 2022-Present
    Teaching: Data Science, Machine Learning, NLP
    Lecturer - ABC University - 2018-2022
    RESEARCH INTERESTS
    Natural Language Processing, Deep Learning, Transformers
    Computer Vision, Knowledge Graphs
    PUBLICATIONS
    Published 15+ papers in top-tier conferences (NeurIPS, ICML, ACL)
    Research Impact: 500+ citations
    PROJECTS & GRANTS
    Principal Investigator - NLP Research Grant ($500K) - 2023
    AI for Healthcare Initiative - Collaborative Research
    TECHNICAL SKILLS
    Python, PyTorch, TensorFlow, Hugging Face, CUDA, C++
    AWS SageMaker, Google Colab, Jupyter""",

    """Fatima Ali - UX/UI Designer
    Portfolio: fatima-design.com | Dribbble: dribbble.com/fatimaali
    Email: fatima@design.studio | +92-300-1234567
    PROFESSIONAL SUMMARY
    Creative UX/UI Designer with 4 years designing digital products used by 500K+ users.
    Specialized in mobile apps and web interfaces.
    EDUCATION
    BDes Interaction Design - Indus Valley School - 2019-2023
    Diploma in Graphic Design - NUFS - 2017-2019
    DESIGN EXPERTISE
    Tools: Figma, Adobe XD, Sketch, Illustrator, Photoshop, Protopie
    Skills: User Research, Wireframing, Prototyping, Design Systems, Usability Testing
    Web: HTML, CSS, Responsive Design, Web Accessibility (WCAG)
    PROFESSIONAL EXPERIENCE
    Senior UX Designer - FinTech Startup - 2022-Present
    Led design system from 0 to 500+ components
    Redesigned mobile banking app - 45% increase in user retention
    Conducted 200+ user interviews
    UX Designer - Digital Agency - 2020-2022
    Designed 30+ digital products for international clients
    NOTABLE PROJECTS
    Banking App Redesign, E-Commerce Platform, Health & Fitness App, SaaS Dashboard
    AWARDS
    Awwwards Honorable Mention - Best UX Design 2023
    Designer of the Month - Dribbble - March 2023""",

    """Muhammad Akram
    Full Stack Engineer
    Location: Lahore, Pakistan | Email: akram@dev.com | Phone: +92-345-0000000
    OBJECTIVE
    Experienced Full Stack Engineer seeking Senior Developer role to lead technical initiatives.
    EDUCATION & CERTIFICATIONS
    BS Computer Science - COMSATS - 2016-2020 - CGPA: 3.5
    AWS Developer Associate Certification - 2023
    Docker & Kubernetes Course - Udemy - 2022
    TECH STACK
    Frontend: React, Vue.js, Next.js, TypeScript, TailwindCSS, Redux
    Backend: Node.js, Express, Python, Django, FastAPI, REST APIs, GraphQL
    Mobile: React Native, Flutter
    Databases: PostgreSQL, MongoDB, MySQL, Firebase, Redis
    DevOps: Docker, Kubernetes, GitHub Actions, CircleCI, AWS (EC2, S3, Lambda)
    WORK EXPERIENCE
    Senior Full Stack Developer - Tech Startup - 2022-Present
    Led team of 5 developers
    Built microservices architecture serving 100K+ requests/day
    Implemented CI/CD pipelines reducing deployment time by 60%
    Full Stack Developer - Web Agency - 2020-2022
    Developed 25+ web applications for startup clients
    Managed 50+ GitHub repositories
    OPEN SOURCE CONTRIBUTIONS
    Contributed to React, Vue.js, and Webpack projects
    300+ GitHub stars on personal projects
    PROJECTS
    E-commerce Platform (Next.js, Node.js, PostgreSQL, Stripe)
    Real-time Chat Application (Socket.io, React, MongoDB)
    Task Management SaaS (React, FastAPI, PostgreSQL)""",

    """Zara Malik - Product Manager
    Product Management Professional | Email: zara.malik@product.com
    LinkedIn: linkedin.com/in/zaramalik | +92-321-1111111
    PROFESSIONAL SUMMARY
    Product Manager with 5 years building products from 0 to 1M users.
    Track record of launching features that increased revenue by 40%.
    EDUCATION
    MBA in Product Management - IBA - 2021-2023
    BS Computer Science - FAST NUCES - 2016-2020
    PRODUCT MANAGEMENT EXPERIENCE
    Senior Product Manager - Fintech Company - 2023-Present
    Led roadmap for payments platform serving 500K users
    Increased user engagement by 35% through feature A/B testing
    Shipped 15+ features, all with positive ROI
    Product Manager - E-Commerce Platform - 2021-2023
    Managed mobile app product achieving 4.8 star rating
    Reduced cart abandonment from 68% to 42%
    Conducted 100+ user interviews
    Associate Product Manager - Tech Startup - 2020-2021
    CORE COMPETENCIES
    Product Strategy & Roadmap, Market Research, User Research, A/B Testing
    Data Analytics, SQL, Tableau, Product-Market Fit, Competitive Analysis
    TOOLS & FRAMEWORKS
    JIRA, Figma, Mixpanel, Amplitude, Google Analytics, SQL
    Jobs to be Done, Lean Canvas, OKRs
    ACHIEVEMENTS
    Featured in Product Hunt's Top Makers 2023
    Speaker at Pakistan Product Summit 2023
    Mentoring 5 junior PMs at local startup""",
]

non_resume_samples = [

# ── ROLL NUMBER SLIPS ─────────────────────────────────────────────────────
"""KHWAJA FAREED UNIVERSITY OF ENGINEERING AND INFORMATION TECHNOLOGY
DEPARTMENT OF INFORMATION TECHNOLOGY

ADMIT CARD / ROLL NUMBER SLIP
FINAL TERM EXAMINATION — SPRING 2024

Student Name: Muhammad Umair Rasheed
Registration Number: INFT221101084
Roll Number: 2024-IT-084
Program: BSIT — 6th Semester
Section: A

Examination Schedule:
Subject: Database Systems | Date: June 10 | Time: 9:00 AM | Room: F-201
Subject: Software Engineering | Date: June 12 | Time: 9:00 AM | Room: F-201
Subject: Operating Systems | Date: June 14 | Time: 2:00 PM | Room: F-203

Instructions:
Students must bring this admit card to the examination hall.
Mobile phones are strictly prohibited in the examination center.
No student will be allowed entry after 15 minutes of commencement.

Controller of Examinations
KFUEIT, Rahim Yar Khan
""",

"""UNIVERSITY OF LAHORE
ADMIT CARD — MID TERM EXAMINATION

Student: Ali Hassan | Reg: 2021-CS-101
Program: BSCS | Semester: 4th
Session: Fall 2023

Exam Timetable:
Data Structures — Nov 5 — 10:00 AM — Hall B
Computer Networks — Nov 7 — 2:00 PM — Hall A
Theory of Automata — Nov 9 — 10:00 AM — Hall C

Exam Center: Main Campus, Block B
Seat No: 45

Rules:
Carry university ID along with this slip.
No mobile phones or electronic devices allowed.
Report 30 minutes before exam commencement.

Signature of Controller of Examinations
""",

# ── RESULT CARDS / TRANSCRIPTS ────────────────────────────────────────────
"""KFUEIT RAHIM YAR KHAN
SEMESTER RESULT CARD

Student Name: Fatima Khan
Registration No: INFT211101056
Program: BSIT | Semester: 5th | Session: 2021-2025

Result Detail:
Course Code  Course Title                    Credit Hrs  Grade  Grade Points
IT-501       Software Engineering            3           A      4.0
IT-502       Database Management Systems     3           B+     3.5
IT-503       Computer Networks               3           A-     3.7
IT-504       Web Technologies                3           B      3.0
IT-505       Professional Ethics             2           A      4.0

Total Credit Hours: 14
Credit Hours Obtained: 14
Semester GPA: 3.64
Cumulative GPA: 3.52

Status: PASS
Issued by: Controller of Examinations
""",

"""TRANSCRIPT OF ACADEMIC RECORD

University: COMSATS University Islamabad
Student: Sara Ali | Reg No: FA19-BCS-056
Degree: BS Computer Science | Duration: 2019-2023

Semester 1:
Programming Fundamentals — 3 Cr — A — 4.0
Calculus — 3 Cr — B+ — 3.5
Islamic Studies — 2 Cr — A — 4.0
Semester GPA: 3.7

Semester 2:
Object Oriented Programming — 3 Cr — A — 4.0
Linear Algebra — 3 Cr — B — 3.0
Semester GPA: 3.5

Cumulative CGPA: 3.6 / 4.0
Total Credit Hours: 136
Status: Degree Awarded

Registrar Signature: _______________
""",

# ── COVER LETTERS ─────────────────────────────────────────────────────────
"""Dear Hiring Manager,

I am writing to apply for the Backend Developer position advertised on your website.

I have experience working with Python, FastAPI, and PostgreSQL. I am passionate about
building scalable backend systems and have worked on REST API development.

I would welcome the opportunity to discuss how my background aligns with your team's needs.

Please find my resume attached separately.

Thank you for your consideration.

Sincerely,
Ali Raza
""",

"""To Whom It May Concern,

I am excited to submit my application for the Frontend Developer role at your company.

My experience with React.js and TypeScript makes me a strong candidate.
I have built multiple production-grade web applications in my previous role.

I look forward to hearing from you.

Best regards,
Fatima Noor
""",

# ── INVOICES ──────────────────────────────────────────────────────────────
"""INVOICE
Invoice No: INV-2025-1001
Date: January 15, 2025

Billed To:
ABC Company Ltd
123 Business Street, Lahore

Description                          Qty    Rate        Amount
Web Development Services              1     PKR 50,000   PKR 50,000
Backend API Development               1     PKR 70,000   PKR 70,000
Monthly Maintenance (3 months)        3     PKR 10,000   PKR 30,000

Subtotal: PKR 150,000
GST (17%): PKR 25,500
Total Due: PKR 175,500

Payment Terms: Net 30 Days
Bank: Meezan Bank | Account: 01234567890
""",

# ── GITHUB README ─────────────────────────────────────────────────────────
"""# Career-Forge

AI-powered skill gap analyzer built with FastAPI and React.js.

## Features
- Resume parsing using NLP
- Skill gap analysis
- Learning roadmap generation
- Course recommendations

## Tech Stack
- Backend: FastAPI, Python, PostgreSQL, MongoDB
- Frontend: React.js, Tailwind CSS
- AI: spaCy, Sentence-BERT, Q-Learning

## Installation

```bash
git clone https://github.com/user/career-forge
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Contributing
Pull requests are welcome. Fork the repository and submit a PR.

## License
MIT License
""",

# ── API DOCUMENTATION ─────────────────────────────────────────────────────
"""API DOCUMENTATION — Career-Forge REST API

Base URL: http://localhost:8000

Authentication Endpoints:

POST /auth/register
Payload: { "full_name": "string", "email": "string", "password": "string" }
Response: { "access_token": "JWT_TOKEN", "user": {...} }

POST /auth/login
Payload: { "email": "string", "password": "string" }
Response: { "access_token": "JWT_TOKEN" }

Resume Endpoints:

POST /resume/upload
Headers: Authorization: Bearer TOKEN
Body: multipart/form-data with file field
Response: { "skills": [...], "education": [...] }

GET /resume/my-resume
Returns the latest parsed resume for current user.
""",

# ── ASSIGNMENT / ACADEMIC REPORT ──────────────────────────────────────────
"""ASSIGNMENT REPORT

Course: Software Engineering (CS-401)
Topic: Analysis of Agile Methodology
Submitted by: Roll No 2021-CS-101

Introduction:
Agile development is an iterative approach to software delivery. The Agile Manifesto
introduced four core values emphasizing individuals over processes.

Literature Review:
Beck et al. (2001) introduced the Agile Manifesto with 12 guiding principles.
Studies show Agile projects have 28% higher success rates than waterfall projects.

Methodology:
This report uses a comparative analysis methodology examining 10 published studies.

Conclusion:
Agile improves team productivity. Future research should examine AI-assisted Agile.

References:
Beck, K. et al. (2001). Agile Manifesto. agilemanifesto.org
""",

# ── BUSINESS PROPOSAL ─────────────────────────────────────────────────────
"""BUSINESS PROPOSAL

Submitted to: ABC Investment Group
From: XYZ Tech Startup
Date: March 2025

Executive Summary:
Seeking PKR 50 million in Series A funding for e-commerce platform expansion.

Market Opportunity:
Pakistan e-commerce market valued at $6 billion growing at 30% annually.

Financial Forecast:
Year 1 Revenue: PKR 20M
Year 2 Revenue: PKR 50M
Year 3 Revenue: PKR 120M

Use of Funds:
40% Technology | 35% Marketing | 25% Operations

ROI Projection:
Investors can expect 3x return within 4 years based on current growth trajectory.
Break-even expected in Month 18.
""",

# ── NEWS ARTICLE ──────────────────────────────────────────────────────────
"""Pakistan IT Exports Hit Record $2.6 Billion

ISLAMABAD — Pakistan's technology sector recorded record exports this year,
according to the Pakistan Software Export Board.

The Minister of IT and Telecom announced new incentives for software companies
including tax exemptions valid for five years.

The startup ecosystem saw significant growth with 500+ new technology companies
registered this fiscal year. Foreign investment increased by 40%.

Several multinational corporations have announced plans to set up development
centers in Lahore, Karachi, and Islamabad, creating thousands of jobs.

Reported by: Tech Correspondent | Dawn News
""",

# ── RECIPE ────────────────────────────────────────────────────────────────
"""Chicken Biryani Recipe — Serves 6

Ingredients:
1 kg basmati rice, 1.5 kg chicken, 3 onions, yogurt
Biryani masala, turmeric, red chili powder, saffron

Instructions:
1. Marinate chicken with yogurt and spices for 2 hours
2. Fry onions until golden brown and crispy
3. Cook chicken on medium heat for 20 minutes
4. Parboil rice until 70% cooked then drain water
5. Layer rice over chicken and add saffron milk
6. Cover and cook on low flame for 25 minutes (dum)

Total Cook Time: 90 minutes
Calories per serving: approximately 650 kcal
""",

# ── SERVICE AGREEMENT ─────────────────────────────────────────────────────
"""SERVICE AGREEMENT

This agreement is entered as of January 1, 2025 between:
Service Provider: Tech Solutions Pvt Ltd
Client: ABC Company Ltd

1. SCOPE OF SERVICES
Service Provider shall provide software development services as detailed in Schedule A.

2. PAYMENT TERMS
Client shall pay PKR 500,000 per month within 15 days of invoice date.

3. CONFIDENTIALITY
Both parties agree to maintain strict confidentiality of all proprietary information.

4. TERMINATION
Either party may terminate this agreement with 30 days written notice.

IN WITNESS WHEREOF the parties have signed below.
Service Provider Signature: _____________
Client Signature: _____________
""",

# ── TEAM PROFILE (looks like resume but is not) ───────────────────────────
"""TEAM MEMBER PROFILE — Company Website

Hamza Ali
Machine Learning Researcher

Current Role:
Research Engineer at AI Lab, Karachi

Research Interests:
Natural Language Processing, Computer Vision, Deep Learning

Publications:
IEEE Conference on AI 2023 — Best Paper Award
Journal of Machine Learning Research 2024

Contact for collaborations: hamza@ailab.com
""",

# ── FREELANCER PROFILE (similar to resume but not one) ───────────────────
"""FREELANCER PROFILE — Upwork

Sara Ahmed | Full Stack Developer
Top Rated Freelancer | 4.9/5 Rating

Services Offered:
MERN Stack Development
REST API Integration
Cloud Deployment on AWS

Completed Projects: 48
Total Earnings: $25,000+

Client Reviews:
"Excellent work, delivered on time" — Client USA
"Professional and skilled developer" — Client UK

Technologies: React.js, Node.js, MongoDB, Docker, AWS
""",

# ── ROADMAPS / LEARNING PATHS ─────────────────────────────────────────────
"""LEARNING ROADMAP — Web Development

Phase 1: Foundations (Weeks 1-4)
- HTML & CSS fundamentals
- JavaScript basics and DOM manipulation
- Git and version control

Phase 2: Frontend (Weeks 5-8)
- React.js fundamentals
- State management (Redux, Context API)
- Component architecture and hooks
- CSS frameworks (Tailwind, Bootstrap)

Phase 3: Backend (Weeks 9-12)
- Node.js and Express.js
- REST API design and development
- Database design (SQL and NoSQL)
- Authentication and authorization

Phase 4: Advanced (Weeks 13-16)
- Deployment and DevOps basics
- Testing (Unit, Integration, E2E)
- Performance optimization
- Security best practices

Resources:
- FreeCodeCamp YouTube Channel
- MDN Web Docs
- Official Framework Documentation
- LeetCode for practice

Estimated Time: 4-6 months of consistent study
""",

"""AI/ML ENGINEERING ROADMAP

Foundation Phase:
- Python programming
- Linear algebra and calculus
- Statistics and probability

Core ML Phase:
- Supervised learning (regression, classification)
- Unsupervised learning (clustering, dimensionality reduction)
- Model evaluation and cross-validation
- Feature engineering

Deep Learning Phase:
- Neural networks and backpropagation
- CNNs for computer vision
- RNNs and Transformers for NLP
- Attention mechanisms

Advanced Topics:
- Reinforcement learning
- Generative models (VAE, GAN)
- Transfer learning
- Model deployment and MLOps

Tools & Libraries:
- TensorFlow / PyTorch
- Scikit-learn, Pandas, NumPy
- Jupyter Notebooks
- AWS SageMaker

Project Timeline: 12-18 months
""",

"""FULL STACK DEVELOPMENT ROADMAP 2025

Quarter 1: Frontend Mastery
Month 1: Advanced React (Hooks, Context, Performance)
Month 2: TypeScript and Testing (Jest, React Testing Library)
Month 3: State Management Deep Dive (Redux, Zustand)

Quarter 2: Backend Development
Month 4: Node.js & Express fundamentals
Month 5: Database design and optimization (PostgreSQL, MongoDB)
Month 6: API design and microservices

Quarter 3: DevOps & Deployment
Month 7: Docker and containerization
Month 8: Kubernetes basics and orchestration
Month 9: CI/CD pipelines (GitHub Actions, Jenkins)

Quarter 4: Advanced Topics
Month 10: System design and scalability
Month 11: Security practices and best practices
Month 12: Performance optimization and monitoring

Key Skills:
- React, Vue, or Angular
- Node.js, Django, or FastAPI
- PostgreSQL or MongoDB
- Docker & Kubernetes
- AWS or Google Cloud
- Testing and monitoring

Expected Outcome: Senior Full Stack Developer
""",
]


# ═══════════════════════════════════════════════════════════════════════════
# SIMPLE PIPELINE - TF-IDF + LOGISTIC REGRESSION
# ═══════════════════════════════════════════════════════════════════════════

from sklearn.preprocessing import StandardScaler

# Simple pipeline without custom classes
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 3),
        stop_words='english',
        min_df=1,
        sublinear_tf=True
    )),
    ('clf', LogisticRegression(
        C=1.0,  # Standard regularization
        max_iter=1000,
        random_state=42,
        solver='lbfgs'  # Better convergence
    ))
])

# ═══════════════════════════════════════════════════════════════════════════
# TRAIN
# ═══════════════════════════════════════════════════════════════════════════

print("Preparing training data...")
texts  = resume_samples + non_resume_samples
labels = [1] * len(resume_samples) + [0] * len(non_resume_samples)
print(f"Samples: {len(resume_samples)} resumes + {len(non_resume_samples)} non-resumes")

# Cross-validation
print("\nRunning cross-validation...")
from sklearn.model_selection import cross_val_score

scores = cross_val_score(pipeline, texts, labels, cv=5, scoring='accuracy')
for i, score in enumerate(scores):
    print(f"  Fold {i+1}: {score:.2%}")

print(f"\nCross-validation accuracy: {scores.mean():.2%} (+/- {scores.std():.2%})")

# Train final model on all data
print("\nTraining final model on all data...")
pipeline.fit(texts, labels)

# Save model
model_path = os.path.join(os.path.dirname(__file__), 'resume_classifier.joblib')
joblib.dump(pipeline, model_path)
print(f"Model saved to: {model_path}")

# ═══════════════════════════════════════════════════════════════════════════
# TEST ON TRICKY EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════

print("\n" + "="*60)
print("EDGE CASE TESTS")
print("="*60)

edge_cases = [
    ("✓ RESUME", "Muhammad Umair — Python Developer — umair@email.com — Skills: Python, React, Docker — Experience: Backend Developer at XYZ — Education: BSIT KFUEIT 2022-2026 — Projects: E-commerce API"),
    ("✗ ROLL SLIP", "KFUEIT ADMIT CARD — Student: Ali Khan — Reg No: INFT2211 — Roll No: 2024-IT-084 — Exam: Database Systems — Date: June 10 — Room: F-201 — Seat No: 45 — Controller of Examinations"),
    ("✗ RESULT CARD", "SEMESTER RESULT CARD — KFUEIT — Student: Sara — CGPA: 3.5 — Course: Software Engineering — Credit Hours: 3 — Grade: A — Grade Points: 4.0 — Total Credit Hours: 15 — Status: PASS — Registrar"),
    ("✗ COVER LETTER", "Dear Hiring Manager, I am writing to apply for the Software Developer position. I have skills in Python and React. Please find my resume attached separately. Sincerely, Applicant"),
    ("✗ GITHUB README", "# MyProject Installation: npm install && npm run dev. Contributing: Fork the repo and submit a pull request. License: MIT. Tech Stack: React, Node.js, MongoDB."),
    ("✗ INVOICE", "INVOICE INV-2025-001 Web Development Services PKR 50000 Backend API Development PKR 70000 GST 17% Total Due PKR 140500 Payment Terms Net 30 Days Bank Account 1234567890"),
    ("✗ FREELANCER", "Upwork Freelancer Profile — Top Rated — 4.9/5 rating — Completed Projects: 48 — Services: MERN Stack Development, REST API Integration — Client Reviews: Excellent work delivered on time"),
    ("✓ MINIMAL RESUME", "Name: Ahmed — Email: ahmed@email.com — Skills: Python, Django, PostgreSQL — Education: BSCS FAST 2020-2024 — Experience: Software intern at ABC Company"),
    ("✗ TEAM PROFILE", "Team Member — Company Website — John Smith — Senior Engineer — Current Role: Tech Lead at Google — Research Interests: Distributed Systems — Contact for collaborations: john@google.com"),
    ("✗ ASSIGNMENT", "Assignment Report Course: Software Engineering Topic: Agile Methodology Introduction: Agile focuses on iterative delivery. Literature Review: Beck 2001. Conclusion: Agile improves productivity. References: Beck et al."),
]

all_correct = True
for expected_label, text in edge_cases:
    preds = pipeline.predict([text])
    probs = pipeline.predict_proba([text])
    pred_label = "Resume" if preds[0] == 1 else "Non-Resume"
    confidence = probs[0][preds[0]] * 100
    expected_is_resume = expected_label.startswith("✓")
    correct = (preds[0] == 1) == expected_is_resume
    status = "PASS" if correct else "FAIL"
    if not correct:
        all_correct = False
    print(f"  [{status}] {expected_label[:20]:22} → Predicted: {pred_label} ({confidence:.1f}%)")

print()
if all_correct:
    print("ALL EDGE CASES PASSED ✓")
else:
    print("Some edge cases failed — consider adding more training samples.")
print("="*60)