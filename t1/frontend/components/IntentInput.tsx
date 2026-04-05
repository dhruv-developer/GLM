"use client"

import { useState } from "react"
import { Send, Loader2, Sparkles } from "lucide-react"
import { createTask } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { motion } from "framer-motion"

interface IntentInputProps {
  onTaskCreated: (data: any) => void
}

const exampleIntents = [
  "Search for the latest AI trends in 2024 and create a summary",
  "Find top 10 Python async best practices and compare them",
  "Research Docker containerization and create a guide",
  "Search for recent cybersecurity news and identify threats",
  "Find technical documentation for FastAPI and summarize",
  "Search for machine learning frameworks and compare features"
]

export default function IntentInput({ onTaskCreated }: IntentInputProps) {
  const [intent, setIntent] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    if (!intent.trim()) {
      setError("Please enter a task description")
      return
    }

    setIsSubmitting(true)

    try {
      const response = await createTask({
        intent: intent.trim(),
        priority: "medium",
      })

      onTaskCreated({
        executionId: response.execution_id,
        executionLink: response.execution_link,
        intent: intent.trim(),
      })

      setIntent("")
    } catch (err: any) {
      setError(err.message || "Failed to create task. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="border-2 border-primary/20 shadow-xl">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            Create New Task
          </CardTitle>
          <CardDescription>
            Describe what you need to accomplish in plain English. Our AI-powered multi-agent system with web search capabilities will handle the rest.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Textarea
                value={intent}
                onChange={(e) => setIntent(e.target.value)}
                placeholder="e.g., Search for the latest AI trends and create a summary, Find top 10 Python tutorials and compare them, Research Docker best practices..."
                className="min-h-[150px] resize-none border-2 focus:border-primary"
                disabled={isSubmitting}
              />
            </div>

            {/* Example Intents */}
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Try these examples:</p>
              <div className="flex flex-wrap gap-2">
                {exampleIntents.map((example) => (
                  <Badge
                    key={example}
                    variant="outline"
                    className="cursor-pointer hover:bg-primary hover:text-primary-foreground transition-all"
                    onClick={() => setIntent(example)}
                  >
                    {example}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Press Enter to submit
              </div>
              <Button
                type="submit"
                disabled={isSubmitting || !intent.trim()}
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 px-8"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Create Task
                  </>
                )}
              </Button>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm"
              >
                {error}
              </motion.div>
            )}
          </form>
        </CardContent>
      </Card>
    </motion.div>
  )
}
