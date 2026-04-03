"use client";

import { useState } from "react";
import { Sparkles, Zap, Shield, Code, Clock, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import IntentInput from "@/components/IntentInput";
import TaskDisplay from "@/components/TaskDisplay";
import ExecutionMonitor from "@/components/ExecutionMonitor";
import { TaskStatus } from "@/types";

export default function Home() {
  const [currentView, setCurrentView] = useState<"home" | "monitoring">("home");
  const [taskData, setTaskData] = useState<{
    executionId: string;
    executionLink: string;
    intent: string;
  } | null>(null);

  const handleTaskCreated = (data: any) => {
    setTaskData(data);
    setCurrentView("monitoring");
  };

  const handleBack = () => {
    setCurrentView("home");
    setTaskData(null);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-black/20">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">ZIEL-MAS</h1>
              <p className="text-xs text-gray-400">Zero-Interaction Execution Links</p>
            </div>
          </div>
          {currentView === "monitoring" && (
            <button
              onClick={handleBack}
              className="px-4 py-2 text-sm bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
            >
              ← Back to Home
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-12">
        {currentView === "home" ? (
          <>
            {/* Hero Section */}
            <div className="text-center mb-16 animate-fade-in">
              <div className="inline-flex items-center space-x-2 bg-purple-500/20 border border-purple-500/30 rounded-full px-4 py-2 mb-6">
                <Sparkles className="w-4 h-4 text-purple-400" />
                <span className="text-sm text-purple-300">Powered by Multi-Agent Architecture</span>
              </div>

              <h2 className="text-5xl md:text-7xl font-bold mb-6">
                <span className="gradient-text">Transform Intent</span>
                <br />
                <span className="text-white">Into Action</span>
              </h2>

              <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
                Describe what you need in plain English. ZIEL-MAS converts your intent into
                autonomous, executable workflows with zero interaction required.
              </p>

              {/* Feature Cards */}
              <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mt-12">
                <div className="glass rounded-xl p-6 hover:bg-white/10 transition-all">
                  <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4 mx-auto">
                    <Sparkles className="w-6 h-6 text-blue-400" />
                  </div>
                  <h3 className="text-white font-semibold mb-2">Natural Language</h3>
                  <p className="text-gray-400 text-sm">Just describe what you need. No coding required.</p>
                </div>

                <div className="glass rounded-xl p-6 hover:bg-white/10 transition-all">
                  <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4 mx-auto">
                    <Shield className="w-6 h-6 text-purple-400" />
                  </div>
                  <h3 className="text-white font-semibold mb-2">Secure Links</h3>
                  <p className="text-gray-400 text-sm">Each task gets a secure, executable link.</p>
                </div>

                <div className="glass rounded-xl p-6 hover:bg-white/10 transition-all">
                  <div className="w-12 h-12 bg-pink-500/20 rounded-lg flex items-center justify-center mb-4 mx-auto">
                    <Zap className="w-6 h-6 text-pink-400" />
                  </div>
                  <h3 className="text-white font-semibold mb-2">Zero Interaction</h3>
                  <p className="text-gray-400 text-sm">Execute complex tasks autonomously.</p>
                </div>
              </div>
            </div>

            {/* Intent Input */}
            <div className="max-w-3xl mx-auto animate-slide-up">
              <IntentInput onTaskCreated={handleTaskCreated} />
            </div>

            {/* Example Intents */}
            <div className="max-w-3xl mx-auto mt-8">
              <p className="text-sm text-gray-500 mb-3 text-center">Try these examples:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {[
                  "Send birthday message to mom at 12 AM",
                  "Book an Uber to the airport at 3 PM",
                  "Find top 5 Italian restaurants nearby",
                  "Apply to Software Engineer position at Google"
                ].map((example) => (
                  <button
                    key={example}
                    onClick={() => {
                      const input = document.querySelector("textarea") as HTMLTextAreaElement;
                      if (input) input.value = example;
                    }}
                    className="px-3 py-1.5 text-xs bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-gray-400 hover:text-white transition-all"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Monitoring View */}
            {taskData && (
              <ExecutionMonitor
                executionId={taskData.executionId}
                executionLink={taskData.executionLink}
                intent={taskData.intent}
              />
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-20">
        <div className="container mx-auto px-4 py-8 text-center text-gray-500 text-sm">
          <p>ZIEL-MAS - Distributed Multi-Agent Execution System</p>
          <p className="mt-1">Powered by GLM 5.1 | Zero-Interaction Computing</p>
        </div>
      </footer>
    </main>
  );
}
