"use client"

import { useState, useEffect } from "react"
import {
  CheckCircle2,
  XCircle,
  Clock,
  Loader2,
  Copy,
  ExternalLink,
  RefreshCw,
  Zap,
  AlertCircle,
  Play,
  Pause,
  RotateCcw
} from "lucide-react"
import { getTaskStatus, executeTask } from "@/lib/api"
import { TaskStatus as TaskStatusType } from "@/types"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { motion, AnimatePresence } from "framer-motion"
import TaskResultDisplay from "@/components/TaskResultDisplay"
import TaskSummaryCard from "@/components/TaskSummaryCard"
import WebSearchResultsDisplay from "@/components/WebSearchResultsDisplay"
import ReasoningChainDisplay from "@/components/ReasoningChainDisplay"

interface ExecutionMonitorProps {
  executionId: string
  executionLink: string
  intent: string
}

export default function ExecutionMonitor({
  executionId,
  executionLink,
  intent,
}: ExecutionMonitorProps) {
  const [status, setStatus] = useState<TaskStatusType | null>(null)
  const [loading, setLoading] = useState(true)
  const [executing, setExecuting] = useState(false)
  const [copied, setCopied] = useState(false)
  const [autoExecuted, setAutoExecuted] = useState(false)
  const [reasoningChain, setReasoningChain] = useState<any>(null)

  const fetchStatus = async () => {
    try {
      const data = await getTaskStatus(executionId);
      setStatus(data);

      // Fetch reasoning chain if available
      try {
        const reasoningResponse = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/reasoning/${executionId}`
        );
        if (reasoningResponse.ok) {
          const reasoningData = await reasoningResponse.json();
          setReasoningChain(reasoningData.reasoning_chain);
        }
      } catch (error) {
        console.log("No reasoning chain available");
      }
    } catch (error) {
      console.error("Failed to fetch status:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    setExecuting(true);
    try {
      const token = executionLink.split("/").pop();
      await executeTask(token || "");
      await fetchStatus();
    } catch (error: any) {
      console.error("Execution failed:", error);
      alert(error.message || "Failed to execute task");
    } finally {
      setExecuting(false);
    }
  };

  const copyLink = () => {
    const fullLink = `${window.location.origin}${executionLink}`;
    navigator.clipboard.writeText(fullLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [executionId]);

  // Auto-execute if task is in pending or ready state (only once)
  useEffect(() => {
    if (status && (status.status === "pending" || status.status === "ready") && !executing && !autoExecuted) {
      setAutoExecuted(true);
      handleExecute();
    }
  }, [status, autoExecuted]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        >
          <Loader2 className="w-12 h-12 text-primary" />
        </motion.div>
      </div>
    );
  }

  const statusConfig = {
    pending: {
      color: "bg-yellow-500",
      textColor: "text-yellow-500",
      bg: "bg-yellow-500/10",
      icon: Clock,
      label: "Pending"
    },
    planning: {
      color: "bg-blue-500",
      textColor: "text-blue-500",
      bg: "bg-blue-500/10",
      icon: AlertCircle,
      label: "Planning"
    },
    ready: {
      color: "bg-purple-500",
      textColor: "text-purple-500",
      bg: "bg-purple-500/10",
      icon: Play,
      label: "Ready"
    },
    running: {
      color: "bg-purple-500",
      textColor: "text-purple-500",
      bg: "bg-purple-500/10",
      icon: Loader2,
      label: "Running"
    },
    completed: {
      color: "bg-green-500",
      textColor: "text-green-500",
      bg: "bg-green-500/10",
      icon: CheckCircle2,
      label: "Completed"
    },
    failed: {
      color: "bg-red-500",
      textColor: "text-red-500",
      bg: "bg-red-500/10",
      icon: XCircle,
      label: "Failed"
    },
    cancelled: {
      color: "bg-gray-500",
      textColor: "text-gray-500",
      bg: "bg-gray-500/10",
      icon: XCircle,
      label: "Cancelled"
    },
  };

  const currentStatus = status?.status || "pending";
  const config = statusConfig[currentStatus as keyof typeof statusConfig];
  const StatusIcon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Task Overview */}
      <Card className="border-2 border-primary/20">
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="flex items-center gap-2 mb-2">
                <Zap className="w-6 h-6 text-primary" />
                Task Overview
              </CardTitle>
              <CardDescription className="text-base">{intent}</CardDescription>
            </div>
            <Badge className={`${config.bg} ${config.textColor} border-0`}>
              <StatusIcon className={`w-4 h-4 mr-1 ${currentStatus === "running" ? "animate-spin" : ""}`} />
              {config.label}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-semibold">{status ? `${Math.round(status.progress * 100)}%` : "0%"}</span>
            </div>
            <Progress value={(status?.progress || 0) * 100} className="h-3" />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>{status?.completed_tasks || 0} tasks completed</span>
              <span>{status?.total_tasks || 0} total tasks</span>
            </div>
          </div>

          {/* Execution Link */}
          <div className="space-y-2">
            <label className="text-sm font-medium">Execution Link</label>
            <div className="flex gap-2">
              <div className="flex-1 flex items-center bg-muted rounded-lg px-4 py-2">
                <code className="text-sm font-mono truncate">
                  {`${window.location.origin}${executionLink}`}
                </code>
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={copyLink}
                title="Copy link"
              >
                <Copy className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="icon"
                asChild
                title="Open in new tab"
              >
                <a
                  href={executionLink}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </Button>
            </div>
            <AnimatePresence>
              {copied && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="text-sm text-green-500"
                >
                  Link copied to clipboard!
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Action Buttons */}
          {currentStatus === "ready" && (
            <Button
              onClick={handleExecute}
              disabled={executing}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
              size="lg"
            >
              {executing ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Executing...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-5 w-5" />
                  Execute Now
                </>
              )}
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Execution Logs */}
      {status && status.logs.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <RefreshCw className="w-5 h-5" />
                Execution Logs
              </CardTitle>
              <Button
                variant="outline"
                size="sm"
                onClick={fetchStatus}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 max-h-[400px] overflow-y-auto">
              {status.logs.map((log) => (
                <motion.div
                  key={log.log_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`p-4 rounded-lg ${
                    log.level === "ERROR"
                      ? "bg-destructive/10 border border-destructive/20"
                      : log.level === "WARNING"
                      ? "bg-yellow-500/10 border border-yellow-500/20"
                      : "bg-muted/50 border border-border"
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        {log.level}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(log.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm">{log.message}</p>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Reasoning Chain Display */}
      {reasoningChain && <ReasoningChainDisplay chain={reasoningChain} />}

      {/* Task Summary Card (shown when task is completed) */}
      {status && <TaskSummaryCard status={status} />}

      {/* Web Search Results (if available) */}
      {status?.web_search_results && status.web_search_results.length > 0 && (
        <WebSearchResultsDisplay searchResults={status.web_search_results} />
      )}

      {/* Result */}
      {status?.result && (
        <TaskResultDisplay 
          result={status.result} 
          executionId={executionId}
          generatedCode={status.generated_code}
          downloadFilename={status.download_filename}
        />
      )}

      {/* Error */}
      {status?.error && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="border-destructive/20 bg-destructive/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <XCircle className="w-6 h-6" />
                Execution Error
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-destructive/90">{status.error}</p>
              <div className="mt-4 flex gap-2">
                <Button variant="outline" size="sm">
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Retry
                </Button>
                <Button variant="outline" size="sm">
                  View Logs
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </motion.div>
  );
}
