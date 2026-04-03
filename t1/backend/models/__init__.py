"""
Models Package for ZIEL-MAS
"""

from .task import (
    TaskStatus,
    AgentType,
    TaskPriority,
    TaskNode,
    ConditionalBranch,
    TaskGraph,
    TaskExecution,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskStatusResponse,
    ExecutionLog
)

from .agent import (
    AgentCapability,
    AgentConfig,
    AgentStatus,
    AgentState,
    AgentMessage,
    AgentResponse,
    AGENT_CONFIGS
)

from .database import (
    MongoDB,
    TaskExecutionDocument,
    ExecutionLogDocument,
    AgentStateDocument,
    AuditLogDocument,
    UserDocument,
    create_task_execution,
    get_task_execution,
    update_task_execution,
    get_task_by_token,
    create_execution_log,
    get_execution_logs,
    update_agent_state,
    get_agent_state,
    create_audit_log,
    get_user_tasks
)

__all__ = [
    # Task models
    "TaskStatus",
    "AgentType",
    "TaskPriority",
    "TaskNode",
    "ConditionalBranch",
    "TaskGraph",
    "TaskExecution",
    "TaskCreateRequest",
    "TaskCreateResponse",
    "TaskStatusResponse",
    "ExecutionLog",

    # Agent models
    "AgentCapability",
    "AgentConfig",
    "AgentStatus",
    "AgentState",
    "AgentMessage",
    "AgentResponse",
    "AGENT_CONFIGS",

    # Database models
    "MongoDB",
    "TaskExecutionDocument",
    "ExecutionLogDocument",
    "AgentStateDocument",
    "AuditLogDocument",
    "UserDocument",
    "create_task_execution",
    "get_task_execution",
    "update_task_execution",
    "get_task_by_token",
    "create_execution_log",
    "get_execution_logs",
    "update_agent_state",
    "get_agent_state",
    "create_audit_log",
    "get_user_tasks",
]
