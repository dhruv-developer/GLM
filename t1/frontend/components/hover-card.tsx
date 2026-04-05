"use client"

import { Card, CardContent } from "@/components/ui/card"
import { motion } from "framer-motion"
import { ReactNode } from "react"

interface HoverCardProps {
  children: ReactNode
  className?: string
  onClick?: () => void
}

export function HoverCard({ children, className = "", onClick }: HoverCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -5 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className={`cursor-pointer transition-all duration-300 hover:shadow-xl hover:shadow-primary/10 ${className}`}
        onClick={onClick}
      >
        <CardContent className="p-6">
          {children}
        </CardContent>
      </Card>
    </motion.div>
  )
}
