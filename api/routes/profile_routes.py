from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session
from database.db_handler import get_db
from database.model import UserProfile
from typing import List, Dict, Optional
from scrapers.profile_scraper import ProfileScraper
import logging
import traceback

router = APIRouter()

@router.get("/profiles", response_model=List[Dict])
async def get_profiles(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated list of profiles"""
    try:
        offset = (page - 1) * limit
        profiles_query = db.query(UserProfile).offset(offset).limit(limit).all()
        
        # Convert ORM objects to dictionaries
        profiles = []
        for profile in profiles_query:
            profile_dict = {
                "id": str(profile.id),
                "name": profile.name,
                "company_id": str(profile.company_id) if profile.company_id else None,
                "position": profile.position,
                "experience": profile.experience,
                "location": profile.location,
                "email": profile.email,
                "phone": profile.phone,
                "skills": profile.skills
            }
            profiles.append(profile_dict)
            
        return profiles
    except Exception as e:
        logging.error(f"Error fetching profiles: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profiles")

@router.get("/profiles/{profile_id}")
async def get_profile(profile_id: str, db: Session = Depends(get_db)):
    """Get a specific profile by ID"""
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
            
        # Convert ORM object to dictionary
        profile_dict = {
            "id": str(profile.id),
            "name": profile.name,
            "company_id": str(profile.company_id) if profile.company_id else None,
            "position": profile.position,
            "experience": profile.experience,
            "location": profile.location,
            "email": profile.email,
            "phone": profile.phone,
            "skills": profile.skills
        }
        return profile_dict
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")

@router.post("/profiles/scrape")
async def scrape_profile(
    background_tasks: BackgroundTasks,
    url: str
):
    """Trigger LinkedIn profile scraping"""
    try:
        if not url or not url.startswith("https://www.linkedin.com/in/"):
            raise HTTPException(status_code=400, detail="Invalid LinkedIn profile URL")
        
        # Start scraping in background to prevent timeout
        background_tasks.add_task(_scrape_profile_task, url)
        return {
            "status": "success",
            "message": "Profile scraping initiated",
            "url": url
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error initiating profile scrape: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate profile scraping")

# Background task for scraping
async def _scrape_profile_task(url: str):
    try:
        scraper = ProfileScraper()
        profile_data = scraper.scrape_profile(url)
        
        if not profile_data:
            logging.error("Failed to scrape profile data")
            return
        
        # Map scraped data to model fields
        db = next(get_db())
        
        # Create new UserProfile with existing fields only - REMOVED profile_url
        user_profile = UserProfile(
            name=profile_data.get('name', 'Unknown'),
            position=profile_data.get('position', profile_data.get('headline', None)),
            location=profile_data.get('location', None),
            company_id=1,  # Default company ID
            experience=profile_data.get('experience', None),
            skills=profile_data.get('skills', None) if isinstance(profile_data.get('skills'), str) 
                  else ','.join(profile_data.get('skills', [])),
            email=profile_data.get('email', None),
            phone=profile_data.get('phone', None)
            # REMOVED profile_url which doesn't exist in your model
        )
        
        db.add(user_profile)
        db.commit()
        
        logging.info(f"Successfully scraped and saved profile: {profile_data.get('name', 'Unknown')}")
    except Exception as e:
        logging.error(f"Background profile scraping failed: {str(e)}")