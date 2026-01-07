'use client';

import Link from 'next/link';
import { useAuthStore } from '@/store/auth-store';
import { useAuth } from '@/hooks/use-auth';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { LogIn, LogOut, User, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';

interface UserMenuProps {
  collapsed?: boolean;
}

export function UserMenu({ collapsed = false }: UserMenuProps) {
  const { user, isAuthenticated, isLoading } = useAuthStore();
  const { logout, isLoggingOut } = useAuth();

  if (isLoading) {
    return (
      <div className={cn(
        'p-3 border-t border-violet-500/20',
        collapsed && 'flex justify-center'
      )}>
        <div className="h-9 w-9 rounded-full bg-violet-500/20 animate-pulse" />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <div className={cn(
        'p-3 border-t border-violet-500/20 space-y-2',
        collapsed && 'flex flex-col items-center'
      )}>
        <Button
          variant="outline"
          size="sm"
          className={cn(
            'w-full border-violet-500/30 hover:bg-violet-500/20',
            collapsed && 'w-9 p-0'
          )}
          asChild
        >
          <Link href="/login">
            <LogIn className="w-4 h-4" />
            {!collapsed && <span className="ml-2">Connexion</span>}
          </Link>
        </Button>
        {!collapsed && (
          <Button
            variant="ghost"
            size="sm"
            className="w-full text-violet-300/70 hover:text-violet-200"
            asChild
          >
            <Link href="/register">
              Creer un compte
            </Link>
          </Button>
        )}
      </div>
    );
  }

  const initials = user.display_name
    ? user.display_name.slice(0, 2).toUpperCase()
    : user.email.slice(0, 2).toUpperCase();

  return (
    <div className={cn(
      'p-3 border-t border-violet-500/20',
      collapsed && 'flex justify-center'
    )}>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            className={cn(
              'w-full justify-start gap-2 px-2 hover:bg-violet-500/20',
              collapsed && 'w-9 p-0 justify-center'
            )}
          >
            <Avatar className="h-8 w-8">
              <AvatarImage src={user.avatar_url || undefined} alt={user.display_name || user.email} />
              <AvatarFallback className="bg-violet-500/30 text-violet-200 text-xs">
                {initials}
              </AvatarFallback>
            </Avatar>
            {!collapsed && (
              <div className="flex-1 text-left overflow-hidden">
                <p className="text-sm font-medium text-violet-100 truncate">
                  {user.display_name || user.username || 'Utilisateur'}
                </p>
                <p className="text-xs text-violet-300/60 truncate">
                  {user.email}
                </p>
              </div>
            )}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align={collapsed ? 'center' : 'end'} className="w-56">
          <DropdownMenuItem asChild>
            <Link href="/profile" className="flex items-center gap-2">
              <User className="w-4 h-4" />
              Mon compte
            </Link>
          </DropdownMenuItem>
          {user.is_admin && (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link href="/admin" className="flex items-center gap-2">
                  <Shield className="w-4 h-4" />
                  Administration
                </Link>
              </DropdownMenuItem>
            </>
          )}
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={() => logout()}
            disabled={isLoggingOut}
            className="text-red-400 focus:text-red-400"
          >
            <LogOut className="w-4 h-4 mr-2" />
            {isLoggingOut ? 'Deconnexion...' : 'Se deconnecter'}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
