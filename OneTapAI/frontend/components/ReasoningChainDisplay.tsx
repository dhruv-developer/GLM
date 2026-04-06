"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { motion, AnimatePresence } from "framer-motion"
import {
  Brain,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
  Lightbulb,
  GitBranch,
  Shield,
  Wand2,
  Clock
} from "lucide-react"
import { useState } from "react"

interface ReasoningStep {
  step_number: number
  step_type: string
  thought: string
  reasoning: string
  alternatives: string[]
  decision: string
  confidence: number
  timestamp: string
}

interface ReasoningChain {
  task_id: string
  intent: string
  steps: ReasoningStep[]
  final_plan: any
  confidence_score: number
  estimated_duration: number
  created_at: string
}

interface ReasoningChainDisplayProps {
  chain: ReasoningChain
}

const stepConfig: Record<string, { icon: any; color: string; label: string }> = {
  analysis: {
    icon: Brain,
    color: "text-blue-500",
    label: "Analysis"
  },
  planning: {
    icon: Lightbulb,
    color: "text-purple-500",
    label: "Planning"
  },
  alternatives: {
    icon: GitBranch,
    color: "text-green-500",
    label: "Alternatives"
  },
  validation: {
    icon: Shield,
    color: "text-orange-500",
    label: "Validation"
  },
  refinement: {
    icon: Wand2,
    color: "text-pink-500",
    label: "Refinement"
  },
  fallback: {
    icon: AlertCircle,
    color: "text-gray-500",
    label: "Fallback"
  }
}

export default function ReasoningChainDisplay({ chain }: ReasoningChainDisplayProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set([0]))

  const toggleStep = (stepNumber: number) => {
    setExpandedSteps(prev => {
      const newSet = new Set(prev)
      if (newSet.has(stepNumber)) {
        newSet.delete(stepNumber)
      } else {
        newSet.add(stepNumber)
      }
      return newSet
    })
  }

  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return "text-green-500"
    if (confidence >= 0.6) return "text-yellow-500"
    return "text-red-500"
  }

  return (
    <Card className="border-2 border-primary/20">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2 mb-2">
              <Brain className="w-6 h-6 text-primary" />
              AI Reasoning Process
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Step-by-step reasoning before execution
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Badge variant="secondary" className="text-lg px-4 py-2">
              Confidence: {chain.confidence_score.toFixed(2)}
            </Badge>
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <Clock className="w-4 h-4" />
              ~{chain.estimated_duration}s estimated
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Original Intent */}
        <div className="bg-muted/50 rounded-lg p-4">
          <div className="text-sm font-medium mb-1">Original Intent:</div>
          <p className="text-sm">{chain.intent}</p>
        </div>

        {/* Reasoning Steps */}
        <div className="space-y-2">
          <div className="text-sm font-medium flex items-center gap-2">
            <Brain className="w-4 h-4" />
            Reasoning Steps ({chain.steps.length})
          </div>

          {chain.steps.map((step, index) => {
            const config = stepConfig[step.step_type] || stepConfig.fallback
            const StepIcon = config.icon
            const isExpanded = expandedSteps.has(step.step_number)

            return (
              <motion.div
                key={step.step_number}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border rounded-lg overflow-hidden"
              >
                <button
                  onClick={() => toggleStep(step.step_number)}
                  className="w-full text-left"
                >
                  <div className="flex items-start gap-3 p-4 hover:bg-accent/50 transition-colors">
                    <div className={`p-2 rounded-lg ${config.color}/10`}>
                      <StepIcon className={`w-5 h-5 ${config.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className={`${config.color}/10 ${config.color} border-0`}>
                          Step {step.step_number}
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          {config.label}
                        </Badge>
                        <Badge
                          variant="outline"
                          className={`text-xs ${getConfidenceColor(step.confidence)}`}
                        >
                          {(step.confidence * 100).toFixed(0)}% confident
                        </Badge>
                      </div>
                      <p className="text-sm font-medium truncate">{step.thought}</p>
                    </div>
                    {isExpanded ? (
                      <ChevronDown className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                    )}
                  </div>
                </button>

                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                      className="border-t bg-muted/30"
                    >
                      <div className="p-4 space-y-3">
                        {/* Reasoning */}
                        <div>
                          <div className="text-sm font-medium mb-1">Reasoning:</div>
                          <p className="text-sm text-muted-foreground">{step.reasoning}</p>
                        </div>

                        {/* Alternatives */}
                        {step.alternatives && step.alternatives.length > 0 && (
                          <div>
                            <div className="text-sm font-medium mb-2">Alternatives Considered:</div>
                            <div className="flex flex-wrap gap-2">
                              {step.alternatives.map((alt, idx) => (
                                <Badge key={idx} variant="secondary" className="text-xs">
                                  {alt}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Decision */}
                        <div>
                          <div className="text-sm font-medium mb-1">Decision:</div>
                          <div className="bg-background rounded p-3 text-sm font-mono">
                            {typeof step.decision === 'string'
                              ? step.decision.length > 200
                                ? step.decision.substring(0, 200) + '...'
                                : step.decision
                              : JSON.stringify(step.decision, null, 2).substring(0, 200) + '...'
                            }
                          </div>
                        </div>

                        {/* Timestamp */}
                        <div className="text-xs text-muted-foreground">
                          {new Date(step.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </div>

        {/* Final Plan Summary */}
        {chain.final_plan && Object.keys(chain.final_plan).length > 0 && (
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <CheckCircle2 className="w-5 h-5 text-green-500" />
              <div className="font-medium">Final Plan:</div>
            </div>
            <pre className="text-sm overflow-x-auto">
              {JSON.stringify(chain.final_plan, null, 2).substring(0, 500)}
              {JSON.stringify(chain.final_plan, null, 2).length > 500 && '...'}
            </pre>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
