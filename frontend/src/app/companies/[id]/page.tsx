// src/app/companies/[id]/page.tsx
import { fetchCompanyById, fetchUsersByCompany, fetchJobsByCompany } from "@/lib/api";
import { UserCard } from "../../../components/UserCard";
import { JobCard } from "../../../components/JobCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Job , User , Company } from "@/types";
interface CompanyPageParams {
    params: {
      id: string;
    };
  }


export default async function CompanyPage({ params }: CompanyPageParams) {
  const company:Company = await fetchCompanyById(params.id);
  const employees:User[] = await fetchUsersByCompany(params.id);
  const jobs:Job[] = await fetchJobsByCompany(params.id);

  return (
    <div className="container py-8 space-y-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">{company.name}</h1>
        <p className="text-muted-foreground">{company.industry}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Card>
          <CardHeader>
            <CardTitle>Company Details</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-2">
              <div className="flex justify-between">
                <dt className="font-medium">Founded</dt>
                <dd>{company.founded}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="font-medium">Headquarters</dt>
                <dd>{company.headquarters}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="font-medium">Size</dt>
                <dd>{company.size}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="font-medium">Revenue</dt>
                <dd>{company.revenue}</dd>
              </div>
              <div className="pt-2">
                <a href={company.url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                  Visit Website
                </a>
              </div>
            </dl>
          </CardContent>
        </Card>
      </div>

      <section className="space-y-6">
        <h2 className="text-2xl font-semibold">Open Positions</h2>
        <div className="space-y-4">
          {jobs.length > 0 ? (
            jobs.map(job => <JobCard key={job.id} job={job} />)
          ) : (
            <p className="text-muted-foreground">No open positions at this time.</p>
          )}
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-2xl font-semibold">Employees</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {employees.map(user => <UserCard key={user.id} user={user} />)}
        </div>
      </section>
    </div>
  );
}