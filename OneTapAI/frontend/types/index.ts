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
  web_search_results?: WebSearchResult[];
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

export interface WebSearchResult {
  query: string;
  results: SearchResultItem[];
  total_results: number;
  search_type?: "web" | "news" | "realtime" | "technical";
}

export interface SearchResultItem {
  title: string;
  url: string;
  snippet: string;
  site_name?: string;
  published_date?: string;
  author?: string;
  thumbnail?: string;
}

export interface AgentExecution {
  task_id: string;
  agent: string;
  action: string;
  status: string;
  output?: any;
  error?: string;
  started_at?: string;
  completed_at?: string;
}

export interface VisionAnalysisResult {
  analysis_type: string;
  prompt: string;
  result: {
    success: boolean;
    analysis?: string;
    mock?: boolean;
    error?: string;
    details?: string;
    model?: string;
    usage?: any;
  };
  execution_time?: number;
  timestamp: string;
  image_analyzed: boolean;
}

export interface VisionAnalysisRequest {
  image_base64?: string;
  prompt?: string;
  analysis_type?: "general" | "extract_text" | "diagnose_error" | "ui_to_code" | "understand_diagram" | "analyze_chart" | "video";
  context?: string;
  framework?: string;
  language?: string;
}
