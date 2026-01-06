import { LoginForm } from '@/components/auth';
import { AuthGuard } from '@/components/auth';

export const metadata = {
  title: 'Connexion - ZenWatch',
  description: 'Connectez-vous a votre compte ZenWatch',
};

export default function LoginPage() {
  return (
    <AuthGuard requireAuth={false} redirectTo="/">
      <LoginForm />
    </AuthGuard>
  );
}
