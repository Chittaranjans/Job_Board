// src/app/layout.tsx
import { Inter } from 'next/font/google';
import './globals.css';
import { Navigation } from '@/components/Navigation';
import { ThemeProvider } from '@/components/ThemeProvider';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'JobBoard - Find Your Dream Job',
  description: 'Discover opportunities at top companies and connect with industry leaders',
};

import { ReactNode } from 'react';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.className} h-full`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <div className="flex flex-col min-h-screen">
            <Navigation />
            <main className="flex-1 w-full">
              {children}
            </main>
            <footer className="border-t py-6 bg-muted/30 ">
              <div className="container mx-auto px-4">
                <p className="text-center text-sm text-muted-foreground ">
                  © {new Date().getFullYear()} JobBoard. All rights reserved.
                </p>
              </div>
            </footer>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}