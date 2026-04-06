"use client"

import { useState } from "react"
import { MainLayout } from "@/components/main-layout"
import VisionImageUpload from "@/components/VisionImageUpload"
import VisionResultDisplay from "@/components/VisionResultDisplay"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import {
  Eye,
  Sparkles,
  ArrowLeft,
  Image as ImageIcon,
  FileText,
  Wrench,
  Code2,
  TrendingUp,
  Zap,
  Shield,
  Clock
} from "lucide-react"
import Link from "next/link"
import { VisionAnalysisResult } from "@/types"

const features = [
  {
    icon: Eye,
    title: "General Image Analysis",
    description: "Understand and describe any image with detailed AI analysis"
  },
  {
    icon: FileText,
    title: "Text Extraction (OCR)",
    description: "Extract text from screenshots, documents, and images"
  },
  {
    icon: Wrench,
    title: "Error Diagnosis",
    description: "Analyze error screenshots and get actionable fix recommendations"
  },
  {
    icon: Code2,
    title: "UI to Code",
    description: "Convert UI designs directly into production-ready code"
  },
  {
    icon: TrendingUp,
    title: "Diagram Understanding",
    description: "Interpret technical diagrams, flowcharts, and architecture"
  },
  {
    icon: ImageIcon,
    title: "Chart Analysis",
    description: "Extract insights from data visualizations and charts"
  }
]

export default function VisionDemoPage() {
  const [analysisResult, setAnalysisResult] = useState<VisionAnalysisResult | null>(null)
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnalysisComplete = (result: VisionAnalysisResult) => {
    setAnalysisResult(result)
    setError(null)
  }

  const handleError = (errorMessage: string) => {
    setError(errorMessage)
    setAnalysisResult(null)
  }

  const handleReset = () => {
    setAnalysisResult(null)
    setPreviewImage(null)
    setError(null)
  }

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
              <Eye className="w-8 h-8 text-purple-500" />
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                GLM Vision AI
              </h1>
            </div>
            <p className="text-muted-foreground text-lg">
              Powerful image and video analysis using GLM-4.6V Vision API
            </p>
          </div>
          <Link href="/">
            <Button variant="outline" className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </Button>
          </Link>
        </div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-destructive/10 border border-destructive/20 rounded-lg p-4"
          >
            <div className="flex items-start gap-3">
              <Wrench className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-medium text-destructive mb-1">Analysis Failed</h4>
                <p className="text-sm text-destructive/90">{error}</p>
              </div>
              <Button variant="outline" size="sm" onClick={() => setError(null)}>
                Dismiss
              </Button>
            </div>
          </motion.div>
        )}

        {!analysisResult ? (
          <>
            {/* Features Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {features.map((feature, index) => {
                const Icon = feature.icon
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <Card className="h-full hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <div className="flex items-center gap-3 mb-2">
                          <div className="p-2 rounded-lg bg-purple-500/10">
                            <Icon className="w-5 h-5 text-purple-500" />
                          </div>
                          <CardTitle className="text-lg">{feature.title}</CardTitle>
                        </div>
                        <CardDescription>{feature.description}</CardDescription>
                      </CardHeader>
                    </Card>
                  </motion.div>
                )
              })}
            </div>

            {/* Upload Section */}
            <VisionImageUpload
              onAnalysisComplete={handleAnalysisComplete}
              onError={handleError}
            />

            {/* Info Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Zap className="w-5 h-5 text-blue-500" />
                    <CardTitle className="text-base">Fast Analysis</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Get detailed image analysis in seconds with GLM-4.6V's advanced vision capabilities
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Shield className="w-5 h-5 text-purple-500" />
                    <CardTitle className="text-base">Secure & Private</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Images are processed securely and not stored. Your privacy is our priority.
                  </p>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2 mb-1">
                    <Clock className="w-5 h-5 text-green-500" />
                    <CardTitle className="text-base">Always Available</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    24/7 availability with scalable infrastructure for all your vision needs.
                  </p>
                </CardContent>
              </Card>
            </div>
          </>
        ) : (
          <>
            {/* Results Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold flex items-center gap-2">
                    <Sparkles className="w-6 h-6 text-purple-500" />
                    Analysis Complete
                  </h2>
                  <p className="text-muted-foreground mt-1">
                    Your image has been analyzed successfully
                  </p>
                </div>
                <Button onClick={handleReset} variant="outline">
                  Analyze Another Image
                </Button>
              </div>

              <VisionResultDisplay result={analysisResult} image={previewImage} />
            </div>
          </>
        )}
      </motion.div>
    </MainLayout>
  )
}
