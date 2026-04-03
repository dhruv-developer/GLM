"""
Database Models for ZIEL-MAS
MongoDB schemas for persistent storage
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from uuid import uuid4
from enum import Enum

from pymongo import MongoClient, IndexModel, ASCENDING, DESCENDING
from motor.motor_asyncio import AsyncIOMotorClient
import os


class MongoDB:
    """MongoDB connection manager"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self, connection_string: str):
        """Establish MongoDB connection"""
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.ziel_mas
        await self._create_indexes()

    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

    async def _create_indexes(self):
        """Create database indexes for performance"""
        # Task execution indexes
        await self.db.task_executions.create_index([("execution_id", ASCENDING)], unique=True)
        await self.db.task_executions.create_index([("user_id", ASCENDING)])
        await self.db.task_executions.create_index([("status", ASCENDING)])
        await self.db.task_executions.create_index([("created_at", DESCENDING)])
        await self.db.task_executions.create_index([("execution_token", ASCENDING)])

        # Execution logs indexes
        await self.db.execution_logs.create_index([("execution_id", ASCENDING)])
        await self.db.execution_logs.create_index([("timestamp", DESCENDING)])
        await self.db.execution_logs.create_index([("level", ASCENDING)])

        # Agent state indexes
        await self.db.agent_states.create_index([("agent_id", ASCENDING)], unique=True)
        await self.db.agent_states.create_index([("status", ASCENDING)])

        # Audit logs indexes
        await self.db.audit_logs.create_index([("timestamp", DESCENDING)])
        await self.db.audit_logs.create_index([("execution_id", ASCENDING)])
        await self.db.audit_logs.create_index([("user_id", ASCENDING)])

    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        return self.db[collection_name]


# Task Execution Document Schema
class TaskExecutionDocument(BaseModel):
    """MongoDB document for task execution"""
    _id: Optional[str] = None
    execution_id: str
    user_id: Optional[str] = None
    intent: str
    task_graph: Dict[str, Any]  # Serialized TaskGraph
    status: str
    priority: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_token: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error_summary: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Execution Log Document Schema
class ExecutionLogDocument(BaseModel):
    """MongoDB document for execution logs"""
    _id: Optional[str] = None
    log_id: str
    execution_id: str
    task_id: Optional[str] = None
    level: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Agent State Document Schema
class AgentStateDocument(BaseModel):
    """MongoDB document for agent state"""
    _id: Optional[str] = None
    agent_id: str
    agent_type: str
    status: str
    current_tasks: List[str] = Field(default_factory=list)
    completed_tasks: int = 0
    failed_tasks: int = 0
    last_heartbeat: datetime
    uptime: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Audit Log Document Schema
class AuditLogDocument(BaseModel):
    """MongoDB document for audit logging"""
    _id: Optional[str] = None
    audit_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_type: str  # task_created, task_started, task_completed, etc.
    execution_id: str
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# User Document Schema (optional, for user management)
class UserDocument(BaseModel):
    """MongoDB document for users"""
    _id: Optional[str] = None
    user_id: str = Field(default_factory=lambda: str(uuid4()))
    email: str
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: Optional[datetime] = None
    total_tasks: int = 0
    preferences: Dict[str, Any] = Field(default_factory=dict)
    api_key: Optional[str] = None
    rate_limit: int = 100  # requests per hour


# Database helper functions
async def create_task_execution(db, execution_data: TaskExecutionDocument) -> str:
    """Create a new task execution document"""
    collection = db.get_collection("task_executions")
    await collection.insert_one(execution_data.dict(exclude={"_id"}))
    return execution_data.execution_id


async def get_task_execution(db, execution_id: str) -> Optional[Dict[str, Any]]:
    """Get a task execution by ID"""
    collection = db.get_collection("task_executions")
    return await collection.find_one({"execution_id": execution_id})


async def update_task_execution(db, execution_id: str, updates: Dict[str, Any]) -> bool:
    """Update a task execution"""
    collection = db.get_collection("task_executions")
    result = await collection.update_one(
        {"execution_id": execution_id},
        {"$set": updates}
    )
    return result.modified_count > 0


async def get_task_by_token(db, token: str) -> Optional[Dict[str, Any]]:
    """Get a task execution by execution token"""
    collection = db.get_collection("task_executions")
    return await collection.find_one({"execution_token": token})


async def create_execution_log(db, log_data: ExecutionLogDocument) -> str:
    """Create an execution log entry"""
    collection = db.get_collection("execution_logs")
    await collection.insert_one(log_data.dict(exclude={"_id"}))
    return log_data.log_id


async def get_execution_logs(db, execution_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get execution logs for a task"""
    collection = db.get_collection("execution_logs")
    cursor = collection.find({"execution_id": execution_id}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def update_agent_state(db, agent_id: str, state_data: Dict[str, Any]) -> bool:
    """Update agent state"""
    collection = db.get_collection("agent_states")
    result = await collection.update_one(
        {"agent_id": agent_id},
        {"$set": state_data},
        upsert=True
    )
    return result.acknowledged


async def get_agent_state(db, agent_id: str) -> Optional[Dict[str, Any]]:
    """Get agent state"""
    collection = db.get_collection("agent_states")
    return await collection.find_one({"agent_id": agent_id})


async def create_audit_log(db, audit_data: AuditLogDocument) -> str:
    """Create an audit log entry"""
    collection = db.get_collection("audit_logs")
    await collection.insert_one(audit_data.dict(exclude={"_id"}))
    return audit_data.audit_id


async def get_user_tasks(db, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Get all tasks for a user"""
    collection = db.get_collection("task_executions")
    cursor = collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    return await cursor.to_list(length=limit)
