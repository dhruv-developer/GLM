"use client"

import { motion } from "framer-motion"

interface GradientBgProps {
  className?: string
}

export function GradientBg({ className = "" }: GradientBgProps) {
  return (
    <div className={`fixed inset-0 -z-10 ${className}`}>
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-purple-500/5 via-pink-500/5 to-blue-500/5"
        animate={{
          backgroundPosition: ["0% 0%", "100% 100%", "0% 0%"],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear",
        }}
      />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-purple-500/10 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-5" />
    </div>
  )
}
