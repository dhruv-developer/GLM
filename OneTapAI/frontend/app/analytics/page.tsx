"use client"

import { MainLayout } from "@/components/main-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  TrendingUp,
  TrendingDown,
  Activity,
  Clock,
  CheckCircle2,
  XCircle,
  Zap,
  Target,
  Award,
  BarChart3
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { motion } from "framer-motion"
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts"

// Mock data for charts
const taskCompletionData = [
  { name: "Mon", completed: 12, failed: 2, total: 14 },
  { name: "Tue", completed: 19, failed: 3, total: 22 },
  { name: "Wed", completed: 15, failed: 1, total: 16 },
  { name: "Thu", completed: 22, failed: 4, total: 26 },
  { name: "Fri", completed: 28, failed: 2, total: 30 },
  { name: "Sat", completed: 18, failed: 1, total: 19 },
  { name: "Sun", completed: 24, failed: 3, total: 27 }
]

const agentPerformanceData = [
  { name: "Communication", tasks: 45, successRate: 96, avgTime: 2.3 },
  { name: "Transportation", tasks: 32, successRate: 89, avgTime: 1.8 },
  { name: "Search", tasks: 58, successRate: 94, avgTime: 1.2 },
  { name: "Application", tasks: 23, successRate: 78, avgTime: 4.5 },
  { name: "Scheduling", tasks: 41, successRate: 91, avgTime: 2.1 }
]

const taskTypeDistribution = [
  { name: "Communication", value: 35, color: "#8b5cf6" },
  { name: "Transportation", value: 25, color: "#ec4899" },
  { name: "Search", value: 45, color: "#06b6d4" },
  { name: "Application", value: 18, color: "#f59e0b" },
  { name: "Scheduling", value: 32, color: "#10b981" }
]

const hourlyActivityData = [
  { hour: "00:00", tasks: 5 },
  { hour: "04:00", tasks: 2 },
  { hour: "08:00", tasks: 15 },
  { hour: "12:00", tasks: 28 },
  { hour: "16:00", tasks: 22 },
  { hour: "20:00", tasks: 18 }
]

const metrics = [
  {
    title: "Total Tasks",
    value: "1,234",
    change: "+12.5%",
    trend: "up",
    icon: Target,
    color: "text-blue-500"
  },
  {
    title: "Success Rate",
    value: "94.2%",
    change: "+2.4%",
    trend: "up",
    icon: Award,
    color: "text-green-500"
  },
  {
    title: "Avg. Completion",
    value: "2.3h",
    change: "-8.1%",
    trend: "down",
    icon: Clock,
    color: "text-purple-500"
  },
  {
    title: "Active Agents",
    value: "8",
    change: "+2",
    trend: "up",
    icon: Zap,
    color: "text-orange-500"
  }
]

export default function AnalyticsPage() {
  return (
    <MainLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-6"
      >
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold">Analytics</h1>
          <p className="text-muted-foreground mt-2">
            Comprehensive insights into your autonomous task performance
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {metrics.map((metric, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {metric.title}
                  </CardTitle>
                  <metric.icon className={`h-5 w-5 ${metric.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{metric.value}</div>
                  <div className="flex items-center mt-1">
                    {metric.trend === "up" ? (
                      <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-green-500 mr-1" />
                    )}
                    <span className={`text-sm ${metric.trend === "up" ? "text-green-500" : "text-green-500"}`}>
                      {metric.change}
                    </span>
                    <span className="text-xs text-muted-foreground ml-1">vs last month</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Task Completion Trends */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-purple-500" />
                Task Completion Trends
              </CardTitle>
              <CardDescription>Weekly task completion and failure rates</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={taskCompletionData}>
                  <defs>
                    <linearGradient id="colorCompleted" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorFailed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="name" className="text-muted-foreground" />
                  <YAxis className="text-muted-foreground" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px"
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="completed"
                    stroke="#8b5cf6"
                    fillOpacity={1}
                    fill="url(#colorCompleted)"
                  />
                  <Area
                    type="monotone"
                    dataKey="failed"
                    stroke="#ef4444"
                    fillOpacity={1}
                    fill="url(#colorFailed)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Task Type Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-blue-500" />
                Task Type Distribution
              </CardTitle>
              <CardDescription>Breakdown by task category</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={taskTypeDistribution}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {taskTypeDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: "8px"
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Agent Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-orange-500" />
              Agent Performance
            </CardTitle>
            <CardDescription>Performance metrics by agent type</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={agentPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-muted-foreground" />
                <YAxis className="text-muted-foreground" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px"
                  }}
                />
                <Legend />
                <Bar dataKey="tasks" fill="#8b5cf6" name="Tasks Completed" />
                <Bar dataKey="successRate" fill="#10b981" name="Success Rate %" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Hourly Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-cyan-500" />
              Hourly Activity
            </CardTitle>
            <CardDescription>Task execution frequency throughout the day</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={hourlyActivityData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="hour" className="text-muted-foreground" />
                <YAxis className="text-muted-foreground" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px"
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="tasks"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  dot={{ fill: "#06b6d4" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Performance Insights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Top Performer
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-2xl font-bold">Search Agent</div>
                <div className="text-sm text-muted-foreground">96% success rate</div>
                <div className="text-sm text-muted-foreground">58 tasks completed</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-blue-500" />
                Fastest Response
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-2xl font-bold">Search Agent</div>
                <div className="text-sm text-muted-foreground">1.2h avg time</div>
                <div className="text-sm text-muted-foreground">Quick completion</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="h-5 w-5 text-purple-500" />
                Most Improved
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-2xl font-bold">Application Agent</div>
                <div className="text-sm text-muted-foreground">+15% this month</div>
                <div className="text-sm text-muted-foreground">Rising performance</div>
              </div>
            </CardContent>
          </Card>
        </div>
      </motion.div>
    </MainLayout>
  )
}
