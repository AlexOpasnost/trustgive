import { motion, type MotionProps } from "framer-motion"
import type { ReactNode } from "react"

type Props = {
  children: ReactNode
  delay?: number
  y?: number
  className?: string
} & MotionProps

/**
 * Restrained scroll-driven reveal — fade in + small translate.
 * Used sparingly: hero, section transitions. Never on text inside long prose.
 *
 * Honours prefers-reduced-motion via the global CSS rule in index.css —
 * framer-motion respects the OS setting automatically.
 */
export function Reveal({ children, delay = 0, y = 12, className, ...rest }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1], delay }}
      className={className}
      {...rest}
    >
      {children}
    </motion.div>
  )
}
