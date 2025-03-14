import { NextResponse } from 'next/server';
import { mockUsers } from "@/data/mock/companies";

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
    
    // Get all profiles and filter by company_id
    const response = await fetch(`${baseUrl}/api/v1/profiles`, {
      next: { revalidate: 60 }
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const users = await response.json();
    const filteredUsers = users.filter((user: { company_id: string }) => String(user.company_id) === String(id));
    
    return NextResponse.json(filteredUsers);
  } catch (error) {
    console.error(`Error fetching users for company ${id}, using mock data:`, error);
    const users = mockUsers.filter(user => user.company_id === id);
    return NextResponse.json(users);
  }
}