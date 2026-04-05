"use client"

import { motion } from "framer-motion"

interface PulseRingProps {
  className?: string
  color?: string
}

export function PulseRing({ className = "", color = "bg-primary" }: PulseRingProps) {
  return (
    <div className={`relative ${className}`}>
      <motion.div
        className={`absolute inset-0 rounded-full ${color}`}
        animate={{
          scale: [1, 1.5, 2],
          opacity: [0.5, 0.3, 0],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeOut",
        }}
      />
      <motion.div
        className={`absolute inset-0 rounded-full ${color}`}
        animate={{
          scale: [1, 1.3, 1.6],
          opacity: [0.6, 0.4, 0.1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeOut",
          delay: 0.5,
        }}
      />
    </div>
  )
}
