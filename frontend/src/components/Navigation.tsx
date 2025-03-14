// src/components/Navigation.tsx
'use client';

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "./ThemeToggle";
import { Briefcase } from "lucide-react";

export function Navigation() {
  const pathname = usePathname();
  
  const routes = [
    { name: 'Home', path: '/' },
    { name: 'Companies', path: '/companies' },
    { name: 'Jobs', path: '/jobs' },
    { name: 'Users', path: '/users' },
  ];

  return (
    <div className="border-b bg-background sticky top-0 z-40">
      <div className="pr-5 pl-5 flex items-center justify-between py-4 container px-4 mx-auto max-w-7xl gap-4">

        <Link href="/" className="text-xl font-bold flex items-center gap-2">
        <Briefcase className="h-6 w-6" />
        <span className="font-bold text-xl">JobBoard</span>
        </Link>
        
        <nav className="flex items-center gap-6">
          {routes.map(route => (
            <Link 
              key={route.path}
              href={route.path}
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                pathname === route.path ? "text-primary" : "text-muted-foreground"
              )}
            >
              {route.name}
            </Link>
          ))}
          <ThemeToggle />
        </nav>
      </div>
    </div>
  );
}