// src/data/mock/companies.ts
export const mockCompanies = [
    {
      id: "1", // Change to string to match interface
      name: "Google",
      url: "https://google.com",
      founded: 1998,
      size: "10,000+",
      headquarters: "Mountain View, CA",
      industry: "Technology",
      revenue: "$100B+"
    },
    {
      id: "2", // Change to string to match interface
      name: "Microsoft",
      url: "https://microsoft.com",
      founded: 1975,
      size: "10,000+",
      headquarters: "Redmond, WA",
      industry: "Technology",
      revenue: "$50B+"
    },
    // Add more companies
];
  
// src/data/mock/users.ts
export const mockUsers = [
    {
      id: "1", // Change to string to match interface
      name: "Sundar Pichai",
      company_id: "1", // Change to string for consistency
      position: "CEO",
      experience: "20+ years",
      location: "Mountain View, CA",
      email: "sundar@example.com",
      phone: "+1234567890",
      skills: "Leadership, Technology, Strategy"
    },
    {
      id: "2", // Change to string to match interface
      name: "Satya Nadella",
      company_id: "2", // Change to string for consistency
      position: "CEO",
      experience: "25+ years",
      location: "Redmond, WA",
      email: "satya@example.com",
      phone: "+0987654321",
      skills: "Cloud Computing, AI, Business Transformation"
    },
    // Add more users
];
  
// src/data/mock/jobs.ts
export const mockJobs = [
    {
      id: "1", // Change to string to match interface
      title: "Software Engineer",
      company_id: "1", // Change to string for consistency
      location: "Mountain View, CA",
      experience: "3-5 years",
      job_type: "Full-time",
      posted_by: "HR Department",
      posted_date: "2025-03-01T00:00:00"
    },
    // Add more jobs
];