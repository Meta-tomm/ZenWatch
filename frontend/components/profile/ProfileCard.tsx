'use client';

import { ExternalLink, Github, Globe, Pencil } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { User, UserPublicProfile } from '@/types/auth';

interface ProfileCardProps {
  profile: User | UserPublicProfile;
  isCurrentUser?: boolean;
  onEdit?: () => void;
}

export const ProfileCard = ({ profile, isCurrentUser, onEdit }: ProfileCardProps) => {
  const userInitials = profile.username?.slice(0, 2).toUpperCase() || 'U';

  return (
    <div className="rounded-xl border border-violet-500/20 bg-anthracite-900/50 backdrop-blur overflow-hidden">
      {/* Header with gradient */}
      <div className="h-24 bg-gradient-to-r from-violet-600/20 via-purple-600/20 to-fuchsia-600/20" />

      {/* Profile content */}
      <div className="px-6 pb-6">
        {/* Avatar - overlapping header */}
        <div className="flex items-end justify-between -mt-12">
          <Avatar className="h-24 w-24 border-4 border-anthracite-900 ring-2 ring-violet-500/30">
            <AvatarImage src={profile.avatar_url} />
            <AvatarFallback className="text-2xl bg-violet-500/20 text-violet-200">
              {userInitials}
            </AvatarFallback>
          </Avatar>

          {isCurrentUser && onEdit && (
            <Button
              variant="outline"
              size="sm"
              onClick={onEdit}
              className="border-violet-500/30 text-violet-300 hover:bg-violet-500/20 hover:text-violet-100 gap-2"
            >
              <Pencil className="w-4 h-4" />
              Modifier
            </Button>
          )}
        </div>

        {/* User info */}
        <div className="mt-4 space-y-3">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="text-2xl font-bold text-violet-100">
              {profile.username || 'Utilisateur'}
            </h2>
            {'is_admin' in profile && (profile as User).is_admin && (
              <Badge className="bg-violet-500/20 text-violet-300 border-violet-500/30">
                Admin
              </Badge>
            )}
            {'is_verified' in profile && (profile as User).is_verified && (
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                Verifie
              </Badge>
            )}
          </div>

          {profile.bio && (
            <p className="text-violet-300/70 leading-relaxed">{profile.bio}</p>
          )}
        </div>

        {/* Links */}
        {(profile.github_url || profile.portfolio_url) && (
          <div className="flex flex-wrap gap-3 mt-6 pt-6 border-t border-violet-500/10">
            {profile.github_url && (
              <a
                href={profile.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-anthracite-800/50 border border-violet-500/20 text-sm text-violet-300 hover:text-violet-100 hover:bg-violet-500/10 hover:border-violet-500/30 transition-colors"
              >
                <Github className="h-4 w-4" />
                GitHub
                <ExternalLink className="h-3 w-3 opacity-50" />
              </a>
            )}

            {profile.portfolio_url && (
              <a
                href={profile.portfolio_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-anthracite-800/50 border border-violet-500/20 text-sm text-violet-300 hover:text-violet-100 hover:bg-violet-500/10 hover:border-violet-500/30 transition-colors"
              >
                <Globe className="h-4 w-4" />
                Portfolio
                <ExternalLink className="h-3 w-3 opacity-50" />
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
