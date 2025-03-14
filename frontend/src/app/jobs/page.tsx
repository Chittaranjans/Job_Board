import { Metadata } from "next";
import { fetchJobs } from "@/lib/api";
import { JobCard } from "@/components/JobCard";
import { Job } from "@/types";

export const metadata: Metadata = {
  title: "Job Openings | JobBoard",
  description: "Browse all job openings on our platform",
};

export default async function JobsPage() {
  const jobs: Job[] = await fetchJobs();

  return (
    <div className="w-full px-4 py-8 md:py-12">
      <div className="container mx-auto max-w-7xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <h1 className="text-3xl font-bold">Job Openings</h1>
          <div className="w-full md:w-64">
            {/* Add search component here if needed */}
          </div>
        </div>

      <div className="space-y-4">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </div>
    </div>
    </div>
  );
}