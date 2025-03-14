from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session
from database.db_handler import get_db
from database.model import Job
from typing import List, Dict, Optional
from scrapers.job_scraper import JobScraper
import logging
import datetime
router = APIRouter()

# Job response model
class JobResponse(Dict):
    id: str
    title: str
    company_id: str
    company_name: str
    location: str
    job_type: str
    description: str

@router.get("/jobs")
async def get_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated list of jobs"""
    try:
        
        logging.info(f"Fetching jobs with page={page}, limit={limit}")
        
        offset = (page - 1) * limit
        jobs_query = db.query(Job).offset(offset).limit(limit).all()
        
        logging.info(f"Query returned {len(jobs_query)} jobs")
        
        # Convert ORM objects to dictionaries - FIXED FIELD NAMES
        jobs = []
        for job in jobs_query:
            job_dict = {
                "id": str(job.id),
                "title": job.title,
                "location": job.location,
                "company_id": str(job.company_id),
                "experience": job.experience,  # FIXED: was experience_level
                "job_type": job.job_type,      # ADDED: required field
                "posted_by": job.posted_by,    # ADDED: required field
                "posted_date": str(job.posted_date) if job.posted_date else None  # FIXED: was posted_at
            }
            jobs.append(job_dict)
            
        return jobs
    except Exception as e:
        logging.error(f"Error fetching jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve jobs")

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)):
    """Get a specific job by ID"""
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
        
        # FIXED field names to match the model
        job_dict = {
            "id": str(job.id),
            "title": job.title,
            "location": job.location,
            "company_id": str(job.company_id),
            "experience": job.experience,  # FIXED: was experience_level
            "job_type": job.job_type,      # ADDED
            "posted_by": job.posted_by,    # ADDED
            "posted_date": str(job.posted_date) if job.posted_date else None # FIXED: was posted_at
        }
        return job_dict
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch job")

@router.post("/jobs/scrape")
async def scrape_jobs(
    background_tasks: BackgroundTasks,
    search_query: str = "software engineer",
    location: str = "United States",
    limit: int = Query(10, ge=1, le=50)
):
    """Trigger LinkedIn job scraping with database storage"""
    try:
        # Start the scraping in a background task
        background_tasks.add_task(
            _scrape_and_store_jobs, 
            search_query=search_query,
            location=location,
            limit=limit
        )
        
        return {
            "status": "success",
            "message": f"Job scraping initiated for '{search_query}' in '{location}'",
            "limit": limit
        }
    except Exception as e:
        logging.error(f"Failed to start job scraping: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate job scraping")

# New background task function for scraping
async def _scrape_and_store_jobs(search_query: str, location: str, limit: int):
    """Background task to scrape and store jobs"""
    try:
        scraper = JobScraper()
        jobs = scraper.scrape_jobs(search_query=search_query, location=location, limit=limit)
        
        if not jobs:
            logging.warning("Scraper returned no jobs")
            return
            
        # Store each job in the database
        stored_count = 0
        for job in jobs:
            try:
                # Prepare job data with correct field names matching your model
                job_data = {
                    "title": job.get("title", "Unknown Position"),
                    "location": job.get("location", "Unknown Location"),
                    "company_id": job.get("company_id", 1),
                    "experience": job.get("experience", "Not specified"),
                    "job_type": job.get("job_type", "Full-time"),  # Required field
                    "posted_by": job.get("posted_by", "LinkedIn"),  # Required field
                    "posted_date": job.get("posted_date", datetime.datetime.now())  # Correct field name
                }
                
                # Store in database
                db = next(get_db())
                db_job = Job(**job_data)
                db.add(db_job)
                db.commit()
                stored_count += 1
                
            except Exception as e:
                logging.error(f"Error storing job: {str(e)}")
                continue
                
        logging.info(f"Successfully stored {stored_count} jobs in database")
        
    except Exception as e:
        logging.error(f"Background job scraping failed: {str(e)}")