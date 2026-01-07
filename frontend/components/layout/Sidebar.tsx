'use client';

import { useUIStore } from '@/store/ui-store';
import { Button } from '@/components/ui/button';
import { NavLink } from './NavLink';
import { ScrapeButton } from './ScrapeButton';
import { UserMenu } from './UserMenu';
import { Home, BarChart3, ChevronLeft, FileText, Bookmark, Shuffle, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', icon: Home, label: 'Feed' },
  { href: '/personalized', icon: Sparkles, label: 'Pour vous' },
  { href: '/articles', icon: FileText, label: 'Articles' },
  { href: '/library', icon: Bookmark, label: 'Library' },
  { href: '/triage', icon: Shuffle, label: 'Triage' },
  { href: '/analytics', icon: BarChart3, label: 'Analytics' },
];

export const Sidebar = () => {
  const collapsed = useUIStore((s) => s.sidebarCollapsed);
  const toggleSidebar = useUIStore((s) => s.toggleSidebar);

  return (
    <aside
      className={cn(
        'hidden md:flex flex-col border-r border-violet-500/20 bg-anthracite-950 transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-violet-500/20">
        {!collapsed && (
          <h1 className="text-xl font-bold text-gradient-violet">
            ZenWatch
          </h1>
        )}
        <div className={cn('flex items-center gap-1', collapsed && 'flex-col')}>
          <ScrapeButton collapsed={collapsed} />
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className={cn('text-violet-300/70 hover:text-violet-200 hover:bg-violet-500/20')}
          >
            <ChevronLeft
              className={cn(
                'w-4 h-4 transition-transform',
                collapsed && 'rotate-180'
              )}
            />
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.href}
            href={item.href}
            icon={item.icon}
            label={item.label}
            collapsed={collapsed}
          />
        ))}
      </nav>

      {/* User section */}
      <UserMenu collapsed={collapsed} />

      {/* Footer */}
      {!collapsed && (
        <div className="px-4 py-2 text-xs text-muted-foreground">
          ZenWatch v1.0.0
        </div>
      )}
    </aside>
  );
};
