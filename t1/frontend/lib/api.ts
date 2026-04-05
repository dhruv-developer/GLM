import { CreateTaskRequest, CreateTaskResponse, TaskStatus, LogEntry } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function createTask(request: CreateTaskRequest): Promise<CreateTaskResponse> {
  const response = await fetch(`${API_BASE}/api/v1/create-task`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ...request,
      user_id: request.user_id || process.env.NEXT_PUBLIC_DEFAULT_USER_ID || "default_user_001",
    }),
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

export async function getTaskLogs(executionId: string, level?: string, limit = 100): Promise<{ logs: LogEntry[]; count: number }> {
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

export async function getUserTasks(userId?: string, status?: string, limit = 50) {
  const params = new URLSearchParams();
  params.append("limit", limit.toString());
  if (status) params.append("status", status);

  const response = await fetch(
    `${API_BASE}/api/v1/user/${userId || process.env.NEXT_PUBLIC_DEFAULT_USER_ID || "default_user_001"}/tasks?${params}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get user tasks");
  }

  return response.json();
}

export async function getStatistics() {
  const response = await fetch(`${API_BASE}/api/v1/stats`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get statistics");
  }

  return response.json();
}

export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`);

  if (!response.ok) {
    throw new Error("Backend is unhealthy");
  }

  return response.json();
}

// Vision Analysis Endpoints
export async function analyzeImage(
  file: File,
  prompt: string = "Describe this image in detail",
  analysisType: string = "general",
  context: string = ""
) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("prompt", prompt);
  formData.append("analysis_type", analysisType);
  formData.append("context", context);

  const response = await fetch(`${API_BASE}/api/v1/vision/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to analyze image");
  }

  return response.json();
}

export async function analyzeImageBase64(request: {
  image_base64: string;
  prompt?: string;
  analysis_type?: string;
  context?: string;
  framework?: string;
  language?: string;
}) {
  const response = await fetch(`${API_BASE}/api/v1/vision/analyze-base64`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to analyze image");
  }

  return response.json();
}

export async function analyzeVideo(
  file: File,
  prompt: string = "Describe this video in detail"
) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("prompt", prompt);

  const response = await fetch(`${API_BASE}/api/v1/vision/analyze-video`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to analyze video");
  }

  return response.json();
}

export async function compareUI(image1: File, image2: File) {
  const formData = new FormData();
  formData.append("image1", image1);
  formData.append("image2", image2);

  const response = await fetch(`${API_BASE}/api/v1/vision/compare-ui`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to compare UI");
  }

  return response.json();
}
