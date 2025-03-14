# database/models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    founded = Column(Integer)
    size = Column(String)
    headquarters = Column(String)
    industry = Column(String)
    revenue = Column(String)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'founded': self.founded,
            'size': self.size,
            'headquarters': self.headquarters,
            'industry': self.industry,
            'revenue': self.revenue
        }

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    company_id = Column(Integer, ForeignKey('companies.id'))
    location = Column(String)
    experience = Column(String)
    job_type = Column(String)
    posted_by = Column(String)
    posted_date = Column(DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company_id': self.company_id,
            'location': self.location,
            'experience': self.experience,
            'job_type': self.job_type,
            'posted_by': self.posted_by,
            'posted_date': str(self.posted_date) if self.posted_date else None
        }

class UserProfile(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    company_id = Column(Integer, ForeignKey('companies.id'))
    position = Column(String)
    experience = Column(String)
    location = Column(String)
    email = Column(String)
    phone = Column(String)
    skills = Column(String)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company_id': self.company_id,
            'position': self.position,
            'experience': self.experience,
            'location': self.location,
            'email': self.email,
            'phone': self.phone,
            'skills': self.skills
        }