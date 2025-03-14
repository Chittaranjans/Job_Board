// src/components/CompanyCard.tsx
"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import { Building2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Company } from "@/types";

export function CompanyCard({ company }: { company: Company }) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      transition={{ type: "spring", stiffness: 300 }}
      className="h-full"
    >
      <Link href={`/companies/${company.id}`} className="block h-full">
        <Card className="h-full overflow-hidden border hover:shadow-md transition-shadow">
          <CardHeader className="bg-muted/50">
            <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
              <Building2 className="h-5 w-5 flex-shrink-0" />
              <span className="line-clamp-1">{company.name}</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground line-clamp-1">{company.industry}</p>
              <p className="text-sm line-clamp-1">{company.headquarters}</p>
              <p className="text-sm">Founded: {company.founded}</p>
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}