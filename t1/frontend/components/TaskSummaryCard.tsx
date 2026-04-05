"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, Clock, TrendingUp, Zap, Target, Award } from "lucide-react"
import { motion } from "framer-motion"
import { TaskStatus } from "@/types"

interface TaskSummaryCardProps {
  status: TaskStatus
}

export default function TaskSummaryCard({ status }: TaskSummaryCardProps) {
  if (!status || status.status !== "completed") {
    return null
  }

  // Calculate duration
  const calculateDuration = () => {
    if (!status.logs || status.logs.length === 0) return null

    const firstLog = status.logs[0]
    const lastLog = status.logs[status.logs.length - 1]
    const start = new Date(firstLog.timestamp)
    const end = new Date(lastLog.timestamp)
    const duration = Math.floor((end.getTime() - start.getTime()) / 1000)

    if (duration < 60) return `${duration} seconds`
    if (duration < 3600) return `${Math.floor(duration / 60)} minutes`
    return `${Math.floor(duration / 3600)} hours`
  }

  const duration = calculateDuration()

  // Count log levels
  const logCounts = status.logs.reduce((acc, log) => {
    acc[log.level] = (acc[log.level] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const stats = [
    {
      icon: CheckCircle2,
      label: "Tasks Completed",
      value: status.completed_tasks,
      color: "text-green-500",
      bgColor: "bg-green-500/10"
    },
    {
      icon: Target,
      label: "Total Tasks",
      value: status.total_tasks,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10"
    },
    {
      icon: TrendingUp,
      label: "Success Rate",
      value: `${Math.round((status.completed_tasks / status.total_tasks) * 100)}%`,
      color: "text-purple-500",
      bgColor: "bg-purple-500/10"
    },
    ...(duration ? [{
      icon: Clock,
      label: "Total Duration",
      value: duration,
      color: "text-orange-500",
      bgColor: "bg-orange-500/10"
    }] as const : [])
  ]

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="border-gradient-to-r from-green-500/20 to-blue-500/20 bg-gradient-to-br from-green-500/5 to-blue-500/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="w-6 h-6 text-yellow-500" />
            Task Execution Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Success Message */}
          <div className="text-center py-4">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 mb-4"
            >
              <CheckCircle2 className="w-10 h-10 text-white" />
            </motion.div>
            <h3 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              Task Completed Successfully!
            </h3>
            <p className="text-muted-foreground mt-2">
              All {status.total_tasks} tasks were executed successfully
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {stats.map((stat, idx) => {
              const Icon = stat.icon
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 * idx }}
                  className={`rounded-lg p-4 ${stat.bgColor} border border-current/10`}
                >
                  <div className={`flex items-center gap-2 mb-2 ${stat.color}`}>
                    <Icon className="w-5 h-5" />
                    <span className="text-xs font-medium">{stat.label}</span>
                  </div>
                  <div className={`text-2xl font-bold ${stat.color}`}>
                    {stat.value}
                  </div>
                </motion.div>
              )
            })}
          </div>

          {/* Log Summary */}
          {Object.keys(logCounts).length > 0 && (
            <div className="pt-4 border-t">
              <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                <Zap className="w-4 h-4" />
                Activity Summary
              </h4>
              <div className="flex flex-wrap gap-2">
                {Object.entries(logCounts).map(([level, count]) => (
                  <Badge
                    key={level}
                    variant="outline"
                    className={
                      level === "ERROR"
                        ? "bg-red-500/10 text-red-500 border-red-500/20"
                        : level === "WARNING"
                        ? "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
                        : level === "INFO"
                        ? "bg-blue-500/10 text-blue-500 border-blue-500/20"
                        : "bg-gray-500/10 text-gray-500 border-gray-500/20"
                    }
                  >
                    {level}: {count}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
