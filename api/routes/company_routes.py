from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from sqlalchemy.orm import Session
from database.db_handler import get_db
from database.model import Company
from typing import List, Dict, Optional
from scrapers.company_scraper import CompanyScraper
import logging

router = APIRouter()

@router.get("/companies", response_model=List[Dict])
async def get_companies(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated list of companies"""
    try:
        offset = (page - 1) * limit
        companies_query = db.query(Company).offset(offset).limit(limit).all()
        
        # Convert ORM objects to dictionaries
        companies = []
        for company in companies_query:
            company_dict = {
                "id": str(company.id),
                "name": company.name,
                "industry": company.industry,
                "size": company.size,
                "location": company.headquarters,
                "founded": company.founded,
                "website": company.website if hasattr(company, 'website') else None
            }
            companies.append(company_dict)
            
        return companies
    except Exception as e:
        logging.error(f"Error fetching companies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve companies")

@router.get("/companies/{company_id}")
async def get_company(company_id: str, db: Session = Depends(get_db)):
    """Get a specific company by ID"""
    try:
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
            
        # Convert ORM object to dictionary
        company_dict = {
            "id": str(company.id),
            "name": company.name,
            "industry": company.industry,
            "size": company.size,
            "location": company.headquarters,
            "founded": company.founded,
            "website": company.website if hasattr(company, 'website') else None
        }
        return company_dict
    except Exception as e:
        logging.error(f"Error fetching company: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve company")