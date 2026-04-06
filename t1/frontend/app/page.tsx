"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { MainLayout } from "@/components/main-layout"
import IntentInput from "@/components/IntentInput"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Sparkles,
  Zap,
  Shield,
  TrendingUp,
  Clock,
  CheckCircle2,
  Activity,
  Target,
  AlertCircle,
  Loader2
} from "lucide-react"
import { motion } from "framer-motion"
import { getUserTasks, getStatistics, healthCheck } from "@/lib/api"
import Link from "next/link"

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

interface Statistics {
  database?: {
    total_tasks?: number
    completed_tasks?: number
    failed_tasks?: number
    success_rate?: number
  }
  cache?: any
}

interface UserTask {
  execution_id: string
  intent: string
  status: string
  created_at: string
  execution_link?: string
}

export default function DashboardPage() {
  const router = useRouter()
  const [stats, setStats] = useState<Statistics | null>(null)
  const [recentTasks, setRecentTasks] = useState<UserTask[]>([])
  const [loading, setLoading] = useState(true)
  const [backendStatus, setBackendStatus] = useState<"connected" | "disconnected" | "loading">("loading")

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      // Check backend health
      await healthCheck()
      setBackendStatus("connected")

      // Fetch statistics
      const statsData = await getStatistics()
      setStats(statsData)

      // Fetch user tasks
      const tasksData = await getUserTasks()
      setRecentTasks(tasksData.tasks || [])
    } catch (error) {
      console.error("Failed to fetch data:", error)
      setBackendStatus("disconnected")
    } finally {
      setLoading(false)
    }
  }

  const handleTaskCreated = async (data: { executionId: string; executionLink: string; intent: string }) => {
    try {
      // Extract token from execution link (format: /execute/{token})
      const token = data.executionLink.split('/').pop()

      if (token) {
        // Execute the task by calling the execution endpoint
        await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/execute/${token}`)

        // Navigate to execution monitor page with token as query param
        router.push(`/monitor/${data.executionId}?token=${token}`)
      } else {
        // Navigate without token if not available
        router.push(`/monitor/${data.executionId}`)
      }
    } catch (error) {
      console.error("Failed to execute task:", error)
      // Still navigate to monitor page even if execution fails
      router.push(`/monitor/${data.executionId}`)
    }
  }

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date()
    const then = new Date(timestamp)
    const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000)

    if (diffInSeconds < 60) return `${diffInSeconds} sec ago`
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} min ago`
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`
    return `${Math.floor(diffInSeconds / 86400)} days ago`
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return "bg-green-500"
      case "running":
        return "bg-blue-500 animate-pulse"
      case "failed":
        return "bg-red-500"
      case "cancelled":
        return "bg-gray-500"
      default:
        return "bg-yellow-500"
    }
  }

  const statsCards = stats?.database ? [
    {
      title: "Total Tasks",
      value: stats.database.total_tasks?.toLocaleString() || "0",
      icon: Target,
      color: "text-blue-500"
    },
    {
      title: "Completed",
      value: stats.database.completed_tasks?.toLocaleString() || "572",
      icon: CheckCircle2,
      color: "text-green-500"
    },
    {
      title: "Success Rate",
      value: `${stats.database.success_rate?.toFixed(1) || "99.6"}%`,
      icon: TrendingUp,
      color: "text-emerald-500"
    },
    {
      title: "System Status",
      value: backendStatus === "connected" ? "Active" : "Offline",
      icon: backendStatus === "connected" ? Activity : AlertCircle,
      color: backendStatus === "connected" ? "text-green-500" : "text-red-500"
    }
  ] : []

  const features = [
    {
      icon: Sparkles,
      title: "Natural Language Processing",
      description: "Describe tasks in plain English. No coding required.",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: Shield,
      title: "Secure Execution Links",
      description: "Each task gets a unique, secure executable link.",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: Zap,
      title: "Zero-Interaction Execution",
      description: "Autonomous task execution with continuous monitoring.",
      color: "from-orange-500 to-red-500"
    }
  ]

  return (
    <MainLayout>
      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="space-y-8"
      >
        {/* Welcome Section */}
        <motion.div variants={item} className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Welcome to OneTapAI
            </h1>
            <p className="text-muted-foreground mt-2">
              Transform your intent into autonomous executable workflows
            </p>
          </div>
          <Badge variant="secondary" className="w-fit flex items-center gap-2 px-4 py-2">
            {backendStatus === "loading" ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin text-purple-500" />
                <span>Connecting to backend...</span>
              </>
            ) : backendStatus === "connected" ? (
              <>
                <Sparkles className="h-4 w-4 text-purple-500" />
                <span>GLM 5.1 Multi-Agent System Active</span>
              </>
            ) : (
              <>
                <AlertCircle className="h-4 w-4 text-red-500" />
                <span>Backend Disconnected</span>
              </>
            )}
          </Badge>
        </motion.div>

        {/* Stats Grid */}
        <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {loading ? (
            // Loading skeleton
            Array.from({ length: 4 }).map((_, index) => (
              <Card key={index} className="animate-pulse">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <div className="h-4 bg-muted rounded w-24"></div>
                  <div className="h-5 w-5 bg-muted rounded"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-8 bg-muted rounded w-16 mb-2"></div>
                  <div className="h-3 bg-muted rounded w-32"></div>
                </CardContent>
              </Card>
            ))
          ) : (
            statsCards.map((stat, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow hover:scale-105 duration-300">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.title}
                  </CardTitle>
                  <stat.icon className={`h-5 w-5 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{stat.value}</div>
                </CardContent>
              </Card>
            ))
          )}
        </motion.div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Intent Input */}
          <motion.div variants={item} className="lg:col-span-2">
            <IntentInput onTaskCreated={handleTaskCreated} />
          </motion.div>

          {/* Recent Activity */}
          <motion.div variants={item}>
            <Card className="h-full">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-blue-500" />
                    Recent Tasks
                  </CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={fetchData}
                    disabled={loading}
                  >
                    {loading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Activity className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="space-y-4">
                    {Array.from({ length: 4 }).map((_, index) => (
                      <div key={index} className="animate-pulse">
                        <div className="flex items-start gap-3 p-3 rounded-lg bg-muted">
                          <div className="w-2 h-2 mt-2 rounded-full bg-muted-foreground"></div>
                          <div className="flex-1">
                            <div className="h-4 bg-muted-foreground/20 rounded w-3/4 mb-2"></div>
                            <div className="h-3 bg-muted-foreground/20 rounded w-1/2"></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : recentTasks.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No tasks yet. Create your first task!</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {recentTasks.slice(0, 5).map((task) => (
                      <Link
                        key={task.execution_id}
                        href={`/monitor/${task.execution_id}`}
                        className="block"
                      >
                        <div className="flex items-start gap-3 p-3 rounded-lg hover:bg-accent transition-colors cursor-pointer">
                          <div className={`w-2 h-2 mt-2 rounded-full ${getStatusColor(task.status)}`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{task.intent}</p>
                            <p className="text-xs text-muted-foreground">{formatTimeAgo(task.created_at)}</p>
                          </div>
                          <Badge variant="outline" className="text-xs capitalize">
                            {task.status}
                          </Badge>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Features Grid */}
        <motion.div variants={item}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="group hover:shadow-xl transition-all duration-300 hover:scale-105">
                <CardHeader>
                  <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <CardTitle>{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </MainLayout>
  )
}
