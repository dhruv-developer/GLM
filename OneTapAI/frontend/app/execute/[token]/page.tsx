"use client"

import { useParams, useRouter, useSearchParams } from "next/navigation"
import { useEffect, useState } from "react"
import { MainLayout } from "@/components/main-layout"
import { executeTask, getTaskStatus } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Loader2, CheckCircle2, AlertCircle, ArrowLeft, FileText, Download, ExternalLink } from "lucide-react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface FinalResult {
  summary?: {
    title: string
    intent: string
    key_findings: string[]
    recommendations: string[]
    sources: Array<{ title: string; url: string }>
  }
  document?: {
    document?: string
    filename?: string
    download_url?: string
    format?: string
  }
}

export default function ExecutePage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = params.token as string
  const [loading, setLoading] = useState(true)
  const [executing, setExecuting] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [error, setError] = useState<string>("")
  const [executionId, setExecutionId] = useState<string>("")
  const [finalResult, setFinalResult] = useState<FinalResult | null>(null)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    // Check if execution already completed (from query params)
    const completedExecId = searchParams.get('execution_id')
    if (completedExecId) {
      setExecutionId(completedExecId)
      setCompleted(true)
      setLoading(false)
      fetchFinalResult(completedExecId)
    } else {
      handleExecution()
    }
  }, [token, searchParams])

  const fetchFinalResult = async (execId: string) => {
    try {
      const status = await getTaskStatus(execId)
      if (status.result && typeof status.result === 'object') {
        const result = status.result as any
        if (result.tasks) {
          // Find the document task output
          const documentTask = Object.values(result.tasks).find(
            (task: any) => task.agent === 'document' || task.agent === 'DOCUMENT'
          )
          if (documentTask && 'output' in documentTask) {
            setFinalResult((documentTask as any).output)
          }
        }
      }
    } catch (err) {
      console.error("Failed to fetch final result:", err)
    }
  }

  const handleExecution = async () => {
    try {
      setLoading(true)
      setExecuting(true)

      // Call the backend execute endpoint
      const response = await executeTask(token)
      const id = response.execution_id
      setExecutionId(id)

      // Monitor progress
      monitorExecution(id)

    } catch (err: any) {
      setError(err.message || "Failed to execute task")
      setExecuting(false)
      setLoading(false)
    }
  }

  const monitorExecution = async (execId: string) => {
    const checkInterval = setInterval(async () => {
      try {
        const status = await getTaskStatus(execId)
        setProgress(status.progress * 100)

        if (status.status === 'completed') {
          clearInterval(checkInterval)
          setCompleted(true)
          setExecuting(false)
          setLoading(false)
          await fetchFinalResult(execId)
        } else if (status.status === 'failed') {
          clearInterval(checkInterval)
          setError(status.error || "Task execution failed")
          setExecuting(false)
          setLoading(false)
        }
      } catch (err) {
        clearInterval(checkInterval)
        console.error("Error monitoring execution:", err)
      }
    }, 2000)
  }

  const renderFinalResult = () => {
    if (!finalResult) return null

    const { summary, document } = finalResult

    return (
      <div className="space-y-6">
        {summary && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-primary" />
                {summary.title}
              </CardTitle>
              <CardDescription>Generated from: {summary.intent}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {summary.key_findings && summary.key_findings.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Key Findings</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {summary.key_findings.map((finding, idx) => (
                      <li key={idx} className="text-sm">{finding}</li>
                    ))}
                  </ul>
                </div>
              )}

              {summary.recommendations && summary.recommendations.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Recommendations</h3>
                  <ol className="list-decimal list-inside space-y-1">
                    {summary.recommendations.map((rec, idx) => (
                      <li key={idx} className="text-sm">{rec}</li>
                    ))}
                  </ol>
                </div>
              )}

              {summary.sources && summary.sources.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Sources</h3>
                  <div className="space-y-2">
                    {summary.sources.map((source, idx) => (
                      <a
                        key={idx}
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-2 rounded border hover:bg-accent transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm flex-1">{source.title}</span>
                          <ExternalLink className="w-4 h-4 text-muted-foreground" />
                        </div>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {document && document.document && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Download className="w-5 h-5 text-primary" />
                Generated Document
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-muted rounded-lg">
                  <pre className="text-sm whitespace-pre-wrap font-mono">
                    {document.document}
                  </pre>
                </div>
                <Button
                  onClick={() => {
                    const blob = new Blob([document.document!], { type: 'text/plain' })
                    const url = URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = document.filename || 'research_summary.txt'
                    a.click()
                    URL.revokeObjectURL(url)
                  }}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download Document
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        <Button
          onClick={() => router.push("/")}
          variant="outline"
          className="w-full"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
      </div>
    )
  }

  return (
    <MainLayout>
      <div className="flex items-center justify-center min-h-[500px] p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-3xl"
        >
          <Card className="border-2">
            <CardContent className="pt-12 pb-12">
              <div className="flex flex-col items-center text-center space-y-6">
                {loading && (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <Loader2 className="w-16 h-16 text-primary" />
                    </motion.div>
                    <div>
                      <h2 className="text-2xl font-bold mb-2">
                        {executing ? "Processing Your Request" : "Starting Task"}
                      </h2>
                      <p className="text-muted-foreground">
                        {executing
                          ? `Analyzing and generating comprehensive results... ${progress.toFixed(0)}%`
                          : "Please wait while we process your request..."
                        }
                      </p>
                      {executing && (
                        <div className="w-full max-w-md mx-auto mt-4">
                          <div className="h-2 bg-muted rounded-full overflow-hidden">
                            <motion.div
                              className="h-full bg-primary"
                              style={{ width: `${progress}%` }}
                              animate={{ width: `${progress}%` }}
                              transition={{ duration: 0.5 }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </>
                )}

                {completed && !finalResult && (
                  <>
                    <CheckCircle2 className="w-16 h-16 text-green-500" />
                    <div>
                      <h2 className="text-2xl font-bold mb-2 text-green-500">Processing Complete!</h2>
                      <p className="text-muted-foreground">Loading your results...</p>
                    </div>
                  </>
                )}

                {error && (
                  <>
                    <AlertCircle className="w-16 h-16 text-destructive" />
                    <div>
                      <h2 className="text-2xl font-bold mb-2 text-destructive">Execution Failed</h2>
                      <p className="text-muted-foreground mb-4">{error}</p>
                      <Button
                        onClick={() => router.push("/")}
                        variant="outline"
                      >
                        <ArrowLeft className="h-4 w-4 mr-2" />
                        Back to Dashboard
                      </Button>
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          {completed && renderFinalResult()}
        </motion.div>
      </div>
    </MainLayout>
  )
}
