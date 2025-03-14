import { NextResponse } from 'next/server';
import { mockJobs } from "@/data/mock/companies";

// Helper function to get base URL
function getBaseUrl() {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const id = params.id;
  
  try {
    const baseUrl = getBaseUrl();
    // First check if company-specific endpoint exists in your API
    const response = await fetch(`${baseUrl}/api/v1/companies/${id}/jobs`, {
      next: { revalidate: 60 }
    });
    
    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    }
    
    // If company-specific endpoint fails, get all jobs and filter
    const allJobsResponse = await fetch(`${baseUrl}/api/v1/jobs`, {
      next: { revalidate: 60 }
    });
    
    if (allJobsResponse.ok) {
      const jobs = await allJobsResponse.json();
      const filteredJobs = jobs.filter((job: { company_id: string }) => job.company_id === id);
      return NextResponse.json(filteredJobs);
    }
    
    throw new Error('Failed to fetch jobs');
  } catch (error) {
    console.error(`Error fetching jobs for company ${id}, using mock data:`, error);
    const jobs = mockJobs.filter(job => job.company_id === id);
    return NextResponse.json(jobs);
  }
}