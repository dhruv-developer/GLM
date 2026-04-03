"""
Main FastAPI application for ZIEL-MAS
REST API endpoints for task creation, execution, and monitoring
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from typing import Optional
import os
from datetime import datetime
from loguru import logger

from backend.models.task import (
    TaskCreateRequest,
    TaskCreateResponse,
    TaskStatusResponse,
    TaskExecution,
    TaskStatus
)
from backend.services.cache import RedisService
from backend.services.database import DatabaseService
from backend.services.security import SecurityService
from backend.core.controller import ControllerAgent
from backend.core.execution import ExecutionEngine, TaskDispatcher


# Global services
redis_service: Optional[RedisService] = None
db_service: Optional[DatabaseService] = None
security_service: Optional[SecurityService] = None
controller_agent: Optional[ControllerAgent] = None
execution_engine: Optional[ExecutionEngine] = None
task_dispatcher: Optional[TaskDispatcher] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global redis_service, db_service, security_service, controller_agent, execution_engine, task_dispatcher

    logger.info("Starting ZIEL-MAS backend services...")

    # Initialize services
    try:
        redis_service = RedisService(
            redis_url=os.getenv("REDIS_URI", "redis://localhost:6379/0")
        )
        await redis_service.connect()

        db_service = DatabaseService(
            connection_string=os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        )
        await db_service.connect()

        security_service = SecurityService(
            jwt_secret=os.getenv("JWT_SECRET", "your-secret-key"),
            encryption_key=os.getenv("ENCRYPTION_KEY", "your-encryption-key")
        )

        controller_agent = ControllerAgent(
            glm_api_key=os.getenv("GLM_API_KEY", ""),
            glm_api_url=os.getenv("GLM_API_URL", "https://api.glm.ai/v1")
        )

        execution_engine = ExecutionEngine(
            redis_service=redis_service,
            db_service=db_service,
            controller=controller_agent
        )

        task_dispatcher = TaskDispatcher(
            redis_service=redis_service,
            db_service=db_service,
            execution_engine=execution_engine
        )

        logger.info("All services initialized successfully")

        # Start task dispatcher in background
        import asyncio
        asyncio.create_task(task_dispatcher.start())

        yield

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        # Cleanup
        logger.info("Shutting down services...")
        if task_dispatcher:
            await task_dispatcher.stop()
        if redis_service:
            await redis_service.close()
        if db_service:
            await db_service.close()


# Initialize FastAPI app
app = FastAPI(
    title="ZIEL-MAS API",
    description="Zero-Interaction Execution Links with Multi-Agent System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Dependency injection
def get_redis() -> RedisService:
    return redis_service


def get_database() -> DatabaseService:
    return db_service


def get_security() -> SecurityService:
    return security_service


def get_controller() -> ControllerAgent:
    return controller_agent


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_health = await redis_service.get_info()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "redis": "connected" if redis_service else "disconnected",
                "database": "connected" if db_service else "disconnected"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


# Create task endpoint
@app.post("/api/v1/create-task", response_model=TaskCreateResponse)
async def create_task(
    request: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    security: SecurityService = Depends(get_security),
    controller: ControllerAgent = Depends(get_controller),
    db: DatabaseService = Depends(get_database),
    redis: RedisService = Depends(get_redis)
):
    """
    Create a new task from natural language intent
    Returns an execution link
    """
    try:
        # Validate intent for security
        is_valid, error_msg = security.validate_intent(request.intent)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        # Parse intent
        parsed_intent = await controller.parse_intent(request.intent)

        # Generate task graph
        task_graph = await controller.generate_task_graph(
            parsed_intent,
            request.user_id
        )

        # Create execution
        execution = TaskExecution(
            user_id=request.user_id,
            intent=request.intent,
            task_graph=task_graph,
            priority=request.priority,
            status=TaskStatus.PENDING
        )

        # Generate execution token
        execution_token = security.generate_execution_token(
            execution.execution_id,
            request.user_id
        )
        execution.execution_token = execution_token

        # Store in database
        await db.create_task_execution(execution.dict())

        # Store token in Redis for quick lookup
        await redis.store_token(execution_token, execution.execution_id)

        # Store initial state
        await redis.set_task_status(execution.execution_id, TaskStatus.PENDING.value)
        await redis.set_task_progress(execution.execution_id, 0.0)

        # Generate execution link
        execution_link = f"/execute/{execution_token}"

        # Estimate duration
        estimated_duration = await controller.estimate_execution_time(task_graph)

        logger.info(f"Created task {execution.execution_id} for intent: {request.intent}")

        return TaskCreateResponse(
            execution_id=execution.execution_id,
            execution_link=execution_link,
            estimated_duration=estimated_duration,
            task_count=len(task_graph.nodes)
        )

    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Execute task endpoint
@app.get("/api/v1/execute/{token}")
async def execute_task(
    token: str,
    background_tasks: BackgroundTasks,
    security: SecurityService = Depends(get_security),
    redis: RedisService = Depends(get_redis),
    db: DatabaseService = Depends(get_database),
    controller: ControllerAgent = Depends(get_controller)
):
    """
    Execute a task via secure token
    This is the zero-interaction execution endpoint
    """
    try:
        # Validate token
        payload = security.validate_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        execution_id = payload.get("execution_id")
        if not execution_id:
            raise HTTPException(status_code=400, detail="Invalid token payload")

        # Get execution from database
        execution_data = await db.get_task_execution(execution_id)
        if not execution_data:
            raise HTTPException(status_code=404, detail="Task execution not found")

        # Check if already executed
        current_status = await redis.get_task_status(execution_id)
        if current_status == TaskStatus.COMPLETED.value:
            return {
                "message": "Task already completed",
                "execution_id": execution_id,
                "status": "completed"
            }

        # Queue for execution
        await redis.push_to_queue("pending_executions", execution_id)

        # Update status
        await redis.set_task_status(execution_id, TaskStatus.READY.value)

        logger.info(f"Executing task {execution_id} via token")

        return {
            "message": "Task execution started",
            "execution_id": execution_id,
            "status": "started",
            "monitor_link": f"/api/v1/status/{execution_id}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Task status endpoint
@app.get("/api/v1/status/{execution_id}", response_model=TaskStatusResponse)
async def get_task_status(
    execution_id: str,
    redis: RedisService = Depends(get_redis),
    db: DatabaseService = Depends(get_database)
):
    """
    Get detailed status of a task execution
    """
    try:
        # Get from cache
        status = await redis.get_task_status(execution_id)
        progress = await redis.get_task_progress(execution_id)

        # Get from database for full details
        execution = await db.get_task_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Task execution not found")

        # Get recent logs
        logs = await db.get_execution_logs(execution_id, limit=20)

        # Calculate progress
        task_graph = execution.get("task_graph", {})
        total_tasks = len(task_graph.get("nodes", {}))

        completed_tasks = sum(
            1 for node in task_graph.get("nodes", {}).values()
            if node.get("status") == "completed"
        )

        calculated_progress = completed_tasks / total_tasks if total_tasks > 0 else 0.0

        return TaskStatusResponse(
            execution_id=execution_id,
            status=TaskStatus(status or "pending"),
            progress=float(progress) if progress else calculated_progress,
            completed_tasks=completed_tasks,
            total_tasks=total_tasks,
            result=execution.get("result"),
            error=execution.get("error_summary"),
            logs=logs
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Cancel task endpoint
@app.post("/api/v1/cancel/{execution_id}")
async def cancel_task(
    execution_id: str,
    redis: RedisService = Depends(get_redis),
    db: DatabaseService = Depends(get_database)
):
    """Cancel a running task execution"""
    try:
        # Update status
        await redis.set_task_status(execution_id, TaskStatus.CANCELLED.value)
        await db.update_task_execution(execution_id, {
            "status": TaskStatus.CANCELLED.value,
            "completed_at": datetime.utcnow()
        })

        return {
            "message": "Task cancelled successfully",
            "execution_id": execution_id
        }

    except Exception as e:
        logger.error(f"Failed to cancel task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get task logs endpoint
@app.get("/api/v1/logs/{execution_id}")
async def get_task_logs(
    execution_id: str,
    level: Optional[str] = None,
    limit: int = 100,
    db: DatabaseService = Depends(get_database)
):
    """Get execution logs for a task"""
    try:
        logs = await db.get_execution_logs(execution_id, level=level, limit=limit)

        return {
            "execution_id": execution_id,
            "logs": logs,
            "count": len(logs)
        }

    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# User tasks endpoint
@app.get("/api/v1/user/{user_id}/tasks")
async def get_user_tasks(
    user_id: str,
    status: Optional[str] = None,
    limit: int = 50,
    db: DatabaseService = Depends(get_database)
):
    """Get all tasks for a user"""
    try:
        tasks = await db.list_user_tasks(user_id, status=status, limit=limit)

        return {
            "user_id": user_id,
            "tasks": tasks,
            "count": len(tasks)
        }

    except Exception as e:
        logger.error(f"Failed to get user tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Statistics endpoint
@app.get("/api/v1/stats")
async def get_statistics(
    db: DatabaseService = Depends(get_database),
    redis: RedisService = Depends(get_redis)
):
    """Get system statistics"""
    try:
        db_stats = await db.get_statistics()
        redis_info = await redis.get_info()

        return {
            "database": db_stats,
            "cache": redis_info,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
