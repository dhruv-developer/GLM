"use client"

import { Badge } from "@/components/ui/badge"
import { motion } from "framer-motion"

interface ShimmerBadgeProps {
  children: React.ReactNode
  className?: string
}

export function ShimmerBadge({ children, className = "" }: ShimmerBadgeProps) {
  return (
    <Badge className={`relative overflow-hidden ${className}`}>
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
        animate={{
          x: ["-100%", "100%"],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "linear",
        }}
      />
      <span className="relative z-10">{children}</span>
    </Badge>
  )
}
