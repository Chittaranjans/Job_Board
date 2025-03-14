// src/app/page.tsx
import { fetchCompanies, fetchUsers } from "@/lib/api";
import { CompanyCard } from "@/components/CompanyCard";
import { UserCard } from "@/components/UserCard";
import { Search } from "@/components/Search";
import { Company, User } from "@/types"; // Import the interfaces

export default async function Home() {
  const companies: Company[] = await fetchCompanies();
  const users: User[] = await fetchUsers();
  
  // Filter to show only CEOs for the featured section
  const featuredCEOs = users.filter((user) => user.position.includes("CEO"));

  return (
    <div className="w-full px-4 py-8 md:py-12 lg:py-16">
      <div className="container mx-auto max-w-7xl">
        <section className="text-center space-y-4 mb-12">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
            Find Your Dream Job
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Discover opportunities at top companies and connect with industry leaders.
          </p>
          <div className="flex justify-center pt-4">
            <Search />
          </div>
        </section>

        <section className="space-y-6 my-10">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Featured Companies</h2>
            <a href="/companies" className="text-sm text-primary hover:underline">
              View all
            </a>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {companies.slice(0, 6).map((company) => (
              <CompanyCard key={company.id} company={company} />
            ))}
          </div>
        </section>

        <section className="space-y-6 my-10">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold">Industry Leaders</h2>
            <a href="/users" className="text-sm text-primary hover:underline">
              View all
            </a>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredCEOs.slice(0, 6).map((user) => (
              <UserCard key={user.id} user={user} />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}