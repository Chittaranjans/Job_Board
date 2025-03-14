// src/types/index.ts

export interface Company {
  id: string;
  name: string;
  url: string;
  founded: number;
  size: string;
  headquarters: string;
  industry: string;
  revenue: string;
}

export interface User {
  id: string;
  name: string;
  company_id: string;
  position: string;
  experience: string;
  location: string;
  email: string;
  phone: string;
  skills: string;
}

export interface Job {
  id: string;
  title: string;
  company_id: string;
  location: string;
  experience: string;
  job_type: string;
  posted_by: string;
  posted_date: string;
}