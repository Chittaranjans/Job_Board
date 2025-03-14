import { Metadata } from "next";
import { fetchCompanies } from "@/lib/api";
import { CompanyCard } from "@/components/CompanyCard";
import { Company } from "@/types";

export const metadata: Metadata = {
  title: "Companies | JobBoard",
  description: "Browse all companies on our platform",
};

export default async function CompaniesPage() {
  const companies: Company[] = await fetchCompanies();

  return (
    <div className="w-full px-4 py-8 md:py-12">
      <div className="container mx-auto max-w-7xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <h1 className="text-3xl font-bold">Companies</h1>
          <div className="w-full md:w-64">
            {/* Add search component here if needed */}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {companies.map((company) => (
            <CompanyCard key={company.id} company={company} />
          ))}
        </div>
      </div>
    </div>
  );
}