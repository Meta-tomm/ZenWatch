'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LoginForm } from '@/components/auth/LoginForm';
import { OAuthButtons } from '@/components/auth/OAuthButtons';

export default function LoginPage() {
  return (
    <Card className="w-full max-w-md bg-anthracite-800/80 border-violet-500/30">
      <CardHeader className="space-y-1 text-center">
        <CardTitle className="text-2xl font-bold text-violet-100">Welcome back</CardTitle>
        <CardDescription className="text-violet-300/70">
          Sign in to your account to continue
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <OAuthButtons mode="login" />

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-violet-500/30" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-anthracite-800 px-2 text-violet-300/50">
              Or continue with email
            </span>
          </div>
        </div>

        <LoginForm />

        <div className="text-center text-sm">
          <span className="text-violet-300/70">Don't have an account? </span>
          <Link
            href="/register"
            className="text-violet-400 hover:text-violet-300 font-medium"
          >
            Sign up
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
