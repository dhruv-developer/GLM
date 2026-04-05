"use client"

import { useParams, useRouter, useSearchParams } from "next/navigation"
import { useEffect, useState } from "react"
import { MainLayout } from "@/components/main-layout"
import ExecutionMonitor from "@/components/ExecutionMonitor"
import { getTaskStatus } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Loader2, AlertCircle } from "lucide-react"
import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { TaskStatus } from "@/types"

export default function MonitorPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const executionId = params.executionId as string
  const [intent, setIntent] = useState<string>("")
  const [executionToken, setExecutionContext] = useState<string>("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>("")

  useEffect(() => {
    // Get token from query params if available
    const token = searchParams.get('token')
    if (token) {
      setExecutionContext(token)
    }

    fetchTaskDetails()
  }, [executionId, searchParams])

  const fetchTaskDetails = async () => {
    try {
      setLoading(true)
      const status: TaskStatus = await getTaskStatus(executionId)

      // Extract intent from the first log or use a default
      if (status.logs && status.logs.length > 0) {
        setIntent(status.logs[0].message)
      } else {
        setIntent("Task execution monitoring")
      }

      // Note: The execution token should be passed via query params or stored in the task
      // For now, we'll use executionId as a fallback (this won't work for actual execution)
      // The proper token should be stored when task is created and retrieved here
      setExecutionContext(executionId) // This should be the token, not executionId
    } catch (err: any) {
      setError(err.message || "Failed to load task details")
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          >
            <Loader2 className="w-12 h-12 text-primary" />
          </motion.div>
        </div>
      </MainLayout>
    )
  }

  if (error) {
    return (
      <MainLayout>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          <Button
            variant="outline"
            onClick={() => router.push("/")}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>

          <Card className="border-destructive/20 bg-destructive/5">
            <CardContent className="pt-6">
              <div className="flex items-start gap-4">
                <AlertCircle className="h-8 w-8 text-destructive flex-shrink-0 mt-1" />
                <div>
                  <h3 className="text-lg font-semibold text-destructive mb-2">
                    Failed to Load Task
                  </h3>
                  <p className="text-muted-foreground mb-4">{error}</p>
                  <Button
                    variant="outline"
                    onClick={() => router.push("/")}
                  >
                    Return to Dashboard
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </MainLayout>
    )
  }

  return (
    <MainLayout>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        <Button
          variant="outline"
          onClick={() => router.push("/")}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>

        <ExecutionMonitor
          executionId={executionId}
          executionLink={`/execute/${executionToken}`}
          intent={intent}
        />
      </motion.div>
    </MainLayout>
  )
}
