"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { motion } from "framer-motion"
import {
  Code2,
  FileText,
  FolderOpen,
  Rocket,
  Wand2,
  Bug,
  Plus,
  Loader2,
  Copy,
  Download,
  Check
} from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

type TaskType = "file" | "project" | "application" | "refactor" | "fix_bug" | "add_feature"
type Language = "python" | "typescript" | "javascript" | "java" | "go" | "rust" | "cpp"

const taskTypes = [
  { value: "file", label: "Write File", icon: FileText, description: "Generate a single code file" },
  { value: "project", label: "Write Project", icon: FolderOpen, description: "Create a multi-file project" },
  { value: "application", label: "Write Application", icon: Rocket, description: "Build a complete application" },
  { value: "refactor", label: "Refactor Code", icon: Wand2, description: "Improve existing code" },
  { value: "fix_bug", label: "Fix Bug", icon: Bug, description: "Fix bugs in your code" },
  { value: "add_feature", label: "Add Feature", icon: Plus, description: "Add new functionality" }
]

const languages: Language[] = ["python", "typescript", "javascript", "java", "go", "rust", "cpp"]

const frameworks: Record<Language, string[]> = {
  python: ["flask", "fastapi", "django", "none"],
  typescript: ["nextjs", "react", "express", "nest", "none"],
  javascript: ["react", "express", "vue", "none"],
  java: ["spring", "none"],
  go: ["gin", "echo", "none"],
  rust: ["actix", "rocket", "none"],
  cpp: ["none"]
}

const projectTypes = ["api", "webapp", "cli", "library"]

export default function CodeWriter() {
  const [taskType, setTaskType] = useState<TaskType>("file")
  const [language, setLanguage] = useState<Language>("python")
  const [framework, setFramework] = useState("none")
  const [description, setDescription] = useState("")
  const [projectName, setProjectName] = useState("")
  const [projectType, setProjectType] = useState("api")
  const [existingCode, setExistingCode] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [copied, setCopied] = useState(false)

  const handleGenerate = async () => {
    setLoading(true)
    setResult(null)

    try {
      let endpoint = ""
      let payload: any = {}

      switch (taskType) {
        case "file":
          endpoint = "/api/v1/code/write-file"
          payload = {
            description,
            language,
            framework: framework === "none" ? null : framework,
            filename: `main.${getFileExtension(language)}`
          }
          break

        case "project":
          endpoint = "/api/v1/code/write-project"
          payload = {
            description,
            language,
            project_type: projectType,
            framework: framework === "none" ? null : framework,
            project_name: projectName || "my_project"
          }
          break

        case "application":
          endpoint = "/api/v1/code/write-application"
          payload = {
            description,
            app_type: "web",
            language,
            framework: framework === "none" ? null : framework
          }
          break

        case "refactor":
          endpoint = "/api/v1/code/refactor"
          payload = {
            code: existingCode,
            refactor_type: "improve"
          }
          break

        case "fix_bug":
          endpoint = "/api/v1/code/fix-bug"
          payload = {
            code: existingCode,
            bug_description: description
          }
          break

        case "add_feature":
          endpoint = "/api/v1/code/add-feature"
          payload = {
            code: existingCode,
            feature_description: description
          }
          break
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${endpoint}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        }
      )

      const data = await response.json()
      setResult(data)
    } catch (error: any) {
      console.error("Code generation failed:", error)
      setResult({ error: error.message })
    } finally {
      setLoading(false)
    }
  }

  const copyCode = (code: string) => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const downloadCode = (code: string, filename: string) => {
    const blob = new Blob([code], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  const getFileExtension = (lang: Language) => {
    const extensions: Record<Language, string> = {
      python: "py",
      typescript: "ts",
      javascript: "js",
      java: "java",
      go: "go",
      rust: "rs",
      cpp: "cpp"
    }
    return extensions[lang]
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Code2 className="w-6 h-6 text-purple-500" />
          AI Code Writer
        </CardTitle>
        <CardDescription>
          Generate complete, production-ready code with AI
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Task Type Selection */}
        <div className="space-y-3">
          <label className="text-sm font-medium">What do you want to create?</label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {taskTypes.map((type) => {
              const Icon = type.icon
              return (
                <motion.button
                  key={type.value}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setTaskType(type.value as TaskType)}
                  className={`p-4 rounded-lg border-2 text-left transition-all ${
                    taskType === type.value
                      ? "border-purple-500 bg-purple-500/10"
                      : "border-border hover:border-purple-300"
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <Icon className="w-5 h-5 text-purple-500 flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm">{type.label}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {type.description}
                      </div>
                    </div>
                  </div>
                </motion.button>
              )
            })}
          </div>
        </div>

        {/* Language Selection */}
        <div className="space-y-3">
          <label className="text-sm font-medium">Programming Language</label>
          <Select value={language} onValueChange={(value) => setLanguage(value as Language)}>
            <SelectTrigger>
              <SelectValue placeholder="Select language" />
            </SelectTrigger>
            <SelectContent>
              {languages.map((lang) => (
                <SelectItem key={lang} value={lang}>
                  {lang.charAt(0).toUpperCase() + lang.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Framework Selection */}
        {frameworks[language] && frameworks[language].length > 1 && (
          <div className="space-y-3">
            <label className="text-sm font-medium">Framework (Optional)</label>
            <Select value={framework} onValueChange={setFramework}>
              <SelectTrigger>
                <SelectValue placeholder="Select framework" />
              </SelectTrigger>
              <SelectContent>
                {frameworks[language].map((fw) => (
                  <SelectItem key={fw} value={fw}>
                    {fw.charAt(0).toUpperCase() + fw.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Project Type (for project creation) */}
        {(taskType === "project" || taskType === "application") && (
          <div className="space-y-3">
            <label className="text-sm font-medium">Project Type</label>
            <Select value={projectType} onValueChange={setProjectType}>
              <SelectTrigger>
                <SelectValue placeholder="Select project type" />
              </SelectTrigger>
              <SelectContent>
                {projectTypes.map((type) => (
                  <SelectItem key={type} value={type}>
                    {type.charAt(0).toUpperCase() + type.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Project Name (for projects) */}
        {taskType === "project" && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Project Name</label>
            <Input
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              placeholder="my-awesome-project"
            />
          </div>
        )}

        {/* Description */}
        <div className="space-y-2">
          <label className="text-sm font-medium">
            {taskType === "refactor" ? "What to improve?" :
             taskType === "fix_bug" ? "Describe the bug" :
             taskType === "add_feature" ? "Feature to add" :
             "Describe what you want to create"}
          </label>
          <Textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={
              taskType === "file" ? "Describe the file functionality..." :
              taskType === "project" ? "Describe the project purpose and features..." :
              taskType === "application" ? "Describe the application..." :
              "Provide details..."
            }
            className="min-h-[100px]"
          />
        </div>

        {/* Existing Code (for refactor/fix/feature) */}
        {(taskType === "refactor" || taskType === "fix_bug" || taskType === "add_feature") && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Existing Code</label>
            <Textarea
              value={existingCode}
              onChange={(e) => setExistingCode(e.target.value)}
              placeholder="Paste your code here..."
              className="min-h-[150px] font-mono text-sm"
            />
          </div>
        )}

        {/* Generate Button */}
        <Button
          onClick={handleGenerate}
          disabled={loading || !description}
          className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
          size="lg"
        >
          {loading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Code2 className="mr-2 h-5 w-5" />
              Generate Code
            </>
          )}
        </Button>

        {/* Result Display */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            {result.error ? (
              <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
                <p className="text-sm text-destructive">{result.error}</p>
              </div>
            ) : (
              <>
                {/* Success Message */}
                <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                  <div className="flex items-center gap-2">
                    <Check className="w-5 h-5 text-green-500" />
                    <p className="text-sm font-medium">Code generated successfully!</p>
                  </div>
                </div>

                {/* Code Display */}
                {result.code && (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">Generated Code:</label>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyCode(result.code)}
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
                          onClick={() => downloadCode(result.code, `generated.${getFileExtension(language)}`)}
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </Button>
                      </div>
                    </div>
                    <pre className="bg-muted rounded-lg p-4 text-sm overflow-x-auto max-h-[500px] overflow-y-auto">
                      <code>{result.code}</code>
                    </pre>
                  </div>
                )}

                {/* Project Display */}
                {result.project && (
                  <div className="space-y-3">
                    <label className="text-sm font-medium">Project Structure:</label>
                    <div className="bg-muted rounded-lg p-4 max-h-[500px] overflow-y-auto">
                      <pre className="text-sm">
                        {JSON.stringify(result.project, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Application Display */}
                {result.application && (
                  <div className="space-y-3">
                    <label className="text-sm font-medium">Application:</label>
                    <div className="bg-muted rounded-lg p-4 max-h-[500px] overflow-y-auto">
                      <pre className="text-sm">
                        {JSON.stringify(result.application, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}

                {/* Refactored/Fixed Code */}
                {(result.refactored_code || result.fixed_code || result.updated_code) && (
                  <div className="space-y-3">
                    <label className="text-sm font-medium">Updated Code:</label>
                    <div className="bg-muted rounded-lg p-4 max-h-[500px] overflow-y-auto">
                      <pre className="text-sm">
                        {result.refactored_code || result.fixed_code || result.updated_code}
                      </pre>
                    </div>
                  </div>
                )}
              </>
            )}
          </motion.div>
        )}
      </CardContent>
    </Card>
  )
}
