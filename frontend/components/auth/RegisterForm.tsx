'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { useAuth } from '@/hooks/use-auth';
import { OAuthButtons } from './OAuthButtons';

const registerSchema = z.object({
  email: z.string().email('Email invalide'),
  username: z
    .string()
    .min(3, 'Le nom utilisateur doit contenir au moins 3 caracteres')
    .max(30, 'Le nom utilisateur ne peut pas depasser 30 caracteres')
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      'Le nom utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores'
    ),
  password: z
    .string()
    .min(8, 'Le mot de passe doit contenir au moins 8 caracteres')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
      'Le mot de passe doit contenir au moins une majuscule, une minuscule et un chiffre'
    ),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Les mots de passe ne correspondent pas',
  path: ['confirmPassword'],
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export const RegisterForm = () => {
  const { register, isRegistering, registerError } = useAuth();

  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: '',
      username: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = (values: RegisterFormValues) => {
    register({
      email: values.email,
      username: values.username,
      password: values.password,
    });
  };

  return (
    <div className="w-full max-w-md space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold">Creer un compte</h1>
        <p className="text-muted-foreground mt-2">
          Rejoignez ZenWatch pour suivre votre veille techno
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    placeholder="votre@email.com"
                    autoComplete="email"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="username"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Nom utilisateur</FormLabel>
                <FormControl>
                  <Input
                    placeholder="johndoe"
                    autoComplete="username"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Mot de passe</FormLabel>
                <FormControl>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    autoComplete="new-password"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="confirmPassword"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Confirmer le mot de passe</FormLabel>
                <FormControl>
                  <Input
                    type="password"
                    placeholder="••••••••"
                    autoComplete="new-password"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {registerError && (
            <p className="text-sm text-destructive">
              Une erreur est survenue lors de linscription
            </p>
          )}

          <Button type="submit" className="w-full" disabled={isRegistering}>
            {isRegistering ? 'Creation...' : 'Creer mon compte'}
          </Button>
        </form>
      </Form>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Ou continuer avec
          </span>
        </div>
      </div>

      <OAuthButtons />

      <p className="text-center text-sm text-muted-foreground">
        Deja un compte ?{' '}
        <Link href="/login" className="text-primary hover:underline">
          Se connecter
        </Link>
      </p>
    </div>
  );
};
