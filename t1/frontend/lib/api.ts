import { CreateTaskRequest, CreateTaskResponse, TaskStatus } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createTask(request: CreateTaskRequest): Promise<CreateTaskResponse> {
  const response = await fetch(`${API_BASE}/api/v1/create-task`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create task");
  }

  return response.json();
}

export async function executeTask(token: string) {
  const response = await fetch(`${API_BASE}/api/v1/execute/${token}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to execute task");
  }

  return response.json();
}

export async function getTaskStatus(executionId: string): Promise<TaskStatus> {
  const response = await fetch(`${API_BASE}/api/v1/status/${executionId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get task status");
  }

  return response.json();
}

export async function getTaskLogs(executionId: string, level?: string, limit = 100) {
  const params = new URLSearchParams();
  if (level) params.append("level", level);
  params.append("limit", limit.toString());

  const response = await fetch(`${API_BASE}/api/v1/logs/${executionId}?${params}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get task logs");
  }

  return response.json();
}

export async function cancelTask(executionId: string) {
  const response = await fetch(`${API_BASE}/api/v1/cancel/${executionId}`, {
    method: "POST",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to cancel task");
  }

  return response.json();
}
