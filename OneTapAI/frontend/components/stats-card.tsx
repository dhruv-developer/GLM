"use client"

import { Card, CardContent } from "@/components/ui/card"
import { LucideIcon } from "lucide-react"
import { motion } from "framer-motion"
import { useEffect, useState } from "react"

interface StatsCardProps {
  title: string
  value: string | number
  change?: string
  icon: LucideIcon
  color?: string
  delay?: number
}

export function StatsCard({
  title,
  value,
  change,
  icon: Icon,
  color = "text-primary",
  delay = 0
}: StatsCardProps) {
  const [animatedValue, setAnimatedValue] = useState(0)
  const numericValue = typeof value === "number" ? value : parseFloat(value.replace(/[^\d.]/g, "")) || 0

  useEffect(() => {
    if (typeof value === "number") {
      const duration = 1000
      const steps = 60
      const stepValue = numericValue / steps
      let current = 0

      const timer = setInterval(() => {
        current += stepValue
        if (current >= numericValue) {
          setAnimatedValue(numericValue)
          clearInterval(timer)
        } else {
          setAnimatedValue(Math.floor(current))
        }
      }, duration / steps)

      return () => clearInterval(timer)
    }
  }, [numericValue, value])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
    >
      <Card className="hover:shadow-lg transition-all duration-300 hover:scale-105">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="space-y-2 flex-1">
              <p className="text-sm font-medium text-muted-foreground">{title}</p>
              <div className="flex items-baseline gap-2">
                <p className="text-3xl font-bold">
                  {typeof value === "number" ? animatedValue : value}
                </p>
                {change && (
                  <span className="text-sm text-green-500">{change}</span>
                )}
              </div>
            </div>
            <div className={`w-12 h-12 rounded-lg bg-gradient-to-r from-purple-500/10 to-pink-500/10 flex items-center justify-center ${color}`}>
              <Icon className="w-6 h-6" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
