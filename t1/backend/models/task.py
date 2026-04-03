"""
Task Models for ZIEL-MAS
Defines the structure of tasks, task graphs (DAGs), and execution states
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import uuid4


class TaskStatus(str, Enum):
    """Status of a task in the execution lifecycle"""
    PENDING = "pending"
    PLANNING = "planning"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class AgentType(str, Enum):
    """Types of worker agents available in the system"""
    CONTROLLER = "controller"
    API = "api"
    WEB_AUTOMATION = "web_automation"
    COMMUNICATION = "communication"
    DATA = "data"
    SCHEDULER = "scheduler"
    VALIDATION = "validation"


class TaskPriority(str, Enum):
    """Priority levels for tasks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskNode(BaseModel):
    """
    Represents a single node in the Task DAG
    Each node is a unit of work assigned to a specific agent
    """
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    agent: AgentType
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    timeout: int = Field(default=300)  # 5 minutes default
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class ConditionalBranch(BaseModel):
    """
    Represents a conditional branch in the task graph
    Allows for dynamic execution paths based on conditions
    """
    condition: str  # Expression to evaluate
    true_tasks: List[str]  # Task IDs to execute if condition is true
    false_tasks: List[str] = Field(default_factory=list)  # Task IDs if false


class TaskGraph(BaseModel):
    """
    Directed Acyclic Graph (DAG) representing the task execution plan
    """
    graph_id: str = Field(default_factory=lambda: str(uuid4()))
    nodes: Dict[str, TaskNode] = Field(default_factory=dict)
    edges: List[Dict[str, str]] = Field(default_factory=list)
    conditional_branches: List[ConditionalBranch] = Field(default_factory=list)
    parallel_execution: bool = Field(default=True)

    def add_node(self, node: TaskNode) -> None:
        """Add a node to the graph"""
        self.nodes[node.task_id] = node

    def add_edge(self, from_task: str, to_task: str) -> None:
        """Add a dependency edge between tasks"""
        self.edges.append({"from": from_task, "to": to_task})
        if to_task not in self.nodes[from_task].dependencies:
            self.nodes[from_task].dependencies.append(to_task)

    def get_ready_tasks(self) -> List[TaskNode]:
        """Get tasks that are ready to execute (all dependencies satisfied)"""
        ready = []
        for task in self.nodes.values():
            if task.status == TaskStatus.PENDING:
                deps_satisfied = all(
                    self.nodes[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                    if dep_id in self.nodes
                )
                if deps_satisfied:
                    ready.append(task)
        return ready

    def is_complete(self) -> bool:
        """Check if all tasks in the graph are complete"""
        return all(
            task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            for task in self.nodes.values()
        )


class TaskExecution(BaseModel):
    """
    Represents a complete task execution from intent to result
    This is stored in MongoDB
    """
    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    intent: str
    task_graph: TaskGraph
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_token: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_summary: Optional[str] = None
    execution_logs: List[Dict[str, Any]] = Field(default_factory=list)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)

    class Config:
        use_enum_values = True


class TaskCreateRequest(BaseModel):
    """Request model for creating a new task from intent"""
    intent: str = Field(..., description="Natural language description of the task")
    priority: TaskPriority = TaskPriority.MEDIUM
    scheduled_at: Optional[datetime] = None
    user_id: Optional[str] = None


class TaskCreateResponse(BaseModel):
    """Response model for task creation"""
    execution_id: str
    execution_link: str
    estimated_duration: Optional[int] = None
    task_count: int


class TaskStatusResponse(BaseModel):
    """Response model for task status queries"""
    execution_id: str
    status: TaskStatus
    progress: float  # 0.0 to 1.0
    completed_tasks: int
    total_tasks: int
    current_task: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: List[Dict[str, Any]] = Field(default_factory=list)


class ExecutionLog(BaseModel):
    """Log entry for task execution"""
    log_id: str = Field(default_factory=lambda: str(uuid4()))
    execution_id: str
    task_id: Optional[str] = None
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
