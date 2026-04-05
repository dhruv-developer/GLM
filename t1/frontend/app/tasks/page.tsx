"use client"

import { useState } from "react"
import { MainLayout } from "@/components/main-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Search,
  Filter,
  Download,
  RefreshCw,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Eye,
  ChevronDown,
  ChevronUp
} from "lucide-react"
import { motion } from "framer-motion"

const tasks = [
  {
    id: "1",
    intent: "Send birthday message to mom at 12 AM",
    status: "completed",
    progress: 100,
    createdAt: "2024-01-15T10:30:00Z",
    completedAt: "2024-01-15T12:00:00Z",
    agentType: "Communication Agent"
  },
  {
    id: "2",
    intent: "Book an Uber to the airport at 3 PM",
    status: "running",
    progress: 65,
    createdAt: "2024-01-15T09:00:00Z",
    completedAt: null,
    agentType: "Transportation Agent"
  },
  {
    id: "3",
    intent: "Find top 5 Italian restaurants nearby",
    status: "completed",
    progress: 100,
    createdAt: "2024-01-15T08:00:00Z",
    completedAt: "2024-01-15T08:15:00Z",
    agentType: "Search Agent"
  },
  {
    id: "4",
    intent: "Apply to Software Engineer position at Google",
    status: "pending",
    progress: 0,
    createdAt: "2024-01-15T07:00:00Z",
    completedAt: null,
    agentType: "Application Agent"
  },
  {
    id: "5",
    intent: "Schedule team meeting for tomorrow",
    status: "failed",
    progress: 45,
    createdAt: "2024-01-15T06:00:00Z",
    completedAt: null,
    agentType: "Scheduling Agent"
  },
  {
    id: "6",
    intent: "Analyze Q4 sales data and create report",
    status: "planning",
    progress: 15,
    createdAt: "2024-01-15T05:00:00Z",
    completedAt: null,
    agentType: "Analytics Agent"
  }
]

const statusConfig = {
  pending: { icon: Clock, color: "bg-yellow-500", textColor: "text-yellow-500", bg: "bg-yellow-500/10" },
  planning: { icon: AlertCircle, color: "bg-blue-500", textColor: "text-blue-500", bg: "bg-blue-500/10" },
  running: { icon: RefreshCw, color: "bg-purple-500", textColor: "text-purple-500", bg: "bg-purple-500/10" },
  completed: { icon: CheckCircle2, color: "bg-green-500", textColor: "text-green-500", bg: "bg-green-500/10" },
  failed: { icon: XCircle, color: "bg-red-500", textColor: "text-red-500", bg: "bg-red-500/10" }
}

export default function TasksPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [sortBy, setSortBy] = useState("createdAt")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")
  const [expandedTask, setExpandedTask] = useState<string | null>(null)

  const filteredTasks = tasks
    .filter(task => {
      const matchesSearch = task.intent.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesStatus = statusFilter === "all" || task.status === statusFilter
      return matchesSearch && matchesStatus
    })
    .sort((a, b) => {
      const aValue = a[sortBy as keyof typeof a]
      const bValue = b[sortBy as keyof typeof b]
      if (aValue === null || bValue === null) return 0
      if (sortOrder === "asc") return aValue > bValue ? 1 : -1
      return aValue < bValue ? 1 : -1
    })

  const stats = {
    total: tasks.length,
    completed: tasks.filter(t => t.status === "completed").length,
    running: tasks.filter(t => t.status === "running").length,
    failed: tasks.filter(t => t.status === "failed").length
  }

  return (
    <MainLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-6"
      >
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold">Tasks</h1>
            <p className="text-muted-foreground mt-2">
              Manage and monitor all your autonomous tasks
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
            <Button variant="outline" size="sm">
              <RefreshCw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Tasks</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Completed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-500">{stats.completed}</div>
              <div className="text-xs text-muted-foreground mt-1">{Math.round(stats.completed / stats.total * 100)}% success rate</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Running</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-500">{stats.running}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">Failed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-500">{stats.failed}</div>
            </CardContent>
          </Card>
        </div>

        {/* Filters and Search */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search tasks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full md:w-[180px]">
                  <Filter className="mr-2 h-4 w-4" />
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="planning">Planning</SelectItem>
                  <SelectItem value="running">Running</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-full md:w-[180px]">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="createdAt">Created Date</SelectItem>
                  <SelectItem value="progress">Progress</SelectItem>
                  <SelectItem value="status">Status</SelectItem>
                </SelectContent>
              </Select>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
              >
                {sortOrder === "asc" ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Tasks List */}
        <div className="space-y-4">
          {filteredTasks.map((task, index) => {
            const config = statusConfig[task.status as keyof typeof statusConfig]
            const StatusIcon = config.icon
            const isExpanded = expandedTask === task.id

            return (
              <motion.div
                key={task.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className={`cursor-pointer transition-all hover:shadow-lg ${isExpanded ? 'ring-2 ring-primary' : ''}`}>
                  <CardContent className="p-6">
                    <div className="flex items-start gap-4" onClick={() => setExpandedTask(isExpanded ? null : task.id)}>
                      <div className={`w-10 h-10 rounded-lg ${config.bg} flex items-center justify-center flex-shrink-0`}>
                        <StatusIcon className={`h-5 w-5 ${config.textColor}`} />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <h3 className="font-semibold text-lg mb-2">{task.intent}</h3>
                            <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                              <Badge variant="outline" className="text-xs">
                                {task.agentType}
                              </Badge>
                              <span>•</span>
                              <span>Created {new Date(task.createdAt).toLocaleDateString()}</span>
                            </div>
                          </div>

                          <div className="flex items-center gap-3">
                            <div className="text-right">
                              <div className="text-2xl font-bold">{task.progress}%</div>
                              <div className="text-xs text-muted-foreground">Complete</div>
                            </div>
                            <Button variant="ghost" size="icon">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="mt-4">
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                              style={{ width: `${task.progress}%` }}
                            />
                          </div>
                        </div>

                        {/* Expanded Details */}
                        {isExpanded && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            transition={{ duration: 0.3 }}
                            className="mt-4 pt-4 border-t border-border"
                          >
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <div className="text-muted-foreground mb-1">Status</div>
                                <Badge className={config.bg + " " + config.textColor}>
                                  {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                                </Badge>
                              </div>
                              <div>
                                <div className="text-muted-foreground mb-1">Created</div>
                                <div className="font-medium">{new Date(task.createdAt).toLocaleString()}</div>
                              </div>
                              <div>
                                <div className="text-muted-foreground mb-1">Completed</div>
                                <div className="font-medium">
                                  {task.completedAt ? new Date(task.completedAt).toLocaleString() : "N/A"}
                                </div>
                              </div>
                              <div>
                                <div className="text-muted-foreground mb-1">Agent</div>
                                <div className="font-medium">{task.agentType}</div>
                              </div>
                            </div>

                            <div className="flex gap-2 mt-4">
                              <Button size="sm" variant="outline">View Logs</Button>
                              <Button size="sm" variant="outline">Retry</Button>
                              <Button size="sm" variant="destructive">Cancel</Button>
                            </div>
                          </motion.div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}

          {filteredTasks.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">No tasks found matching your criteria</p>
              </CardContent>
            </Card>
          )}
        </div>
      </motion.div>
    </MainLayout>
  )
}
