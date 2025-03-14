# api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from .routes import job_routes, company_routes, profile_routes

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

app = FastAPI(
    title="JobLo API",
    description="API for job scraping and management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    filename='logs/api.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Include routers
app.include_router(job_routes.router, prefix="/api/v1", tags=["jobs"])
app.include_router(company_routes.router, prefix="/api/v1", tags=["companies"])
app.include_router(profile_routes.router, prefix="/api/v1", tags=["profiles"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to JobLo API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }