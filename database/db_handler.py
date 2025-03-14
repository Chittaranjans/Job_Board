# database/db_handler.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.model import Company, Job, UserProfile, Base
from datetime import datetime, timedelta
import dotenv
import os
import logging

dotenv.load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def store_data(data, data_type):
    """Store data in appropriate database table"""
    try:
        if data_type.lower() == 'job':
            # Only include fields that match your Job model
            job_data = {
                'title': data.get('title', 'Exciting Position'),
                'location': data.get('location', 'Remote'),
                'company_id': data.get('company_id', 1),
                'experience': data.get('experience', 'Various levels'),
                'job_type': data.get('job_type', 'Full-time'),  # Required field
                'posted_by': data.get('posted_by', 'LinkedIn'),  # Required field
                'posted_date': data.get('posted_date', datetime.datetime.now())  # Correct field name
            }
            
            # Create and save job
            job = Job(**job_data)
            db = next(get_db())
            db.add(job)
            db.commit()
            db.refresh(job)
            return job.id
        
        # Handle other data types...
        
    except Exception as e:
        logging.error(f"Database error: {str(e)}")
        return None

def get_data(table: str, id: int = None):
    """Retrieve data from database"""
    session = SessionLocal()
    try:
        if table == 'job':
            return session.query(Job).filter(Job.id == id).first() if id else session.query(Job).all()
        elif table == 'company':
            return session.query(Company).filter(Company.id == id).first() if id else session.query(Company).all()
        elif table == 'user':
            return session.query(UserProfile).filter(UserProfile.id == id).first() if id else session.query(UserProfile).all()
        else:
            raise ValueError(f"Unknown table type: {table}")
    finally:
        session.close()

def delete_data(table: str, id: int):
    """Delete data from database"""
    session = SessionLocal()
    try:
        if table == 'job':
            session.query(Job).filter(Job.id == id).delete()
        elif table == 'company':
            session.query(Company).filter(Company.id == id).delete()
        elif table == 'user':
            session.query(UserProfile).filter(UserProfile.id == id).delete()
        else:
            raise ValueError(f"Unknown table type: {table}")
            
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Delete error: {str(e)}")
        raise
    finally:
        session.close()

def refresh_data():
    """Clean up old data"""
    session = SessionLocal()
    try:
        # Delete jobs older than 30 days
        cutoff = datetime.now() - timedelta(days=30)
        session.query(Job).filter(Job.posted_date < cutoff).delete()
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Refresh error: {str(e)}")
        raise
    finally:
        session.close()