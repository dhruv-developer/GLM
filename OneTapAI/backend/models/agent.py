"""
Agent Models for ZIEL-MAS
Defines agent configurations, capabilities, and communication protocols
"""

from typing import Dict, Any, List, Optional, Set
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4

from .task import AgentType


class AgentCapability(BaseModel):
    """Represents a specific capability of an agent"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    required_permissions: List[str] = Field(default_factory=list)
    estimated_duration: int = Field(default=60)  # seconds


class AgentConfig(BaseModel):
    """Configuration for a worker agent"""
    agent_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_type: AgentType
    name: str
    description: str
    capabilities: List[AgentCapability] = Field(default_factory=list)
    max_concurrent_tasks: int = Field(default=1)
    timeout: int = Field(default=300)
    retry_enabled: bool = Field(default=True)
    max_retries: int = Field(default=3)
    api_whitelist: List[str] = Field(default_factory=list)
    required_env_vars: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class AgentStatus(str, Enum):
    """Status of an agent in the system"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class AgentState(BaseModel):
    """Runtime state of an agent"""
    agent_id: str
    status: AgentStatus
    current_tasks: List[str] = Field(default_factory=list)  # Task IDs
    completed_tasks: int = Field(default=0)
    failed_tasks: int = Field(default=0)
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)
    uptime: int = Field(default=0)  # seconds

    class Config:
        use_enum_values = True


class AgentMessage(BaseModel):
    """Communication message between agents and controller"""
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    from_agent: str  # Agent ID
    to_agent: str  # Agent ID or "controller"
    message_type: str  # task_assignment, status_update, result, error, heartbeat
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentResponse(BaseModel):
    """Response from an agent after task execution"""
    task_id: str
    agent_id: str
    agent_type: AgentType
    status: str  # completed, failed, partial
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float  # seconds
    retry_count: int = Field(default=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


# Predefined Agent Configurations
AGENT_CONFIGS = {
    AgentType.API: AgentConfig(
        agent_type=AgentType.API,
        name="API Agent",
        description="Executes structured API calls to external services",
        capabilities=[
            AgentCapability(
                name="http_get",
                description="Make HTTP GET requests",
                parameters={"url": "string", "headers": "dict", "params": "dict"},
                required_permissions=["http.request"]
            ),
            AgentCapability(
                name="http_post",
                description="Make HTTP POST requests",
                parameters={"url": "string", "headers": "dict", "body": "dict"},
                required_permissions=["http.request"]
            ),
            AgentCapability(
                name="api_call",
                description="Execute API call with retry logic",
                parameters={"service": "string", "endpoint": "string", "method": "string", "data": "dict"},
                required_permissions=["api.execute"]
            )
        ],
        max_concurrent_tasks=5,
        api_whitelist=["api.github.com", "api.twitter.com", "graph.facebook.com", "www.googleapis.com"]
    ),

    AgentType.WEB_AUTOMATION: AgentConfig(
        agent_type=AgentType.WEB_AUTOMATION,
        name="Web Automation Agent",
        description="Automates browser-based workflows using Playwright",
        capabilities=[
            AgentCapability(
                name="navigate",
                description="Navigate to a URL",
                parameters={"url": "string"},
                required_permissions=["browser.navigate"]
            ),
            AgentCapability(
                name="fill_form",
                description="Fill form fields on a page",
                parameters={"selector": "string", "values": "dict"},
                required_permissions=["browser.interact"]
            ),
            AgentCapability(
                name="click",
                description="Click elements on a page",
                parameters={"selector": "string", "wait_for": "string"},
                required_permissions=["browser.interact"]
            ),
            AgentCapability(
                name="screenshot",
                description="Take screenshot of current page",
                parameters={},
                required_permissions=["browser.screenshot"]
            )
        ],
        max_concurrent_tasks=2,
        timeout=600
    ),

    AgentType.COMMUNICATION: AgentConfig(
        agent_type=AgentType.COMMUNICATION,
        name="Communication Agent",
        description="Sends messages via email, WhatsApp, SMS",
        capabilities=[
            AgentCapability(
                name="send_email",
                description="Send an email",
                parameters={"to": "list", "subject": "string", "body": "string", "attachments": "list"},
                required_permissions=["email.send"]
            ),
            AgentCapability(
                name="send_whatsapp",
                description="Send WhatsApp message",
                parameters={"to": "string", "message": "string"},
                required_permissions=["whatsapp.send"]
            ),
            AgentCapability(
                name="send_sms",
                description="Send SMS message",
                parameters={"to": "string", "message": "string"},
                required_permissions=["sms.send"]
            )
        ],
        max_concurrent_tasks=3,
        required_env_vars=["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"]
    ),

    AgentType.DATA: AgentConfig(
        agent_type=AgentType.DATA,
        name="Data Agent",
        description="Fetches, filters, and ranks data from various sources",
        capabilities=[
            AgentCapability(
                name="fetch_data",
                description="Fetch data from API or database",
                parameters={"source": "string", "query": "dict"},
                required_permissions=["data.fetch"]
            ),
            AgentCapability(
                name="filter_data",
                description="Filter data based on criteria",
                parameters={"data": "list", "filters": "dict"},
                required_permissions=["data.process"]
            ),
            AgentCapability(
                name="rank_data",
                description="Rank items based on scoring function",
                parameters={"data": "list", "scoring_function": "string"},
                required_permissions=["data.process"]
            ),
            AgentCapability(
                name="transform_data",
                description="Transform data structure",
                parameters={"data": "any", "transformation": "string"},
                required_permissions=["data.process"]
            )
        ],
        max_concurrent_tasks=10
    ),

    AgentType.SCHEDULER: AgentConfig(
        agent_type=AgentType.SCHEDULER,
        name="Scheduler Agent",
        description="Handles delayed and recurring task execution",
        capabilities=[
            AgentCapability(
                name="schedule_once",
                description="Schedule task for specific time",
                parameters={"execute_at": "datetime", "task": "dict"},
                required_permissions=["scheduler.create"]
            ),
            AgentCapability(
                name="schedule_recurring",
                description="Schedule recurring task",
                parameters={"cron": "string", "task": "dict"},
                required_permissions=["scheduler.create"]
            ),
            AgentCapability(
                name="cancel_schedule",
                description="Cancel scheduled task",
                parameters={"schedule_id": "string"},
                required_permissions=["scheduler.cancel"]
            )
        ],
        max_concurrent_tasks=1
    ),

    AgentType.VALIDATION: AgentConfig(
        agent_type=AgentType.VALIDATION,
        name="Validation Agent",
        description="Verifies correctness of outputs",
        capabilities=[
            AgentCapability(
                name="validate_output",
                description="Validate task output against schema",
                parameters={"output": "dict", "schema": "dict"},
                required_permissions=["validation.execute"]
            ),
            AgentCapability(
                name="verify_result",
                description="Verify result meets criteria",
                parameters={"result": "any", "criteria": "dict"},
                required_permissions=["validation.execute"]
            ),
            AgentCapability(
                name="sanity_check",
                description="Perform sanity check on output",
                parameters={"output": "any", "checks": "list"},
                required_permissions=["validation.execute"]
            )
        ],
        max_concurrent_tasks=5
    ),

    AgentType.VISION: AgentConfig(
        agent_type=AgentType.VISION,
        name="Vision Agent",
        description="Analyzes images and videos using GLM Vision API",
        capabilities=[
            AgentCapability(
                name="analyze_image",
                description="General-purpose image understanding",
                parameters={"image_path": "string", "image_base64": "string", "prompt": "string"},
                required_permissions=["vision.analyze"]
            ),
            AgentCapability(
                name="analyze_video",
                description="Video understanding and analysis",
                parameters={"video_path": "string", "video_base64": "string", "prompt": "string"},
                required_permissions=["vision.analyze"]
            ),
            AgentCapability(
                name="extract_text",
                description="OCR - Extract text from images",
                parameters={"image_path": "string", "image_base64": "string"},
                required_permissions=["vision.ocr"]
            ),
            AgentCapability(
                name="diagnose_error",
                description="Analyze error screenshots and propose fixes",
                parameters={"image_path": "string", "image_base64": "string", "context": "string"},
                required_permissions=["vision.diagnose"]
            ),
            AgentCapability(
                name="ui_to_code",
                description="Convert UI screenshots to code",
                parameters={"image_path": "string", "image_base64": "string", "framework": "string"},
                required_permissions=["vision.ui_analysis"]
            ),
            AgentCapability(
                name="understand_diagram",
                description="Interpret technical diagrams",
                parameters={"image_path": "string", "image_base64": "string", "diagram_type": "string"},
                required_permissions=["vision.diagram"]
            ),
            AgentCapability(
                name="analyze_chart",
                description="Analyze data visualizations and charts",
                parameters={"image_path": "string", "image_base64": "string"},
                required_permissions=["vision.chart"]
            ),
            AgentCapability(
                name="compare_ui",
                description="Compare two UI screenshots",
                parameters={"image1_path": "string", "image2_path": "string"},
                required_permissions=["vision.compare"]
            )
        ],
        max_concurrent_tasks=3,
        timeout=600,
        required_env_vars=["ZAI_API_KEY"]
    )
}
