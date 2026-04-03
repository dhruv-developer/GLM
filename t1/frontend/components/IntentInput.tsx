"use client";

import { useState } from "react";
import { Send, Loader2 } from "lucide-react";
import { createTask } from "@/lib/api";

interface IntentInputProps {
  onTaskCreated: (data: any) => void;
}

export default function IntentInput({ onTaskCreated }: IntentInputProps) {
  const [intent, setIntent] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!intent.trim()) {
      setError("Please enter a task description");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await createTask({
        intent: intent.trim(),
        priority: "medium",
      });

      onTaskCreated({
        executionId: response.execution_id,
        executionLink: response.execution_link,
        intent: intent.trim(),
      });

      setIntent("");
    } catch (err: any) {
      setError(err.message || "Failed to create task. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="glass rounded-2xl p-1">
        <div className="bg-black/30 rounded-xl overflow-hidden">
          <textarea
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
            placeholder="Describe what you need to do..."
            className="w-full bg-transparent text-white placeholder-gray-500 p-6 resize-none focus:outline-none min-h-[150px]"
            disabled={isSubmitting}
          />
          <div className="border-t border-white/10 px-6 py-4 flex items-center justify-between">
            <div className="text-sm text-gray-500">
              Press Enter to submit
            </div>
            <button
              type="submit"
              disabled={isSubmitting || !intent.trim()}
              className="flex items-center space-x-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg font-medium transition-all"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Creating...</span>
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Create Task</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-4 text-red-300">
          {error}
        </div>
      )}
    </form>
  );
}
