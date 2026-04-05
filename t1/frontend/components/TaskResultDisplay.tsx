"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, ChevronDown, ChevronRight, ExternalLink, FileText, Globe, Search, Bot, Code2, Copy, Check, Download } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { WebSearchResult, SearchResultItem } from "@/types"

interface TaskResultDisplayProps {
  result: any
  executionId?: string
  generatedCode?: string
  downloadFilename?: string
}

type ResultType = "web_search" | "agent_execution" | "text" | "json" | "error"

export default function TaskResultDisplay({ result, executionId, generatedCode, downloadFilename }: TaskResultDisplayProps) {
  const [showRawJson, setShowRawJson] = useState(false)
  const [copied, setCopied] = useState(false)
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev)
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId)
      } else {
        newSet.add(sectionId)
      }
      return newSet
    })
  }

  const copyToClipboard = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadCode = () => {
    const codeToDownload = generatedCode || result?.code || result?.output?.code
    const filename = downloadFilename || result?.filename || "generated_code.py"
    
    if (!codeToDownload) {
      alert("No code available to download")
      return
    }
    
    const blob = new Blob([codeToDownload], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const downloadFromServer = async () => {
    if (!executionId) {
      alert("No execution ID available")
      return
    }
    
    try {
      const response = await fetch(`/api/v1/download/${executionId}`)
      if (!response.ok) {
        throw new Error("Download failed")
      }
      
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = downloadFilename || "generated_code.py"
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error("Download failed:", error)
      alert("Download failed. Please try again.")
    }
  }

  // Detect result type
  const detectResultType = (): ResultType => {
    if (!result) return "json"

    // Check for web search results
    if (result.query && result.results && Array.isArray(result.results)) {
      return "web_search"
    }

    // Check for agent execution
    if (result.agent_executions && Array.isArray(result.agent_executions)) {
      return "agent_execution"
    }

    // Check for single agent execution
    if (result.agent && result.action && result.status) {
      return "agent_execution"
    }

    // Check if it's a simple text result
    if (typeof result === "string") {
      return "text"
    }

    // Check if it has a summary or final_answer field
    if (result.summary || result.final_answer || result.answer) {
      return "text"
    }

    return "json"
  }

  const resultType = detectResultType()

  // Render web search results
  const renderWebSearchResults = (searchResult: WebSearchResult) => {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
          <Search className="w-4 h-4" />
          <span>Found {searchResult.total_results || searchResult.results.length} results for "{searchResult.query}"</span>
          {searchResult.search_type && (
            <Badge variant="secondary" className="ml-2">
              {searchResult.search_type}
            </Badge>
          )}
        </div>

        <div className="space-y-3">
          {searchResult.results.map((item: SearchResultItem, idx: number) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow bg-card"
            >
              <div className="flex items-start gap-3">
                {item.thumbnail && (
                  <img
                    src={item.thumbnail}
                    alt=""
                    className="w-16 h-16 rounded object-cover flex-shrink-0"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 hover:underline"
                  >
                    <h4 className="font-medium text-blue-600 dark:text-blue-400 line-clamp-2">
                      {item.title}
                    </h4>
                    <ExternalLink className="w-3 h-3 flex-shrink-0" />
                  </a>

                  <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                    {item.site_name && (
                      <span className="font-medium">{item.site_name}</span>
                    )}
                    {item.published_date && (
                      <span>• {new Date(item.published_date).toLocaleDateString()}</span>
                    )}
                    {item.author && (
                      <span>• {item.author}</span>
                    )}
                  </div>

                  <p className="text-sm text-muted-foreground mt-2 line-clamp-3">
                    {item.snippet}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    )
  }

  // Render agent execution results
  const renderAgentExecution = () => {
    const executions = result.agent_executions || [result]

    return (
      <div className="space-y-3">
        {executions.map((execution: any, idx: number) => {
          const execId = execution.task_id || `exec-${idx}`
          const isExpanded = expandedSections.has(execId)

          return (
            <Card key={idx} className="overflow-hidden">
              <button
                onClick={() => toggleSection(execId)}
                className="w-full text-left"
              >
                <CardHeader className="hover:bg-accent/50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <Bot className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-base flex items-center gap-2">
                          {execution.agent}
                          <Badge variant={execution.status === "completed" ? "default" : "secondary"}>
                            {execution.status}
                          </Badge>
                        </CardTitle>
                        <p className="text-sm text-muted-foreground mt-1">
                          {execution.action}
                        </p>
                      </div>
                    </div>
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 text-muted-foreground" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-muted-foreground" />
                    )}
                  </div>
                </CardHeader>
              </button>

              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <CardContent className="border-t pt-4 space-y-3">
                      {execution.started_at && (
                        <div className="text-sm text-muted-foreground">
                          <span className="font-medium">Started:</span>{" "}
                          {new Date(execution.started_at).toLocaleString()}
                        </div>
                      )}

                      {execution.completed_at && (
                        <div className="text-sm text-muted-foreground">
                          <span className="font-medium">Completed:</span>{" "}
                          {new Date(execution.completed_at).toLocaleString()}
                        </div>
                      )}

                      {execution.output && (
                        <div>
                          <div className="text-sm font-medium mb-2 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <FileText className="w-4 h-4" />
                              Output:
                            </div>
                            {/* Add download button for code output */}
                            {(execution.output.code || execution.output.content || (typeof execution.output === 'string' && execution.output.includes('def ') || execution.output.includes('function ') || execution.output.includes('class '))) && (
                              <div className="flex gap-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => downloadCode()}
                                >
                                  <Download className="h-4 w-4 mr-2" />
                                  Download
                                </Button>
                                {executionId && (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => downloadFromServer()}
                                  >
                                    <Download className="h-4 w-4 mr-2" />
                                    Server Download
                                  </Button>
                                )}
                              </div>
                            )}
                          </div>
                          <div className="bg-muted rounded-lg p-3 text-sm">
                            {typeof execution.output === "string" ? (
                              <pre className="whitespace-pre-wrap font-mono text-xs">
                                {execution.output}
                              </pre>
                            ) : (
                              <pre className="whitespace-pre-wrap font-mono text-xs">
                                {JSON.stringify(execution.output, null, 2)}
                              </pre>
                            )}
                          </div>
                        </div>
                      )}

                      {execution.error && (
                        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3">
                          <div className="text-sm font-medium text-destructive mb-1">Error:</div>
                          <p className="text-sm text-destructive/90">{execution.error}</p>
                        </div>
                      )}
                    </CardContent>
                  </motion.div>
                )}
              </AnimatePresence>
            </Card>
          )
        })}
      </div>
    )
  }

  // Render text result
  const renderTextResult = () => {
    const text = result.summary || result.final_answer || result.answer || result

    return (
      <div className="prose dark:prose-invert max-w-none">
        <p className="text-base leading-relaxed whitespace-pre-wrap">{text}</p>
      </div>
    )
  }

  // Render raw JSON
  const renderRawJson = () => {
    return (
      <div className="relative">
        <pre className="bg-muted rounded-lg p-4 text-sm overflow-x-auto">
          <code>{JSON.stringify(result, null, 2)}</code>
        </pre>
        <Button
          variant="outline"
          size="sm"
          className="absolute top-2 right-2"
          onClick={copyToClipboard}
        >
          {copied ? (
            <>
              <Check className="h-4 w-4 mr-2" />
              Copied!
            </>
          ) : (
            <>
              <Copy className="h-4 w-4 mr-2" />
              Copy
            </>
          )}
        </Button>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="border-green-500/20 bg-green-500/5">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-green-500">
              <CheckCircle2 className="w-6 h-6" />
              Execution Result
            </CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowRawJson(!showRawJson)}
              className="text-muted-foreground"
            >
              <Code2 className="w-4 h-4 mr-2" />
              {showRawJson ? "Hide" : "View"} JSON
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {showRawJson ? (
            renderRawJson()
          ) : (
            <div className="space-y-4">
              {resultType === "web_search" && renderWebSearchResults(result)}
              {resultType === "agent_execution" && renderAgentExecution()}
              {resultType === "text" && renderTextResult()}
              {resultType === "json" && renderRawJson()}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
