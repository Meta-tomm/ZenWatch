'use client';

import { AnimatedTitle } from './AnimatedTitle';
import { LiveMetrics } from './LiveMetrics';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

interface HeroSectionProps {
  className?: string;
}

/**
 * Minimalist hero section with black and gold theme.
 * Features subtle animations and clean design.
 *
 * @example
 * <HeroSection className="min-h-screen" />
 */
export const HeroSection = ({ className = '' }: HeroSectionProps) => {
  // Sample metrics data (in real app, this would come from API/props)
  const metrics = [
    { value: 127, label: 'Articles Today', trend: 'up' as const, color: 'gold' as const },
    { value: 42, label: 'New Keywords', trend: 'up' as const, color: 'gold-light' as const },
    { value: '99%', label: 'Relevance Score', color: 'gold-dark' as const },
    { value: 8, label: 'Sources Active', trend: 'neutral' as const, color: 'gold' as const },
  ];

  return (
    <section className={`relative overflow-hidden bg-charcoal-950 ${className}`}>
      {/* Main Content */}
      <div className="relative z-10">
        <div className="container mx-auto px-4 py-20 md:py-32">
          {/* Hero Title */}
          <AnimatedTitle
            title="ZENWATCH"
            subtitle="Your AI-Powered Tech Intelligence Platform"
            className="text-center mb-16"
          />

          {/* CTA Button */}
          <div className="flex justify-center mb-12">
            <Link href="/articles">
              <Button
                size="lg"
                className="bg-gold text-black hover:bg-gold-light font-bold text-lg px-8 py-6 transition-all hover:scale-105"
              >
                Explore Articles
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
          </div>

          {/* Live Metrics */}
          <LiveMetrics metrics={metrics} className="mt-12" />
        </div>
      </div>
    </section>
  );
};
