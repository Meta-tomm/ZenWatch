'use client';

import { MatrixRain, ScanLine } from '@/components/cyberpunk';
import { AnimatedTitle } from './AnimatedTitle';
import { LiveMetrics } from './LiveMetrics';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

interface HeroSectionProps {
  className?: string;
}

/**
 * Cyberpunk-themed hero section for the home page.
 * Combines MatrixRain background, ScanLine effect, AnimatedTitle, and LiveMetrics.
 *
 * @example
 * <HeroSection className="min-h-screen" />
 */
export const HeroSection = ({ className = '' }: HeroSectionProps) => {
  // Sample metrics data (in real app, this would come from API/props)
  const metrics = [
    { value: 127, label: 'Articles Today', trend: 'up' as const, color: 'blue' as const },
    { value: 42, label: 'New Keywords', trend: 'up' as const, color: 'yellow' as const },
    { value: '99%', label: 'Relevance Score', color: 'green' as const },
    { value: 8, label: 'Sources Active', trend: 'neutral' as const, color: 'blue' as const },
  ];

  return (
    <section className={`relative overflow-hidden bg-cyber-black ${className}`}>
      {/* Matrix Rain Background */}
      <MatrixRain className="fixed inset-0 -z-10" color="#00FF41" speed={33} />

      {/* Main Content */}
      <ScanLine className="relative z-10">
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
                className="bg-cyber-green text-cyber-black hover:bg-cyber-green/90 font-bold text-lg px-8 py-6 shadow-lg shadow-cyber-green/50 transition-all hover:shadow-xl hover:shadow-cyber-green/70"
              >
                Explore Articles
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
          </div>

          {/* Live Metrics */}
          <LiveMetrics metrics={metrics} className="mt-12" />
        </div>
      </ScanLine>
    </section>
  );
};
