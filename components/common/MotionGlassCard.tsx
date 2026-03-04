"use client";

import * as React from "react";
import { motion, HTMLMotionProps } from "framer-motion";

// Reusable glassmorphism motion card with subtle lift + glow on hover
// - Provides sane defaults for background, border, blur, and shadow
// - Allows passing any motion.div props (e.g., layout)
// - Glow overlay fades in on hover; can be disabled via `glow={false}`
// - Hover lift/scale can be disabled via `hoverEffect={false}`

// HTMLMotionProps<'div'> already includes className, children, and all
// animation-related props, so extending it ensures the component is
// fully compatible with framer-motion's <motion.div> properties.
export interface MotionGlassCardProps extends HTMLMotionProps<"div"> {
  hoverEffect?: boolean;
  glow?: boolean;
  glowClassName?: string;
}

const MotionGlassCard = React.forwardRef<HTMLDivElement, MotionGlassCardProps>(
  (
    {
      className = "",
      children,
      hoverEffect = true,
      glow = true,
      glowClassName = "",
      initial,
      animate,
      whileHover,
      whileTap,
      transition,
      ...rest
    },
    ref
  ) => {
    return (
      <motion.div
        ref={ref}
        // Sensible entry animation; overridable via props
        initial={initial ?? { opacity: 0, y: 4, scale: 0.985 }}
        animate={animate ?? { opacity: 1, y: 0, scale: 1 }}
        whileHover={
          hoverEffect
            ? whileHover ?? { y: -6, scale: 1.01 }
            : whileHover
        }
        whileTap={hoverEffect ? whileTap ?? { scale: 0.997 } : whileTap}
        transition={
          transition ?? { type: "spring", stiffness: 320, damping: 26, mass: 0.6 }
        }
        className={
          [
            // Base glass look
            "relative group overflow-hidden rounded-xl",
            "bg-deep-black/50 backdrop-blur-xl",
            "border border-white/10",
            "shadow-[0_10px_30px_rgba(0,0,0,0.25)]",
            className,
          ].join(" ")
        }
        {...rest}
      >
        {/* Subtle top sheen */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-x-0 top-0 h-1/2 bg-gradient-to-b from-white/[0.04] to-transparent"
        />

        {/* Neon glow overlay (fades in on hover) */}
        {glow && (
          <div
            aria-hidden
            className={[
              "pointer-events-none absolute inset-0",
              "opacity-0 group-hover:opacity-100 transition-opacity duration-300",
              glowClassName,
            ].join(" ")}
          >
            <div className="absolute -inset-24 bg-[radial-gradient(200px_120px_at_50%_-20px,rgba(193,255,0,0.18),transparent_70%)] blur-2xl" />
          </div>
        )}

        {/* Content */}
        <div className="relative z-[1]">{children}</div>
      </motion.div>
    );
  }
);

MotionGlassCard.displayName = "MotionGlassCard";

export default MotionGlassCard;
