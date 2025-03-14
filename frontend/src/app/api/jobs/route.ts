import { NextResponse } from 'next/server';
import { mockJobs } from "@/data/mock/companies";

// Helper function to get base URL
function getBaseUrl() {
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
}

export async function GET() {
  try {
    const baseUrl = getBaseUrl();
    const response = await fetch(`${baseUrl}/api/v1/jobs`, {
      next: { revalidate: 60 }
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching jobs, using mock data:', error);
    return NextResponse.json(mockJobs);
  }
}