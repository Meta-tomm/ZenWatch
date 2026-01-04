import { Variants } from 'framer-motion';

/**
 * 3D card lift animation with rotation
 * Use on cards for premium hover effect
 */
export const card3DLift: Variants = {
  initial: {
    rotateX: 0,
    rotateY: 0,
    z: 0,
    scale: 1,
  },
  hover: {
    rotateX: -5,
    rotateY: 5,
    z: 20,
    scale: 1.02,
    transition: {
      duration: 0.6,
      ease: [0.23, 1, 0.32, 1], // Custom easing
    },
  },
};

/**
 * Fade in from bottom with slight rotation
 * Use for scroll-based reveal animations
 */
export const fadeInFromBottom: Variants = {
  hidden: {
    opacity: 0,
    y: 60,
    rotateX: 10,
  },
  visible: {
    opacity: 1,
    y: 0,
    rotateX: 0,
    transition: {
      duration: 0.8,
      ease: [0.23, 1, 0.32, 1],
    },
  },
};

/**
 * Stagger children animations
 * Use on parent containers
 */
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
    },
  },
};

/**
 * Minimal fade in (for articles page)
 * Quick, subtle, performance-friendly
 */
export const minimalFadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.3,
      ease: 'easeOut',
    },
  },
};

/**
 * Glow intensity animation
 * Use with box-shadow for hover states
 */
export const glowPulse: Variants = {
  initial: {
    boxShadow: '0 0 20px rgba(139, 92, 246, 0.3)',
  },
  hover: {
    boxShadow: [
      '0 0 20px rgba(139, 92, 246, 0.3)',
      '0 0 40px rgba(217, 70, 239, 0.5)',
      '0 0 20px rgba(139, 92, 246, 0.3)',
    ],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};
