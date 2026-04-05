"use client"

import { useState, useCallback } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { motion } from "framer-motion"
import {
  Upload,
  Image as ImageIcon,
  X,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Eye,
  Trash2
} from "lucide-react"
import { analyzeImage } from "@/lib/api"

interface VisionImageUploadProps {
  onAnalysisComplete: (result: any) => void
  onError?: (error: string) => void
}

type AnalysisType =
  | "general"
  | "extract_text"
  | "diagnose_error"
  | "ui_to_code"
  | "understand_diagram"
  | "analyze_chart"

const analysisTypes: { value: AnalysisType; label: string; description: string; icon: string }[] = [
  {
    value: "general",
    label: "General Analysis",
    description: "Describe and understand the image content",
    icon: "🔍"
  },
  {
    value: "extract_text",
    label: "Extract Text (OCR)",
    description: "Extract all text from the image",
    icon: "📝"
  },
  {
    value: "diagnose_error",
    label: "Diagnose Error",
    description: "Analyze error screenshots and suggest fixes",
    icon: "🔧"
  },
  {
    value: "ui_to_code",
    label: "UI to Code",
    description: "Convert UI design to code",
    icon: "💻"
  },
  {
    value: "understand_diagram",
    label: "Understand Diagram",
    description: "Interpret technical diagrams",
    icon: "📊"
  },
  {
    value: "analyze_chart",
    label: "Analyze Chart",
    description: "Read and analyze data visualizations",
    icon: "📈"
  }
]

export default function VisionImageUpload({ onAnalysisComplete, onError }: VisionImageUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [selectedType, setSelectedType] = useState<AnalysisType>("general")
  const [customPrompt, setCustomPrompt] = useState("")
  const [context, setContext] = useState("")
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }, [])

  const handleFile = (file: File) => {
    if (!file.type.startsWith("image/")) {
      onError?.("Please upload an image file")
      return
    }

    setSelectedFile(file)

    // Create preview
    const reader = new FileReader()
    reader.onloadend = () => {
      setPreview(reader.result as string)
    }
    reader.readAsDataURL(file)
  }

  const handleRemove = () => {
    setSelectedFile(null)
    setPreview(null)
    setCustomPrompt("")
    setContext("")
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setAnalyzing(true)

    try {
      const prompt = customPrompt || getDefaultPrompt(selectedType)

      const result = await analyzeImage(
        selectedFile,
        prompt,
        selectedType,
        context
      )

      if (result.success) {
        onAnalysisComplete(result.result)
      } else {
        onError?.(result.result?.error || "Analysis failed")
      }
    } catch (error: any) {
      onError?.(error.message || "Failed to analyze image")
    } finally {
      setAnalyzing(false)
    }
  }

  const getDefaultPrompt = (type: AnalysisType): string => {
    switch (type) {
      case "general":
        return "Describe this image in detail"
      case "extract_text":
        return "Extract all text from this image accurately"
      case "diagnose_error":
        return "Analyze this error screenshot and provide specific fix steps"
      case "ui_to_code":
        return "Convert this UI design into production-ready React code"
      case "understand_diagram":
        return "Analyze this technical diagram and explain its components and flow"
      case "analyze_chart":
        return "Analyze this data visualization and extract key insights"
      default:
        return "Describe this image in detail"
    }
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ImageIcon className="w-6 h-6 text-purple-500" />
          Image Analysis
        </CardTitle>
        <CardDescription>
          Upload an image for AI-powered analysis using GLM Vision
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Analysis Type Selection */}
        <div className="space-y-3">
          <label className="text-sm font-medium">Analysis Type</label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {analysisTypes.map((type) => (
              <motion.button
                key={type.value}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedType(type.value)}
                className={`p-4 rounded-lg border-2 text-left transition-all ${
                  selectedType === type.value
                    ? "border-purple-500 bg-purple-500/10"
                    : "border-border hover:border-purple-300"
                }`}
              >
                <div className="flex items-start gap-2">
                  <span className="text-2xl">{type.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm">{type.label}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {type.description}
                    </div>
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Upload Area */}
        {!selectedFile ? (
          <motion.div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive
                ? "border-purple-500 bg-purple-500/5"
                : "border-border hover:border-purple-300"
            }`}
          >
            <input
              type="file"
              accept="image/*"
              onChange={(e) => e.target.files && handleFile(e.target.files[0])}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <p className="text-sm font-medium mb-2">
              Drop an image here or click to upload
            </p>
            <p className="text-xs text-muted-foreground">
              Supports PNG, JPG, GIF, WebP
            </p>
          </motion.div>
        ) : (
          <div className="space-y-4">
            {/* Preview */}
            <div className="relative rounded-lg overflow-hidden border">
              {preview && (
                <img
                  src={preview}
                  alt="Preview"
                  className="w-full max-h-96 object-contain bg-muted"
                />
              )}
              <Button
                variant="destructive"
                size="icon"
                onClick={handleRemove}
                className="absolute top-2 right-2"
              >
                <X className="w-4 h-4" />
              </Button>
              <Badge className="absolute top-2 left-2">
                {selectedFile.name}
              </Badge>
            </div>

            {/* Custom Prompt */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Custom Prompt (Optional)</label>
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder={getDefaultPrompt(selectedType)}
                className="w-full min-h-[80px] p-3 rounded-lg border resize-none focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>

            {/* Context (for error diagnosis) */}
            {selectedType === "diagnose_error" && (
              <div className="space-y-2">
                <label className="text-sm font-medium">Context (Optional)</label>
                <input
                  type="text"
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  placeholder="What were you trying to do when this error occurred?"
                  className="w-full p-3 rounded-lg border focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>
            )}

            {/* Analyze Button */}
            <Button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
              size="lg"
            >
              {analyzing ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Eye className="mr-2 h-5 w-5" />
                  Analyze Image
                </>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
