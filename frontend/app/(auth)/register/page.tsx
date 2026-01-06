import { RegisterForm } from '@/components/auth';
import { AuthGuard } from '@/components/auth';

export const metadata = {
  title: 'Inscription - ZenWatch',
  description: 'Creez votre compte ZenWatch',
};

export default function RegisterPage() {
  return (
    <AuthGuard requireAuth={false} redirectTo="/">
      <RegisterForm />
    </AuthGuard>
  );
}
