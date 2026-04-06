"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, Clock, Loader2, XCircle, AlertCircle } from "lucide-react"
import { motion } from "framer-motion"
import { TaskNode, AgentExecution } from "@/types"

interface TaskExecutionTimelineProps {
  tasks: TaskNode[]
  currentTask?: string
}

export default function TaskExecutionTimeline({ tasks, currentTask }: TaskExecutionTimelineProps) {
  const getTaskStatus = (task: TaskNode) => {
    if (task.status === "completed") return "completed"
    if (task.status === "running") return "running"
    if (task.status === "failed") return "failed"
    if (task.status === "cancelled") return "cancelled"
    return "pending"
  }

  const getStatusConfig = (status: string) => {
    switch (status) {
      case "completed":
        return {
          icon: CheckCircle2,
          color: "text-green-500",
          bgColor: "bg-green-500/10",
          borderColor: "border-green-500/20",
          label: "Completed"
        }
      case "running":
        return {
          icon: Loader2,
          color: "text-blue-500",
          bgColor: "bg-blue-500/10",
          borderColor: "border-blue-500/20",
          label: "Running"
        }
      case "failed":
        return {
          icon: XCircle,
          color: "text-red-500",
          bgColor: "bg-red-500/10",
          borderColor: "border-red-500/20",
          label: "Failed"
        }
      case "cancelled":
        return {
          icon: XCircle,
          color: "text-gray-500",
          bgColor: "bg-gray-500/10",
          borderColor: "border-gray-500/20",
          label: "Cancelled"
        }
      default:
        return {
          icon: Clock,
          color: "text-yellow-500",
          bgColor: "bg-yellow-500/10",
          borderColor: "border-yellow-500/20",
          label: "Pending"
        }
    }
  }

  const getAgentBadgeColor = (agent: string) => {
    const colors: Record<string, string> = {
      "api_agent": "bg-blue-500/10 text-blue-500 border-blue-500/20",
      "data_agent": "bg-green-500/10 text-green-500 border-green-500/20",
      "web_search_agent": "bg-purple-500/10 text-purple-500 border-purple-500/20",
      "web_automation_agent": "bg-orange-500/10 text-orange-500 border-orange-500/20",
      "communication_agent": "bg-pink-500/10 text-pink-500 border-pink-500/20",
      "scheduler_agent": "bg-cyan-500/10 text-cyan-500 border-cyan-500/20",
      "validation_agent": "bg-indigo-500/10 text-indigo-500 border-indigo-500/20",
      "controller_agent": "bg-red-500/10 text-red-500 border-red-500/20",
      "document_agent": "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    }
    return colors[agent] || "bg-gray-500/10 text-gray-500 border-gray-500/20"
  }

  const formatAgentName = (agent: string) => {
    return agent
      .split("_")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ")
  }

  if (!tasks || tasks.length === 0) {
    return null
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          Execution Steps
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {tasks.map((task, index) => {
            const status = getTaskStatus(task)
            const config = getStatusConfig(status)
            const StatusIcon = config.icon
            const isCurrent = task.task_id === currentTask

            return (
              <motion.div
                key={task.task_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`relative pl-8 pb-4 ${index < tasks.length - 1 ? "border-l-2 border-muted" : ""}`}
              >
                {/* Status indicator */}
                <div className="absolute left-0 top-0 -translate-x-1/2">
                  <div className={`p-2 rounded-full ${config.bgColor} ${config.borderColor} border-2 ${isCurrent ? "ring-2 ring-primary" : ""}`}>
                    <StatusIcon className={`w-4 h-4 ${config.color} ${status === "running" ? "animate-spin" : ""}`} />
                  </div>
                </div>

                {/* Task content */}
                <div className={`rounded-lg p-4 ${config.bgColor} ${config.borderColor} border ${isCurrent ? "ring-2 ring-primary ring-offset-2" : ""}`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className={getAgentBadgeColor(task.agent)}>
                          {formatAgentName(task.agent)}
                        </Badge>
                        <Badge variant="outline" className={`${config.bgColor} ${config.color} border-0`}>
                          {config.label}
                        </Badge>
                        {isCurrent && (
                          <Badge className="bg-primary text-primary-foreground">
                            Current
                          </Badge>
                        )}
                      </div>
                      <h4 className="font-medium">{task.action}</h4>
                    </div>
                  </div>

                  {/* Timestamps */}
                  <div className="flex gap-4 text-xs text-muted-foreground mt-2">
                    {task.started_at && (
                      <span>Started: {new Date(task.started_at).toLocaleTimeString()}</span>
                    )}
                    {task.completed_at && (
                      <span>Completed: {new Date(task.completed_at).toLocaleTimeString()}</span>
                    )}
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
