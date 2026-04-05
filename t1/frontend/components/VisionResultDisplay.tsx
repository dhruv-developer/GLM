"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { motion } from "framer-motion"
import {
  Eye,
  Code2,
  FileText,
  Wrench,
  TrendingUp,
  AlertTriangle,
  Copy,
  Check,
  Download,
  ExternalLink
} from "lucide-react"
import { useState } from "react"
import { VisionAnalysisResult } from "@/types"

interface VisionResultDisplayProps {
  result: VisionAnalysisResult
  image?: string
}

const analysisTypeIcons: Record<string, any> = {
  general: Eye,
  extract_text: FileText,
  diagnose_error: Wrench,
  ui_to_code: Code2,
  understand_diagram: TrendingUp,
  analyze_chart: TrendingUp,
  video: Eye
}

const analysisTypeLabels: Record<string, string> = {
  general: "General Analysis",
  extract_text: "Text Extraction (OCR)",
  diagnose_error: "Error Diagnosis",
  ui_to_code: "UI to Code",
  understand_diagram: "Diagram Understanding",
  analyze_chart: "Chart Analysis",
  video: "Video Analysis"
}

export default function VisionResultDisplay({ result, image }: VisionResultDisplayProps) {
  const [copied, setCopied] = useState(false)

  const copyResult = () => {
    const text = result.result?.analysis || ""
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadResult = () => {
    const text = result.result?.analysis || ""
    const blob = new Blob([text], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `vision-analysis-${result.analysis_type}-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  const Icon = analysisTypeIcons[result.analysis_type] || Eye

  const isError = !result.result?.success || result.result?.error
  const isMock = result.result?.mock

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Result Header */}
      <Card className={isError ? "border-destructive/20" : "border-green-500/20"}>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-lg ${isError ? "bg-destructive/10" : "bg-green-500/10"}`}>
                <Icon className={`w-6 h-6 ${isError ? "text-destructive" : "text-green-500"}`} />
              </div>
              <div>
                <CardTitle className={`flex items-center gap-2 ${isError ? "text-destructive" : "text-green-500"}`}>
                  {analysisTypeLabels[result.analysis_type] || "Vision Analysis"}
                  {isMock && (
                    <Badge variant="secondary" className="text-xs">
                      Mock Result
                    </Badge>
                  )}
                </CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  {isError ? "Analysis failed" : "Analysis completed successfully"}
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={copyResult}
                disabled={!result.result?.analysis}
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
              <Button
                variant="outline"
                size="sm"
                onClick={downloadResult}
                disabled={!result.result?.analysis}
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Metadata */}
          <div className="flex flex-wrap gap-4 text-sm">
            <div>
              <span className="font-medium">Type:</span>{" "}
              <Badge variant="secondary">{analysisTypeLabels[result.analysis_type]}</Badge>
            </div>
            {result.execution_time && (
              <div>
                <span className="font-medium">Duration:</span>{" "}
                <span className="text-muted-foreground">{result.execution_time.toFixed(2)}s</span>
              </div>
            )}
            <div>
              <span className="font-medium">Timestamp:</span>{" "}
              <span className="text-muted-foreground">
                {new Date(result.timestamp).toLocaleString()}
              </span>
            </div>
          </div>

          {/* Error Display */}
          {isError && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-medium text-destructive mb-1">Analysis Error</h4>
                  <p className="text-sm text-destructive/90">
                    {result.result?.error || result.result?.details || "Unknown error occurred"}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Analysis Result */}
          {result.result?.analysis && (
            <div className="space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Analysis Result
              </h4>
              <div className="bg-muted rounded-lg p-4">
                <div className="prose dark:prose-invert max-w-none whitespace-pre-wrap text-sm">
                  {result.result.analysis}
                </div>
              </div>
            </div>
          )}

          {/* Mock Result Notice */}
          {isMock && (
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h4 className="font-medium text-yellow-500 mb-1">Mock Result</h4>
                  <p className="text-sm text-yellow-500/90">
                    This is a mock result. To use real GLM Vision API, configure the{" "}
                    <code className="px-1 py-0.5 rounded bg-yellow-500/20">ZAI_API_KEY</code>{" "}
                    environment variable in your backend.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Model Info */}
          {result.result?.model && (
            <div className="text-sm text-muted-foreground">
              <span className="font-medium">Model:</span> {result.result.model}
            </div>
          )}

          {/* Original Image */}
          {image && (
            <div className="space-y-3">
              <h4 className="font-medium flex items-center gap-2">
                <Eye className="w-4 h-4" />
                Original Image
              </h4>
              <div className="rounded-lg overflow-hidden border">
                <img
                  src={image}
                  alt="Analyzed image"
                  className="w-full max-h-96 object-contain bg-muted"
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
