"use client"

import { MainLayout } from "@/components/main-layout"
import CodeWriter from "@/components/CodeWriter"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import {
  Code2,
  Sparkles,
  ArrowLeft,
  Rocket,
  FileText,
  FolderOpen,
  Wand2,
  Bug,
  Plus,
  Zap,
  Shield,
  Clock
} from "lucide-react"
import Link from "next/link"

const features = [
  {
    icon: FileText,
    title: "Single File Generation",
    description: "Generate individual code files with complete functionality"
  },
  {
    icon: FolderOpen,
    title: "Multi-File Projects",
    description: "Create complete projects with proper structure and organization"
  },
  {
    icon: Rocket,
    title: "Full Applications",
    description: "Build complete applications with all components and features"
  },
  {
    icon: Wand2,
    title: "Code Refactoring",
    description: "Improve and optimize existing code automatically"
  },
  {
    icon: Bug,
    title: "Bug Fixing",
    description: "Identify and fix bugs in your code with AI assistance"
  },
  {
    icon: Plus,
    title: "Feature Addition",
    description: "Add new features to existing codebases effortlessly"
  }
]

const languages = [
  { name: "Python", icon: "🐍", frameworks: ["Flask", "FastAPI", "Django"] },
  { name: "TypeScript", icon: "📘", frameworks: ["Next.js", "React", "NestJS"] },
  { name: "JavaScript", icon: "📙", frameworks: ["React", "Express", "Vue"] },
  { name: "Go", icon: "🐹", frameworks: ["Gin", "Echo"] },
  { name: "Rust", icon: "🦀", frameworks: ["Actix", "Rocket"] },
  { name: "Java", icon: "☕", frameworks: ["Spring Boot"] },
  { name: "C++", icon: "⚡", frameworks: ["STL"] }
]

export default function CodeWriterPage() {
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
              <Code2 className="w-8 h-8 text-purple-500" />
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                AI Code Writer
              </h1>
            </div>
            <p className="text-muted-foreground text-lg">
              Generate complete, production-ready code with AI assistance
            </p>
          </div>
          <Link href="/">
            <Button variant="outline" className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Dashboard
            </Button>
          </Link>
        </div>

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

        {/* Main Code Writer */}
        <CodeWriter />

        {/* Supported Languages */}
        <Card>
          <CardHeader>
            <CardTitle>Supported Languages & Frameworks</CardTitle>
            <CardDescription>
              Generate code in 7+ programming languages with popular frameworks
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {languages.map((lang, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 p-4 rounded-lg border hover:border-purple-300 transition-colors"
                >
                  <div className="text-3xl">{lang.icon}</div>
                  <div className="flex-1">
                    <div className="font-medium">{lang.name}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {lang.frameworks.join(", ")}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2 mb-1">
                <Zap className="w-5 h-5 text-blue-500" />
                <CardTitle className="text-base">Instant Generation</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Get production-ready code in seconds with AI-powered generation
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-500/10 to-pink-500/10">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2 mb-1">
                <Shield className="w-5 h-5 text-purple-500" />
                <CardTitle className="text-base">Best Practices</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Code follows industry best practices with proper error handling
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2 mb-1">
                <Clock className="w-5 h-5 text-green-500" />
                <CardTitle className="text-base">Full Documentation</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Includes comments and usage examples for easy understanding
              </p>
            </CardContent>
          </Card>
        </div>

        {/* How It Works */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-purple-500" />
              How It Works
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl font-bold text-purple-500">1</span>
                </div>
                <h4 className="font-medium mb-2">Describe</h4>
                <p className="text-sm text-muted-foreground">
                  Tell us what you want to create in plain English
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl font-bold text-purple-500">2</span>
                </div>
                <h4 className="font-medium mb-2">Configure</h4>
                <p className="text-sm text-muted-foreground">
                  Choose language, framework, and other options
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl font-bold text-purple-500">3</span>
                </div>
                <h4 className="font-medium mb-2">Generate</h4>
                <p className="text-sm text-muted-foreground">
                  AI generates complete, production-ready code
                </p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 rounded-full bg-purple-500/10 flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl font-bold text-purple-500">4</span>
                </div>
                <h4 className="font-medium mb-2">Use</h4>
                <p className="text-sm text-muted-foreground">
                  Copy or download the code for your projects
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </MainLayout>
  )
}
