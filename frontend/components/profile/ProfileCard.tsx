'use client';

import { formatDistanceToNow } from 'date-fns';
import { Github, Globe, Calendar, Shield } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
} from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { User, UserPublicProfile } from '@/types/auth';

interface ProfileCardProps {
  user: User | UserPublicProfile;
  isCurrentUser?: boolean;
  onEdit?: () => void;
}

export const ProfileCard = ({ user, isCurrentUser = false, onEdit }: ProfileCardProps) => {
  const getInitials = (username: string) => {
    return username.slice(0, 2).toUpperCase();
  };

  const isFullUser = (u: User | UserPublicProfile): u is User => {
    return 'email' in u;
  };

  return (
    <Card className="bg-anthracite-800/80 border-violet-500/30">
      <CardHeader className="pb-4">
        <div className="flex items-start gap-4">
          <Avatar className="h-20 w-20">
            {user.avatar_url && (
              <AvatarImage src={user.avatar_url} alt={user.username} />
            )}
            <AvatarFallback className="bg-violet-600 text-white text-xl">
              {getInitials(user.username)}
            </AvatarFallback>
          </Avatar>

          <div className="flex-1">
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-violet-100">{user.username}</h2>
              {isFullUser(user) && user.role === 'admin' && (
                <Badge className="bg-violet-600 text-white">
                  <Shield className="w-3 h-3 mr-1" />
                  Admin
                </Badge>
              )}
              {isFullUser(user) && user.is_verified && (
                <Badge variant="outline" className="border-green-500/50 text-green-400">
                  Verified
                </Badge>
              )}
            </div>

            {isFullUser(user) && (
              <p className="text-sm text-violet-300/70 mt-1">{user.email}</p>
            )}

            <div className="flex items-center gap-1 text-xs text-violet-300/50 mt-2">
              <Calendar className="w-3 h-3" />
              Joined {formatDistanceToNow(new Date(user.created_at), { addSuffix: true })}
            </div>
          </div>

          {isCurrentUser && onEdit && (
            <Button
              variant="outline"
              size="sm"
              onClick={onEdit}
              className="border-violet-500/30 text-violet-200 hover:bg-violet-500/20"
            >
              Edit Profile
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {user.bio && (
          <p className="text-violet-100/80 text-sm leading-relaxed">{user.bio}</p>
        )}

        <div className="flex flex-wrap gap-3">
          {user.github_url && (
            <a
              href={user.github_url}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(
                'inline-flex items-center gap-2 px-3 py-1.5 rounded-md',
                'bg-anthracite-700 hover:bg-anthracite-600',
                'text-violet-200 text-sm transition-colors'
              )}
            >
              <Github className="w-4 h-4" />
              GitHub
            </a>
          )}

          {user.portfolio_url && (
            <a
              href={user.portfolio_url}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(
                'inline-flex items-center gap-2 px-3 py-1.5 rounded-md',
                'bg-anthracite-700 hover:bg-anthracite-600',
                'text-violet-200 text-sm transition-colors'
              )}
            >
              <Globe className="w-4 h-4" />
              Portfolio
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
