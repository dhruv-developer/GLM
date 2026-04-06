"use client"

import { MainLayout } from "@/components/main-layout"
import TaskResultDisplay from "@/components/TaskResultDisplay"
import TaskSummaryCard from "@/components/TaskSummaryCard"
import WebSearchResultsDisplay from "@/components/WebSearchResultsDisplay"
import TaskExecutionTimeline from "@/components/TaskExecutionTimeline"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Sparkles, ArrowLeft } from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"
import { TaskStatus, WebSearchResult } from "@/types"

// Demo data
const demoTaskStatus: TaskStatus = {
  execution_id: "demo-exec-123",
  status: "completed",
  progress: 1.0,
  completed_tasks: 5,
  total_tasks: 5,
  result: {
    summary: "Successfully completed web search for 'latest AI trends 2025' and compiled a comprehensive report with 8 relevant sources from various tech publications and research platforms.",
    agent_executions: [
      {
        task_id: "task-1",
        agent: "web_search_agent",
        action: "Search for 'latest AI trends 2025'",
        status: "completed",
        started_at: new Date(Date.now() - 30000).toISOString(),
        completed_at: new Date(Date.now() - 25000).toISOString(),
        output: "Found 8 relevant results"
      },
      {
        task_id: "task-2",
        agent: "data_agent",
        action: "Process and filter search results",
        status: "completed",
        started_at: new Date(Date.now() - 24000).toISOString(),
        completed_at: new Date(Date.now() - 20000).toISOString(),
        output: "Filtered down to 8 high-quality sources"
      },
      {
        task_id: "task-3",
        agent: "document_agent",
        action: "Compile findings into summary",
        status: "completed",
        started_at: new Date(Date.now() - 19000).toISOString(),
        completed_at: new Date(Date.now() - 15000).toISOString(),
        output: "Generated comprehensive summary"
      }
    ]
  },
  web_search_results: [
    {
      query: "latest AI trends 2025",
      results: [
        {
          title: "The Top AI Trends That Will Define 2025",
          url: "https://www.wired.com/story/ai-trends-2025/",
          snippet: "From multimodal models to AI agents, here are the key artificial intelligence trends shaping the future in 2025. Experts predict a shift towards more autonomous AI systems.",
          site_name: "Wired",
          published_date: "2025-03-15",
          author: "Jane Smith",
          thumbnail: "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=400&h=300&fit=crop"
        },
        {
          title: "AI in 2025: What to Expect from Artificial Intelligence This Year",
          url: "https://www.techcrunch.com/2025/01/20/ai-2025-predictions/",
          snippet: "Industry leaders share their predictions for AI in 2025, including advances in reasoning, memory, and task execution capabilities. The focus shifts from chatbots to autonomous agents.",
          site_name: "TechCrunch",
          published_date: "2025-01-20",
          author: "Alex Johnson",
          thumbnail: "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=300&fit=crop"
        },
        {
          title: "2025 AI Trends Report: Multimodal Models Take Center Stage",
          url: "https://www.technologyreview.com/2025/02/10/ai-trends-2025/",
          snippet: "MIT Technology Review's annual AI trends report highlights multimodal AI, autonomous agents, and improved reasoning as the key developments to watch in 2025.",
          site_name: "MIT Technology Review",
          published_date: "2025-02-10",
          thumbnail: "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=400&h=300&fit=crop"
        }
      ],
      total_results: 8,
      search_type: "web"
    }
  ],
  logs: [
    {
      log_id: "log-1",
      execution_id: "demo-exec-123",
      level: "INFO",
      message: "Task created: Search for latest AI trends",
      timestamp: new Date(Date.now() - 35000).toISOString()
    },
    {
      log_id: "log-2",
      execution_id: "demo-exec-123",
      level: "INFO",
      message: "Web search completed successfully",
      timestamp: new Date(Date.now() - 25000).toISOString()
    },
    {
      log_id: "log-3",
      execution_id: "demo-exec-123",
      level: "INFO",
      message: "Results processed and summarized",
      timestamp: new Date(Date.now() - 15000).toISOString()
    }
  ]
}

const demoTimelineTasks = [
  {
    task_id: "task-1",
    agent: "web_search_agent",
    action: "Search for 'latest AI trends 2025'",
    status: "completed",
    started_at: new Date(Date.now() - 30000).toISOString(),
    completed_at: new Date(Date.now() - 25000).toISOString()
  },
  {
    task_id: "task-2",
    agent: "data_agent",
    action: "Process and filter search results",
    status: "completed",
    started_at: new Date(Date.now() - 24000).toISOString(),
    completed_at: new Date(Date.now() - 20000).toISOString()
  },
  {
    task_id: "task-3",
    agent: "document_agent",
    action: "Compile findings into summary",
    status: "completed",
    started_at: new Date(Date.now() - 19000).toISOString(),
    completed_at: new Date(Date.now() - 15000).toISOString()
  },
  {
    task_id: "task-4",
    agent: "validation_agent",
    action: "Validate summary quality",
    status: "completed",
    started_at: new Date(Date.now() - 14000).toISOString(),
    completed_at: new Date(Date.now() - 10000).toISOString()
  },
  {
    task_id: "task-5",
    agent: "controller_agent",
    action: "Finalize and return results",
    status: "completed",
    started_at: new Date(Date.now() - 9000).toISOString(),
    completed_at: new Date(Date.now() - 5000).toISOString()
  }
]

export default function DemoPage() {
  return (
    <MainLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-8"
      >
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <Sparkles className="w-8 h-8 text-purple-500" />
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Task Results Display Demo
              </h1>
            </div>
            <p className="text-muted-foreground text-lg">
              Showcase of user-friendly task result components
            </p>
          </div>
          <Link href="/">
            <Button variant="outline" className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </Button>
          </Link>
        </div>

        {/* Task Summary Card */}
        <div className="space-y-3">
          <h2 className="text-2xl font-semibold">1. Task Summary Card</h2>
          <p className="text-muted-foreground">
            Shows a celebratory summary when tasks complete successfully
          </p>
          <TaskSummaryCard status={demoTaskStatus} />
        </div>

        {/* Web Search Results */}
        <div className="space-y-3">
          <h2 className="text-2xl font-semibold">2. Web Search Results Display</h2>
          <p className="text-muted-foreground">
            Enhanced display for web search results with thumbnails and rich metadata
          </p>
          <WebSearchResultsDisplay searchResults={demoTaskStatus.web_search_results || []} />
        </div>

        {/* Task Execution Timeline */}
        <div className="space-y-3">
          <h2 className="text-2xl font-semibold">3. Task Execution Timeline</h2>
          <p className="text-muted-foreground">
            Visual timeline showing execution steps with status indicators
          </p>
          <TaskExecutionTimeline tasks={demoTimelineTasks} />
        </div>

        {/* Task Result Display */}
        <div className="space-y-3">
          <h2 className="text-2xl font-semibold">4. Task Result Display</h2>
          <p className="text-muted-foreground">
            Intelligent display that adapts to different result types
          </p>
          <TaskResultDisplay result={demoTaskStatus.result} />
        </div>

        {/* All Components Together */}
        <Card className="border-2 border-primary/20">
          <CardHeader>
            <CardTitle>Complete Execution Monitor Example</CardTitle>
            <p className="text-muted-foreground">
              All components working together as they would in the actual monitor page
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            <TaskSummaryCard status={demoTaskStatus} />
            <TaskExecutionTimeline tasks={demoTimelineTasks} />
            <WebSearchResultsDisplay searchResults={demoTaskStatus.web_search_results || []} />
            <TaskResultDisplay result={demoTaskStatus.result} />
          </CardContent>
        </Card>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">🎨 Beautiful UI</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Modern, gradient-based design with smooth animations and hover effects
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">🔍 Smart Detection</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Automatically detects result type and displays with appropriate formatting
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">⚡ Responsive</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Works seamlessly on desktop, tablet, and mobile devices
              </p>
            </CardContent>
          </Card>
        </div>
      </motion.div>
    </MainLayout>
  )
}
