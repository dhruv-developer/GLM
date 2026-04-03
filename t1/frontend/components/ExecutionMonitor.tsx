"use client";

import { useState, useEffect } from "react";
import { CheckCircle2, XCircle, Clock, Loader2, Copy, ExternalLink, RefreshCw } from "lucide-react";
import { getTaskStatus, executeTask } from "@/lib/api";
import { TaskStatus as TaskStatusType } from "@/types";

interface ExecutionMonitorProps {
  executionId: string;
  executionLink: string;
  intent: string;
}

export default function ExecutionMonitor({
  executionId,
  executionLink,
  intent,
}: ExecutionMonitorProps) {
  const [status, setStatus] = useState<TaskStatusType | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [copied, setCopied] = useState(false);

  const fetchStatus = async () => {
    try {
      const data = await getTaskStatus(executionId);
      setStatus(data);
    } catch (error) {
      console.error("Failed to fetch status:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    setExecuting(true);
    try {
      const token = executionLink.split("/").pop();
      await executeTask(token || "");
      await fetchStatus();
    } catch (error: any) {
      console.error("Execution failed:", error);
      alert(error.message || "Failed to execute task");
    } finally {
      setExecuting(false);
    }
  };

  const copyLink = () => {
    const fullLink = `${window.location.origin}${executionLink}`;
    navigator.clipboard.writeText(fullLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [executionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
      </div>
    );
  }

  const statusConfig = {
    pending: { color: "yellow", icon: Clock, label: "Pending" },
    planning: { color: "blue", icon: Loader2, label: "Planning" },
    ready: { color: "purple", icon: Clock, label: "Ready" },
    running: { color: "purple", icon: Loader2, label: "Running" },
    completed: { color: "green", icon: CheckCircle2, label: "Completed" },
    failed: { color: "red", icon: XCircle, label: "Failed" },
    cancelled: { color: "gray", icon: XCircle, label: "Cancelled" },
  };

  const currentStatus = status?.status || "pending";
  const config = statusConfig[currentStatus as keyof typeof statusConfig];
  const StatusIcon = config.icon;

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      {/* Task Overview */}
      <div className="glass rounded-2xl p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-white font-semibold mb-2">Your Task</h3>
            <p className="text-gray-400">{intent}</p>
          </div>
          <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg bg-${config.color}-500/20 border border-${config.color}-500/30`}>
            <StatusIcon className={`w-5 h-5 text-${config.color}-400 ${currentStatus === "running" ? "animate-spin" : ""}`} />
            <span className={`text-${config.color}-300 font-medium`}>{config.label}</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>Progress</span>
            <span>{status ? `${Math.round(status.progress * 100)}%` : "0%"}</span>
          </div>
          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
              style={{ width: `${(status?.progress || 0) * 100}%` }}
            />
          </div>
        </div>

        {/* Task Count */}
        <div className="flex items-center justify-between text-sm text-gray-400">
          <span>Tasks Completed</span>
          <span>{status?.completed_tasks || 0} / {status?.total_tasks || 0}</span>
        </div>
      </div>

      {/* Execution Link */}
      <div className="glass rounded-2xl p-6">
        <h3 className="text-white font-semibold mb-4">Execution Link</h3>
        <div className="flex items-center space-x-2 mb-4">
          <input
            type="text"
            value={`${window.location.origin}${executionLink}`}
            readOnly
            className="flex-1 bg-black/30 border border-white/10 rounded-lg px-4 py-3 text-white text-sm font-mono"
          />
          <button
            onClick={copyLink}
            className="px-4 py-3 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
            title="Copy link"
          >
            <Copy className="w-5 h-5 text-white" />
          </button>
          <a
            href={executionLink}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-lg transition-colors"
            title="Open in new tab"
          >
            <ExternalLink className="w-5 h-5 text-white" />
          </a>
        </div>

        {currentStatus === "ready" && (
          <button
            onClick={handleExecute}
            disabled={executing}
            className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 text-white px-6 py-4 rounded-lg font-medium transition-all"
          >
            {executing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Executing...</span>
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                <span>Execute Now</span>
              </>
            )}
          </button>
        )}
      </div>

      {/* Execution Logs */}
      {status && status.logs.length > 0 && (
        <div className="glass rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-white font-semibold">Execution Logs</h3>
            <button
              onClick={fetchStatus}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              title="Refresh logs"
            >
              <RefreshCw className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {status.logs.map((log) => (
              <div
                key={log.log_id}
                className={`p-3 rounded-lg text-sm font-mono ${
                  log.level === "ERROR"
                    ? "bg-red-500/10 border border-red-500/20 text-red-300"
                    : log.level === "WARNING"
                    ? "bg-yellow-500/10 border border-yellow-500/20 text-yellow-300"
                    : "bg-white/5 border border-white/10 text-gray-300"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs text-gray-500">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="text-xs uppercase">{log.level}</span>
                </div>
                <div>{log.message}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Result */}
      {status?.result && (
        <div className="glass rounded-2xl p-6 border border-green-500/30">
          <h3 className="text-green-300 font-semibold mb-4 flex items-center">
            <CheckCircle2 className="w-5 h-5 mr-2" />
            Execution Result
          </h3>
          <pre className="bg-black/30 rounded-lg p-4 text-sm text-gray-300 overflow-x-auto">
            {JSON.stringify(status.result, null, 2)}
          </pre>
        </div>
      )}

      {/* Error */}
      {status?.error && (
        <div className="glass rounded-2xl p-6 border border-red-500/30">
          <h3 className="text-red-300 font-semibold mb-4 flex items-center">
            <XCircle className="w-5 h-5 mr-2" />
            Execution Error
          </h3>
          <p className="text-red-200">{status.error}</p>
        </div>
      )}
    </div>
  );
}

import { Zap } from "lucide-react";
