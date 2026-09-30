from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .core.database import engine, Base, get_db
from .models import models
from .schemas import schemas
from .services.credit_service import CreditService
from .services.research_service import ResearchService
import os

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI News Research & Content Generator")


# Create dummy user if not exists
def create_dummy_user():
    from .core.database import SessionLocal
    db = SessionLocal()
    try:
        if not db.query(models.User).first():
            dummy_user = models.User(username="test_user", balance=100)
            db.add(dummy_user)
            db.commit()
    finally:
        db.close()


create_dummy_user()

frontend_dir = os.path.join(os.path.dirname(__file__), "../../frontend")
exports_dir = os.path.join(os.path.dirname(__file__), "exports")
os.makedirs(exports_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static")
app.mount("/exports", StaticFiles(directory=exports_dir), name="exports")
templates = Jinja2Templates(directory=os.path.join(frontend_dir, "templates"))


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/credits/estimate", response_model=schemas.CreditEstimateResponse)
async def estimate_credits(content_type: str):
    credits = CreditService.get_estimate(content_type)
    return {"content_type": content_type, "estimated_credits": credits}


@app.post("/api/research/start", response_model=schemas.ResearchResponse)
def start_research(
    request: schemas.ResearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.username == "test_user").first()

    # 1. Create ResearchJob record
    job = models.ResearchJob(
        user_id=user.id,
        topic=request.topic,
        category=request.category,
        content_type=request.content_type,
        time_range=request.time_range,
        status="pending",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # 2. Reserve credits
    success = CreditService.reserve_credits(db, user.id, job.id, request.content_type)
    if not success:
        job.status = "failed"
        db.commit()
        raise HTTPException(status_code=402, detail="Insufficient credits")

    job.status = "searching"
    db.commit()

    # 3. Kick off background task
    background_tasks.add_task(ResearchService.process_research_job, job.id)

    return job


@app.get("/api/research/{job_id}/status", response_model=schemas.JobStatusResponse)
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    job = (
        db.query(models.ResearchJob)
        .filter(models.ResearchJob.id == job_id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    response = schemas.JobStatusResponse.model_validate(job)
    if job.pdf_path:
        response.pdf_url = job.pdf_path
        
    return response
