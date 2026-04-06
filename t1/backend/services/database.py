"""
Database Service for ZIEL-MAS
MongoDB integration for persistent storage
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger

from backend.models.database import (
    TaskExecutionDocument,
    ExecutionLogDocument,
    AgentStateDocument,
    AuditLogDocument,
    UserDocument
)


class DatabaseService:
    """
    MongoDB service for persistent storage
    Handles task executions, logs, agent states, and audit trails
    """

    def __init__(self, connection_string: str = "mongodb://localhost:27017"):
        self.connection_string = connection_string
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client.ziel_mas
            await self._create_indexes()
            logger.info(f"Connected to MongoDB at {self.connection_string}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

    async def _create_indexes(self):
        """Create database indexes for optimal performance"""
        # Task executions collection
        await self.db.task_executions.create_index("execution_id", unique=True)
        await self.db.task_executions.create_index("user_id")
        await self.db.task_executions.create_index("status")
        await self.db.task_executions.create_index("created_at")
        await self.db.task_executions.create_index("execution_token")

        # Execution logs collection
        await self.db.execution_logs.create_index("execution_id")
        await self.db.execution_logs.create_index("timestamp")
        await self.db.execution_logs.create_index("level")

        # Agent states collection
        await self.db.agent_states.create_index("agent_id", unique=True)
        await self.db.agent_states.create_index("status")

        # Audit logs collection
        await self.db.audit_logs.create_index("timestamp")
        await self.db.audit_logs.create_index("execution_id")
        await self.db.audit_logs.create_index("user_id")

        # Users collection
        await self.db.users.create_index("user_id", unique=True)
        await self.db.users.create_index("email", unique=True)

        logger.info("Database indexes created successfully")

    # Task Execution Methods

    async def create_task_execution(self, execution_data: Dict[str, Any]) -> str:
        """Create a new task execution"""
        try:
            result = await self.db.task_executions.insert_one(execution_data)
            logger.info(f"Created task execution: {execution_data['execution_id']}")
            return execution_data["execution_id"]
        except Exception as e:
            logger.error(f"Failed to create task execution: {e}")
            raise

    async def get_task_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get task execution by ID"""
        try:
            execution = await self.db.task_executions.find_one({"execution_id": execution_id})
            if execution:
                # Convert ObjectId to string for JSON serialization
                if "_id" in execution:
                    execution["_id"] = str(execution["_id"])
            return execution
        except Exception as e:
            logger.error(f"Failed to get task execution {execution_id}: {e}")
            return None

    async def update_task_execution(self, execution_id: str, updates: Dict[str, Any]) -> bool:
        """Update task execution"""
        try:
            result = await self.db.task_executions.update_one(
                {"execution_id": execution_id},
                {"$set": updates}
            )
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated task execution: {execution_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to update task execution {execution_id}: {e}")
            return False

    async def get_task_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Get task execution by execution token"""
        try:
            execution = await self.db.task_executions.find_one({"execution_token": token})
            if execution:
                # Convert ObjectId to string for JSON serialization
                if "_id" in execution:
                    execution["_id"] = str(execution["_id"])
            return execution
        except Exception as e:
            logger.error(f"Failed to get task by token: {e}")
            return None

    async def list_user_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """List tasks for a user with optional filtering"""
        try:
            query = {"user_id": user_id}
            if status:
                query["status"] = status

            cursor = self.db.task_executions.find(query).sort("created_at", -1).skip(skip).limit(limit)
            tasks = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON serialization
            for task in tasks:
                if "_id" in task:
                    task["_id"] = str(task["_id"])
            
            return tasks
        except Exception as e:
            logger.error(f"Failed to list user tasks: {e}")
            return []

    async def delete_task_execution(self, execution_id: str) -> bool:
        """Delete a task execution (soft delete by updating status)"""
        try:
            result = await self.db.task_executions.update_one(
                {"execution_id": execution_id},
                {"$set": {"status": "deleted", "deleted_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to delete task execution {execution_id}: {e}")
            return False

    async def delete_task(self, execution_id: str) -> bool:
        """Delete a task completely (hard delete)"""
        try:
            # Delete task execution
            task_result = await self.db.task_executions.delete_one({"execution_id": execution_id})
            
            # Delete associated logs
            logs_result = await self.db.execution_logs.delete_many({"execution_id": execution_id})
            
            logger.info(f"Deleted task {execution_id}: {task_result.deleted_count} task, {logs_result.deleted_count} logs")
            return task_result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete task {execution_id}: {e}")
            return False

    async def get_task(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by execution_id"""
        try:
            task = await self.db.task_executions.find_one({"execution_id": execution_id})
            if task:
                # Convert ObjectId to string
                task["_id"] = str(task["_id"])
                return task
            return None
        except Exception as e:
            logger.error(f"Failed to get task {execution_id}: {e}")
            return None

    # Execution Log Methods

    async def create_execution_log(self, log_data: Dict[str, Any]) -> str:
        """Create an execution log entry"""
        try:
            await self.db.execution_logs.insert_one(log_data)
            return log_data["log_id"]
        except Exception as e:
            logger.error(f"Failed to create execution log: {e}")
            raise

    async def get_execution_logs(
        self,
        execution_id: str,
        level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get execution logs for a task"""
        try:
            query = {"execution_id": execution_id}
            if level:
                query["level"] = level

            cursor = self.db.execution_logs.find(query).sort("timestamp", -1).limit(limit)
            logs = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON serialization
            for log in logs:
                if "_id" in log:
                    log["_id"] = str(log["_id"])
            
            return logs
        except Exception as e:
            logger.error(f"Failed to get execution logs: {e}")
            return []

    async def delete_old_logs(self, days: int = 30) -> int:
        """Delete logs older than specified days"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = await self.db.execution_logs.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            logger.info(f"Deleted {result.deleted_count} old logs")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Failed to delete old logs: {e}")
            return 0

    # Agent State Methods

    async def update_agent_state(self, agent_id: str, state_data: Dict[str, Any]) -> bool:
        """Update or create agent state"""
        try:
            result = await self.db.agent_states.update_one(
                {"agent_id": agent_id},
                {"$set": state_data},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Failed to update agent state: {e}")
            return False

    async def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent state"""
        try:
            agent = await self.db.agent_states.find_one({"agent_id": agent_id})
            if agent:
                # Convert ObjectId to string for JSON serialization
                if "_id" in agent:
                    agent["_id"] = str(agent["_id"])
            return agent
        except Exception as e:
            logger.error(f"Failed to get agent state: {e}")
            return None

    async def list_agents(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all agents with optional status filter"""
        try:
            query = {}
            if status:
                query["status"] = status

            cursor = self.db.agent_states.find(query)
            agents = await cursor.to_list(length=None)
            
            # Convert ObjectId to string for JSON serialization
            for agent in agents:
                if "_id" in agent:
                    agent["_id"] = str(agent["_id"])
            
            return agents
        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return []

    # Audit Log Methods

    async def create_audit_log(self, audit_data: Dict[str, Any]) -> str:
        """Create an audit log entry"""
        try:
            await self.db.audit_logs.insert_one(audit_data)
            return audit_data["audit_id"]
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            raise

    async def get_audit_logs(
        self,
        execution_id: Optional[str] = None,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit logs with filters"""
        try:
            query = {}
            if execution_id:
                query["execution_id"] = execution_id
            if user_id:
                query["user_id"] = user_id
            if event_type:
                query["event_type"] = event_type

            cursor = self.db.audit_logs.find(query).sort("timestamp", -1).limit(limit)
            logs = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON serialization
            for log in logs:
                if "_id" in log:
                    log["_id"] = str(log["_id"])
            
            return logs
        except Exception as e:
            logger.error(f"Failed to get audit logs: {e}")
            return []

    # User Methods

    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        try:
            await self.db.users.insert_one(user_data)
            return user_data["user_id"]
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = await self.db.users.find_one({"user_id": user_id})
            if user:
                # Convert ObjectId to string for JSON serialization
                if "_id" in user:
                    user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = await self.db.users.find_one({"email": email})
            if user:
                # Convert ObjectId to string for JSON serialization
                if "_id" in user:
                    user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None

    async def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            result = await self.db.users.update_one(
                {"user_id": user_id},
                {"$set": updates}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            return False

    # Statistics Methods

    async def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            task_count = await self.db.task_executions.count_documents({})
            log_count = await self.db.execution_logs.count_documents({})
            agent_count = await self.db.agent_states.count_documents({})
            user_count = await self.db.users.count_documents({})

            # Task status distribution
            status_pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            status_dist = await self.db.task_executions.aggregate(status_pipeline).to_list(None)

            return {
                "total_tasks": task_count,
                "total_logs": log_count,
                "total_agents": agent_count,
                "total_users": user_count,
                "task_status_distribution": {
                    item["_id"]: item["count"] for item in status_dist
                }
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
