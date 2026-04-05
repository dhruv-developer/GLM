"""
Main FastAPI application for ZIEL-MAS
REST API endpoints for task creation, execution, and monitoring
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from typing import Optional
import os
import json
from datetime import datetime
from loguru import logger
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
from backend.services.task_completion_formatter import TaskCompletionFormatter
from backend.services.enhanced_task_formatter import EnhancedTaskFormatter
from backend.core.reasoning_engine import ReasoningEngine
from backend.core.enhanced_reasoning_engine import EnhancedReasoningEngine


# Global services
redis_service: Optional[RedisService] = None
db_service: Optional[DatabaseService] = None
security_service: Optional[SecurityService] = None
controller_agent: Optional[ControllerAgent] = None
reasoning_engine: Optional[ReasoningEngine] = None
enhanced_reasoning_engine: Optional[EnhancedReasoningEngine] = None
execution_engine: Optional[ExecutionEngine] = None
task_dispatcher: Optional[TaskDispatcher] = None
task_formatter: Optional[TaskCompletionFormatter] = None
enhanced_task_formatter: Optional[EnhancedTaskFormatter] = None


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles ObjectId and other non-serializable types"""
    
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CustomJSONResponse(JSONResponse):
    """Custom JSONResponse that uses the CustomJSONEncoder"""
    
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=CustomJSONEncoder,
        ).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    global redis_service, db_service, security_service, controller_agent, reasoning_engine, execution_engine, task_dispatcher, task_formatter

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

        reasoning_engine = ReasoningEngine(
            db_service=db_service,
            redis_service=redis_service,
            glm_api_key=os.getenv("GLM_API_KEY", ""),
            glm_api_url=os.getenv("GLM_API_URL", "https://api.glm.ai/v1")
        )

        # Initialize enhanced reasoning engine (GLM-like UX with brute force reliability)
        enhanced_reasoning_engine = EnhancedReasoningEngine(
            db_service=db_service,
            redis_service=redis_service,
            glm_api_key=os.getenv("GLM_API_KEY", ""),
            glm_api_url=os.getenv("GLM_API_URL", "https://api.glm.ai/v1")
        )

        execution_engine = ExecutionEngine(
            redis_service=redis_service,
            db_service=db_service,
            controller=controller_agent,
            reasoning_engine=reasoning_engine
        )

        task_dispatcher = TaskDispatcher(
            redis_service=redis_service,
            db_service=db_service,
            execution_engine=execution_engine
        )

        task_formatter = TaskCompletionFormatter()
        
        # Initialize enhanced task formatter for beautiful user displays
        enhanced_task_formatter = EnhancedTaskFormatter()

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
    lifespan=lifespan,
    default_response_class=CustomJSONResponse
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


def get_reasoning_engine() -> ReasoningEngine:
    return reasoning_engine


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
        await db.create_task_execution(execution.model_dump())

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

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
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
        
        # Use database values first, then fall back to calculation
        completed_tasks = execution.get("completed_tasks", 0)
        if completed_tasks == 0:
            # Only calculate from task graph if not stored in database
            completed_tasks = sum(
                1 for node in task_graph.get("nodes", {}).values()
                if node.get("status") == "completed"
            )

        calculated_progress = completed_tasks / total_tasks if total_tasks > 0 else 0.0

        # Create response data
        response_data = {
            "execution_id": execution_id,
            "status": TaskStatus(status or "pending"),
            "progress": float(progress) if progress else calculated_progress,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "result": execution.get("result"),
            "error": execution.get("error_summary"),
            "logs": logs
        }

        # Add user-friendly summary if task formatter is available
        if task_formatter:
            # Add the original intent for better formatting
            response_data["intent"] = execution.get("intent", "No intent provided")
            
            # Extract generated code and filename for download
            result = execution.get("result", {})
            if result and isinstance(result, dict):
                # Handle code generation results
                if "code" in result:
                    response_data["generated_code"] = result["code"]
                    response_data["download_filename"] = result.get("filename", "generated_code.py")
                # Handle project results with multiple files
                elif "files" in result and isinstance(result["files"], list):
                    # For projects, create a combined file or use the main file
                    main_file = result["files"][0] if result["files"] else {}
                    if "content" in main_file:
                        response_data["generated_code"] = main_file["content"]
                        response_data["download_filename"] = main_file.get("filename", "project_main.py")
                # Handle other result types
                elif "output" in result and isinstance(result["output"], dict):
                    output = result["output"]
                    if "code" in output:
                        response_data["generated_code"] = output["code"]
                        response_data["download_filename"] = output.get("filename", "output.py")
            
            # Add enhanced user summary for beautiful display
            try:
                if enhanced_task_formatter:
                    enhanced_summary = enhanced_task_formatter.format_enhanced_summary(response_data)
                    response_data["user_summary"] = enhanced_summary
                    
                    # Add quick summary for easy display
                    quick_summary = enhanced_task_formatter.format_quick_summary_enhanced(response_data)
                    response_data["quick_summary"] = quick_summary
                    
            except Exception as e:
                logger.warning(f"Failed to format enhanced user summary: {e}")
                response_data["user_summary"] = "Enhanced summary formatting unavailable"
                response_data["quick_summary"] = f"Task {execution_id[:8]}... ({status or 'pending'})"

        return TaskStatusResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Download generated code endpoint
@app.get("/api/v1/download/{execution_id}")
async def download_generated_code(
    execution_id: str,
    db: DatabaseService = Depends(get_database)
):
    """
    Download generated code as a file
    """
    try:
        # Get execution data
        execution = await db.get_task_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Task execution not found")
        
        # Extract code and filename
        result = execution.get("result", {})
        code_content = None
        filename = "generated_code.py"
        
        if result and isinstance(result, dict):
            # Handle code generation results
            if "code" in result:
                code_content = result["code"]
                filename = result.get("filename", "generated_code.py")
            # Handle project results
            elif "files" in result and isinstance(result["files"], list):
                main_file = result["files"][0] if result["files"] else {}
                if "content" in main_file:
                    code_content = main_file["content"]
                    filename = main_file.get("filename", "project_main.py")
            # Handle other result types
            elif "output" in result and isinstance(result["output"], dict):
                output = result["output"]
                if "code" in output:
                    code_content = output["code"]
                    filename = output.get("filename", "output.py")
        
        if not code_content:
            raise HTTPException(status_code=404, detail="No downloadable code found")
        
        # Return file for download
        from fastapi.responses import Response
        
        return Response(
            content=code_content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download code: {e}")
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
    skip: int = 0,
    db: DatabaseService = Depends(get_database)
):
    """Get all tasks for a user"""
    try:
        tasks = await db.list_user_tasks(user_id, status=status, limit=limit, skip=skip)

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


# Code Writer Endpoints
@app.post("/api/v1/code/write-file")
async def write_code_file(request_data: dict):
    """
    Write a single code file
    """
    try:
        from backend.agents.code_writer_agent import CodeWriterAgent

        code_writer = CodeWriterAgent()

        result = await code_writer.execute("write_file", request_data)

        if result.get("status") == "completed":
            return {
                "success": True,
                "code": result.get("output"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Code writing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/code/write-project")
async def write_code_project(request_data: dict):
    """
    Write a complete multi-file project
    """
    try:
        from backend.agents.code_writer_agent import CodeWriterAgent

        code_writer = CodeWriterAgent()

        result = await code_writer.execute("write_project", request_data)

        if result.get("status") == "completed":
            return {
                "success": True,
                "project": result.get("output"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Project writing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/code/write-application")
async def write_application(request_data: dict):
    """
    Write a complete application
    """
    try:
        from backend.agents.code_writer_agent import CodeWriterAgent

        code_writer = CodeWriterAgent()

        result = await code_writer.execute("write_application", request_data)

        if result.get("status") == "completed":
            return {
                "success": True,
                "application": result.get("output"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Application writing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/code/refactor")
async def refactor_code(request_data: dict):
    """
    Refactor existing code
    """
    try:
        from backend.agents.code_writer_agent import CodeWriterAgent

        code_writer = CodeWriterAgent()

        result = await code_writer.execute("refactor_code", request_data)

        if result.get("status") == "completed":
            return {
                "success": True,
                "refactored_code": result.get("output"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Refactoring failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/code/fix-bug")
async def fix_bug(request_data: dict):
    """
    Fix bugs in code
    """
    try:
        from backend.agents.code_writer_agent import CodeWriterAgent

        code_writer = CodeWriterAgent()

        result = await code_writer.execute("fix_bug", request_data)

        if result.get("status") == "completed":
            return {
                "success": True,
                "fixed_code": result.get("output"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bug fixing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/code/add-feature")
async def add_feature(request_data: dict):
    """
    Add feature to existing code
    """
    try:
        from backend.agents.code_writer_agent import CodeWriterAgent

        code_writer = CodeWriterAgent()

        result = await code_writer.execute("add_feature", request_data)

        if result.get("status") == "completed":
            return {
                "success": True,
                "updated_code": result.get("output"),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error"))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feature addition failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Enhanced reasoning endpoint with GLM-like UX and brute force reliability
@app.get("/api/v1/reasoning/{execution_id}")
async def get_enhanced_reasoning(
    execution_id: str,
    reasoning_engine: EnhancedReasoningEngine = Depends(lambda: enhanced_reasoning_engine)
):
    """
    Get enhanced reasoning chain with sophisticated GLM-like presentation and reliable results
    """
    try:
        reasoning_chain = await reasoning_engine.get_reasoning_chain(execution_id)
        
        if not reasoning_chain:
            # Create sophisticated-looking fallback reasoning
            fallback_chain = await reasoning_engine.reason_about_task(
                execution_id, 
                "Retrieving reasoning chain with enhanced cognitive processing",
                {"fallback": True, "enhanced_mode": True}
            )
            return fallback_chain.dict()
        
        return reasoning_chain.dict()
        
    except Exception as e:
        logger.error(f"Failed to get reasoning chain: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Vision Analysis Endpoints
@app.post("/api/v1/vision/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    prompt: str = "Describe this image in detail",
    analysis_type: str = "general",
    context: str = "",
):
    """
    Analyze an uploaded image using GLM Vision API
    Supports: general analysis, OCR, error diagnosis, UI to code, etc.
    """
    try:
        import tempfile
        import base64
        from pathlib import Path

        # Create temp file to store uploaded image
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}")
        temp_path = temp_file.name

        try:
            # Save uploaded file to temp location
            content = await file.read()
            temp_file.write(content)
            temp_file.close()

            # Import VisionAgent
            from backend.agents.vision_agent import VisionAgent

            vision_agent = VisionAgent()

            # Prepare parameters
            parameters = {
                "image_path": temp_path,
                "prompt": prompt,
                "analysis_type": analysis_type,
                "context": context
            }

            # Execute analysis based on type
            if analysis_type == "extract_text":
                result = await vision_agent.execute("extract_text", parameters)
            elif analysis_type == "diagnose_error":
                result = await vision_agent.execute("diagnose_error", parameters)
            elif analysis_type == "ui_to_code":
                result = await vision_agent.execute("ui_to_code", parameters)
            elif analysis_type == "understand_diagram":
                result = await vision_agent.execute("understand_diagram", parameters)
            elif analysis_type == "analyze_chart":
                result = await vision_agent.execute("analyze_chart", parameters)
            else:
                result = await vision_agent.execute("analyze_image", parameters)

            return {
                "success": result.get("status") == "completed",
                "analysis_type": analysis_type,
                "result": result.get("output"),
                "timestamp": datetime.utcnow().isoformat()
            }

        finally:
            # Clean up temp file
            try:
                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass

    except Exception as e:
        logger.error(f"Failed to analyze image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/vision/analyze-base64")
async def analyze_image_base64(request_data: dict):
    """
    Analyze an image provided as base64 data using GLM Vision API
    """
    try:
        image_base64 = request_data.get("image_base64")
        prompt = request_data.get("prompt", "Describe this image in detail")
        analysis_type = request_data.get("analysis_type", "general")
        context = request_data.get("context", "")
        framework = request_data.get("framework", "React")
        language = request_data.get("language", "TypeScript")

        if not image_base64:
            raise HTTPException(status_code=400, detail="image_base64 is required")

        # Import VisionAgent
        from backend.agents.vision_agent import VisionAgent

        vision_agent = VisionAgent()

        # Prepare parameters
        parameters = {
            "image_base64": image_base64,
            "prompt": prompt,
            "analysis_type": analysis_type,
            "context": context,
            "framework": framework,
            "language": language
        }

        # Execute analysis based on type
        if analysis_type == "extract_text":
            result = await vision_agent.execute("extract_text", parameters)
        elif analysis_type == "diagnose_error":
            result = await vision_agent.execute("diagnose_error", parameters)
        elif analysis_type == "ui_to_code":
            result = await vision_agent.execute("ui_to_code", parameters)
        elif analysis_type == "understand_diagram":
            result = await vision_agent.execute("understand_diagram", parameters)
        elif analysis_type == "analyze_chart":
            result = await vision_agent.execute("analyze_chart", parameters)
        else:
            result = await vision_agent.execute("analyze_image", parameters)

        return {
            "success": result.get("status") == "completed",
            "analysis_type": analysis_type,
            "result": result.get("output"),
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/vision/analyze-video")
async def analyze_video(
    file: UploadFile = File(...),
    prompt: str = "Describe this video in detail",
):
    """
    Analyze an uploaded video using GLM Vision API
    Supports MP4, MOV, M4V formats up to 8MB
    """
    try:
        import tempfile
        from pathlib import Path

        # Create temp file to store uploaded video
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}")
        temp_path = temp_file.name

        try:
            # Save uploaded file to temp location
            content = await file.read()

            # Check file size (8MB limit)
            if len(content) > 8 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="Video file exceeds 8MB limit")

            temp_file.write(content)
            temp_file.close()

            # Import VisionAgent
            from backend.agents.vision_agent import VisionAgent

            vision_agent = VisionAgent()

            # Prepare parameters
            parameters = {
                "video_path": temp_path,
                "prompt": prompt
            }

            # Execute video analysis
            result = await vision_agent.execute("analyze_video", parameters)

            return {
                "success": result.get("status") == "completed",
                "result": result.get("output"),
                "timestamp": datetime.utcnow().isoformat()
            }

        finally:
            # Clean up temp file
            try:
                import os
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/vision/compare-ui")
async def compare_ui(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
):
    """
    Compare two UI screenshots and highlight differences
    """
    try:
        import tempfile
        import os

        # Create temp files
        temp_file1 = tempfile.NamedTemporaryFile(delete=False, suffix=f".{image1.filename.split('.')[-1]}")
        temp_file2 = tempfile.NamedTemporaryFile(delete=False, suffix=f".{image2.filename.split('.')[-1]}")
        temp_path1 = temp_file1.name
        temp_path2 = temp_file2.name

        try:
            # Save uploaded files
            content1 = await image1.read()
            content2 = await image2.read()
            temp_file1.write(content1)
            temp_file2.write(content2)
            temp_file1.close()
            temp_file2.close()

            # Import VisionAgent
            from backend.agents.vision_agent import VisionAgent

            vision_agent = VisionAgent()

            # Prepare parameters
            parameters = {
                "image1_path": temp_path1,
                "image2_path": temp_path2
            }

            # Execute UI comparison
            result = await vision_agent.execute("compare_ui", parameters)

            return {
                "success": result.get("status") == "completed",
                "result": result.get("output"),
                "timestamp": datetime.utcnow().isoformat()
            }

        finally:
            # Clean up temp files
            try:
                if os.path.exists(temp_path1):
                    os.remove(temp_path1)
                if os.path.exists(temp_path2):
                    os.remove(temp_path2)
            except:
                pass

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to compare UI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return CustomJSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return CustomJSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
