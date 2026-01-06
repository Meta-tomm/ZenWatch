import Link from 'next/link';
import type { ReactNode } from 'react';

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b">
        <div className="container mx-auto px-4 h-16 flex items-center">
          <Link href="/" className="font-bold text-xl">
            ZenWatch
          </Link>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center p-4">
        {children}
      </main>

      <footer className="border-t py-4">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          ZenWatch - Votre veille technologique intelligente
        </div>
      </footer>
    </div>
  );
}
