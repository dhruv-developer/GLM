export interface TaskStatus {
  execution_id: string;
  status: "pending" | "planning" | "ready" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  completed_tasks: number;
  total_tasks: number;
  current_task?: string;
  result?: any;
  error?: string;
  logs: LogEntry[];
}

export interface LogEntry {
  log_id: string;
  execution_id: string;
  task_id?: string;
  level: string;
  message: string;
  timestamp: string;
}

export interface CreateTaskRequest {
  intent: string;
  priority?: "low" | "medium" | "high";
  user_id?: string;
}

export interface CreateTaskResponse {
  execution_id: string;
  execution_link: string;
  estimated_duration?: number;
  task_count: number;
}

export interface TaskNode {
  task_id: string;
  agent: string;
  action: string;
  status: string;
  started_at?: string;
  completed_at?: string;
}
