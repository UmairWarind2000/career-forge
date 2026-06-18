from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from core.database import engine, Base
from core.mongodb import create_indexes
from models import user
from routers import auth, resume, jobs, gap, roadmap, courses, live_jobs, profile
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SkillGap AI...")
    Base.metadata.create_all(bind=engine)
    await create_indexes()
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="Skill Gap Analyzer API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://career-forge.vercel.app",
        "https://career-forge-git-main-UmairWarind2000.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{round((time.time()-start)*1000,2)}ms"
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.include_router(auth.router)
app.include_router(resume.router)
app.include_router(jobs.router)
app.include_router(gap.router)
app.include_router(roadmap.router)
app.include_router(courses.router)
app.include_router(live_jobs.router)
app.include_router(profile.router)

@app.get("/")
def root():
    return {"message": "SkillGap AI API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}