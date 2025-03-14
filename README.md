# JobLo Scraping - LinkedIn Data Scraping Platform

A comprehensive platform for scraping job listings, user profiles, and company information from LinkedIn with a FastAPI backend.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [API Routes](#api-routes)
- [Scraping Approach](#scraping-approach)
- [Usage Examples](#usage-examples)
- [Deployment](#deployment)

## Overview
JobLo Scraping is a professional platform designed to extract and manage job listings, professional profiles, and company information from LinkedIn. The system includes advanced web scraping capabilities with anti-detection features, data storage in PostgreSQL/SQLite, and a RESTful API for accessing the collected data.

## Features
- **Job Scraping**: Extract job listings with title, company, location, experience level, and more
- **Profile Scraping**: Collect user profiles with name, position, skills, experience, etc.
- **Company Scraping**: Gather company information including industry, size, headquarters
- **REST API**: Access all data through a well-documented FastAPI interface
- **Anti-Detection**: Advanced techniques to prevent scraping detection
- **Proxy Rotation**: Automatic rotation of proxies to avoid IP blocks
- **Database Storage**: Persistent storage of all scraped data

## Tech Stack
- **Backend**: FastAPI
- **Database**: SQLAlchemy with PostgreSQL/SQLite
- **Web Scraping**: Selenium, BeautifulSoup4
- **Browser Automation**: Chrome WebDriver
- **Authentication**: Cookie-based session management
- **Proxy Management**: Custom proxy rotation system

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/joblo_scraping.git
   cd joblo_scraping

   ```

2. Install dependencies:  
3. Create environment variables:

4. Create a .env file in the project root with the following variables:
   ```bash
  DATABASE_URL=postgresql://user:password@host/dbname
  LINKEDIN_EMAIL=your_email@example.com
  LINKEDIN_PASSWORD=your_password

  ```
 5. Proxy Configuration
 Add proxy servers to proxies.txt (one per line) in the format:

## API Routes
#### Jobs Routes
```bash
GET /api/v1/jobs: Get all job listings (paginated)

GET /api/v1/jobs/{job_id}: Get specific job by ID

POST /api/v1/jobs/scrape: Initiate job scraping with query parameters
```
## Profiles Routes
```bash
GET /api/v1/profiles: Get all user profiles (paginated)

GET /api/v1/profiles/{profile_id}: Get specific profile by ID

POST /api/v1/profiles/scrape: Initiate profile scraping with LinkedIn URL
```
## Companies Routes

```bash
GET /api/v1/companies: Get all companies (paginated)

GET /api/v1/companies/{company_id}: Get specific company by ID

GET /api/v1/companies/{company_id}/jobs: Get jobs associated with a company

GET /api/v1/companies/{company_id}/users: Get profiles associated with a company
```
## Query Parameters

1. Most GET endpoints support the following query parameters:

page: Page number (default: 1)
limit: Items per page (default: 10, max: 100)

## Scraping Approach
1. Anti-Detection Techniques
#### Browser Fingerprinting Evasion: Disables automation flags in WebDriver
#### Human-like Behavior: Randomized delays between actions

2. Proxy Rotation: Changes IP addresses to avoid rate limiting

3. Cookie Management: Saves and reuses session cookies

4. User-Agent Rotation: Changes browser identification

5. Headless Mode: Optional hidden browser operation

### Job Scraping Process
```bash
Authenticate with LinkedIn credentials or saved cookies

Navigate to job search URL with query parameters

Handle any security verifications (CAPTCHA/challenges)

Scroll through listings to load content dynamically

Extract job details using advanced selectors

Parse and clean data before storing in database

Profile Scraping Process
Authenticate with LinkedIn credentials

Navigate to specific profile URL

Extract user information sections (experience, education, etc.)

Process connections and company relationships

Store normalized data in database

```

## Usage Examples
1. Scrape Job Listings
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/scrape?query=software+engineer&location=usa"
```
2. Start API Server
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```



### How to Use:
1. Copy the above markdown code.
2. Create a file named `README.md` in the root of your project.
3. Paste the code into the file.
4. Customize placeholders (e.g., `yourusername`, `your_email@example.com`, etc.) with your actual details.

Let me know if you need further assistance! 🚀