import { Metadata } from "next";
import { fetchUsers } from "@/lib/api";
import { UserCard } from "@/components/UserCard";
import { User } from "@/types";

export const metadata: Metadata = {
  title: "Professionals | JobBoard",
  description: "Browse all professionals on our platform",
};

export default async function UsersPage() {
  const users: User[] = await fetchUsers();

  return (
    <div className="w-full px-4 py-8 md:py-12">
      <div className="container mx-auto max-w-7xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
          <h1 className="text-3xl font-bold">Professionals</h1>
          <div className="w-full md:w-64">
            {/* Add search component here if needed */}
          </div>
        </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {users.map((user) => (
          <UserCard key={user.id} user={user} />
        ))}
      </div>
    </div>
    </div>
  );
}