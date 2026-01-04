'use client';

interface ScanLineProps {
  children: React.ReactNode;
  className?: string;
}

export const ScanLine = ({ children, className = '' }: ScanLineProps) => {
  return (
    <div className={`scan-line ${className}`}>
      {children}
    </div>
  );
};
