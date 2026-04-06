"use client"

import { useState, useEffect } from "react"
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
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
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
  ChevronUp,
  Trash2,
  Trash
} from "lucide-react"
import { motion } from "framer-motion"
import { getUserTasks, deleteTask, deleteRecentTasks, clearAllTasks } from "@/lib/api"
import { toast } from "sonner"

interface Task {
  execution_id: string
  intent: string
  status: string
  progress: number
  created_at: string
  completed_at?: string
  user_id: string
  result?: any
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [sortBy, setSortBy] = useState("created_at")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")
  const [expandedTask, setExpandedTask] = useState<string | null>(null)
  const [deletingTask, setDeletingTask] = useState<string | null>(null)

  const statusConfig = {
    pending: { icon: Clock, bg: "bg-yellow-100", textColor: "text-yellow-800" },
    planning: { icon: AlertCircle, bg: "bg-blue-100", textColor: "text-blue-800" },
    running: { icon: RefreshCw, bg: "bg-purple-100", textColor: "text-purple-800" },
    completed: { icon: CheckCircle2, bg: "bg-green-100", textColor: "text-green-800" },
    failed: { icon: XCircle, bg: "bg-red-100", textColor: "text-red-800" },
  }

  const fetchTasks = async () => {
    try {
      setLoading(true)
      const response = await getUserTasks()
      setTasks(response.tasks || [])
    } catch (error) {
      console.error("Failed to fetch tasks:", error)
      toast.error("Failed to load tasks")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTasks()
  }, [])

  const handleDeleteTask = async (executionId: string) => {
    try {
      setDeletingTask(executionId)
      await deleteTask(executionId)
      setTasks(tasks.filter(task => task.execution_id !== executionId))
      toast.success("Task deleted successfully")
    } catch (error) {
      console.error("Failed to delete task:", error)
      toast.error("Failed to delete task")
    } finally {
      setDeletingTask(null)
    }
  }

  const handleDeleteRecentTasks = async () => {
    try {
      const response = await deleteRecentTasks()
      toast.success(`Deleted ${response.deleted_count} recent tasks`)
      await fetchTasks() // Refresh the list
    } catch (error) {
      console.error("Failed to delete recent tasks:", error)
      toast.error("Failed to delete recent tasks")
    }
  }

  const handleClearAllTasks = async () => {
    try {
      const response = await clearAllTasks()
      toast.success(`Cleared ${response.deleted_count} tasks`)
      setTasks([]) // Clear the local list
    } catch (error) {
      console.error("Failed to clear all tasks:", error)
      toast.error("Failed to clear all tasks")
    }
  }

  const filteredTasks = tasks
    .filter(task => {
      const matchesSearch = task.intent.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = statusFilter === "all" || task.status === statusFilter
      return matchesSearch && matchesStatus
    })
    .sort((a, b) => {
      const aValue = a[sortBy as keyof Task]
      const bValue = b[sortBy as keyof Task]
      const modifier = sortOrder === "asc" ? 1 : -1
      return aValue > bValue ? modifier : -modifier
    })

  return (
    <MainLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-6"
      >
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Tasks</h1>
            <p className="text-muted-foreground">Manage and monitor your task executions</p>
          </div>
          <div className="flex gap-2">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="outline" size="sm">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete Recent
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Delete Recent Tasks?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will delete your last 10 tasks. This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleDeleteRecentTasks}>Delete</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>

            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" size="sm">
                  <Trash className="mr-2 h-4 w-4" />
                  Clear All
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Clear All Tasks?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will permanently delete all your tasks. This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={handleClearAllTasks}>Clear All</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>

            <Button variant="outline" size="sm" onClick={fetchTasks} disabled={loading}>
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search tasks..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
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
                  <SelectItem value="created_at">Created Date</SelectItem>
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
          {loading ? (
            <div className="text-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
              <p className="text-muted-foreground">Loading tasks...</p>
            </div>
          ) : filteredTasks.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground">No tasks found matching your criteria</p>
              </CardContent>
            </Card>
          ) : (
            filteredTasks.map((task, index) => {
              const config = statusConfig[task.status as keyof typeof statusConfig] || statusConfig.pending
              const StatusIcon = config.icon
              const isExpanded = expandedTask === task.execution_id

              return (
                <motion.div
                  key={task.execution_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card className={`cursor-pointer transition-all hover:shadow-lg ${isExpanded ? 'ring-2 ring-primary' : ''}`}>
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4" onClick={() => setExpandedTask(isExpanded ? null : task.execution_id)}>
                        <div className={`w-10 h-10 rounded-lg ${config.bg} flex items-center justify-center flex-shrink-0`}>
                          <StatusIcon className={`h-5 w-5 ${config.textColor}`} />
                        </div>

                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <h3 className="font-semibold text-lg mb-2">{task.intent}</h3>
                              <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
                                <Badge variant="outline" className="text-xs">
                                  {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                                </Badge>
                                <span>•</span>
                                <span>Created {new Date(task.created_at).toLocaleDateString()}</span>
                              </div>
                            </div>

                            <div className="flex items-center gap-3">
                              <div className="text-right">
                                <div className="text-2xl font-bold">{task.progress || 0}%</div>
                                <div className="text-xs text-muted-foreground">Complete</div>
                              </div>
                              
                              <AlertDialog>
                                <AlertDialogTrigger asChild>
                                  <Button 
                                    variant="ghost" 
                                    size="icon"
                                    onClick={(e) => e.stopPropagation()}
                                    disabled={deletingTask === task.execution_id}
                                  >
                                    <Trash2 className="h-4 w-4" />
                                  </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                  <AlertDialogHeader>
                                    <AlertDialogTitle>Delete Task?</AlertDialogTitle>
                                    <AlertDialogDescription>
                                      Are you sure you want to delete this task? This action cannot be undone.
                                    </AlertDialogDescription>
                                  </AlertDialogHeader>
                                  <AlertDialogFooter>
                                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                                    <AlertDialogAction 
                                      onClick={() => handleDeleteTask(task.execution_id)}
                                      className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                    >
                                      Delete
                                    </AlertDialogAction>
                                  </AlertDialogFooter>
                                </AlertDialogContent>
                              </AlertDialog>
                            </div>
                          </div>

                          {/* Progress Bar */}
                          <div className="mt-4">
                            <div className="h-2 bg-muted rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                                style={{ width: `${task.progress || 0}%` }}
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
                                  <div className="font-medium">{new Date(task.created_at).toLocaleString()}</div>
                                </div>
                                <div>
                                  <div className="text-muted-foreground mb-1">Completed</div>
                                  <div className="font-medium">
                                    {task.completed_at ? new Date(task.completed_at).toLocaleString() : "N/A"}
                                  </div>
                                </div>
                                <div>
                                  <div className="text-muted-foreground mb-1">Task ID</div>
                                  <div className="font-medium text-xs">{task.execution_id.slice(0, 8)}...</div>
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
            })
          )}
        </div>
      </motion.div>
    </MainLayout>
  )
}
