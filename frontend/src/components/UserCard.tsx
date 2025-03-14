// src/components/UserCard.tsx
"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import { User as UserIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { User } from "@/types"; 

export function UserCard({ user }: { user: User }) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      transition={{ type: "spring", stiffness: 300 }}
    >
      <Link href={`/users/${user.id}`}>
        <Card className="h-full overflow-hidden">
          <CardHeader className="flex flex-row items-center gap-4">
            <Avatar>
              <AvatarFallback>
                {user.name.split(' ').map(n => n[0]).join('')}
              </AvatarFallback>
            </Avatar>
            <CardTitle>{user.name}</CardTitle>
          </CardHeader>
          <CardContent className="pt-2">
            <div className="space-y-2">
              <p className="text-sm font-medium">{user.position}</p>
              <p className="text-sm text-muted-foreground">{user.location}</p>
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}