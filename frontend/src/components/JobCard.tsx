"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import { Briefcase } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Job } from "@/types"; // Import the interface

export function JobCard({ job }: { job: Job }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      transition={{ type: "spring", stiffness: 300 }}
    >
      <Link href={`/jobs/${job.id}`}>
        <Card className="h-full overflow-hidden">
          <CardHeader className="bg-muted/30">
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="h-5 w-5" />
              {job.title}
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-4">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Location: {job.location}
              </p>
              <p className="text-sm">
                Experience: {job.experience}
              </p>
              <p className="text-sm text-muted-foreground">
                Type: {job.job_type}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Posted: {new Date(job.posted_date).toLocaleDateString()}
              </p>
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}