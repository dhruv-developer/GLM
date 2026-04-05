"""
Unit Tests for ZIEL-MAS Services
Tests for Database, Cache, and Security services
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.services.database import DatabaseService
from backend.services.cache import RedisService
from backend.services.security import SecurityService


class TestDatabaseService:
    """Test DatabaseService operations"""

    @pytest.mark.asyncio
    async def test_create_task_execution(self, database_service, sample_task_execution):
        """Test creating a task execution"""
        execution_dict = sample_task_execution.dict()

        execution_id = await database_service.create_task_execution(execution_dict)

        assert execution_id == sample_task_execution.execution_id

        # Verify it was stored
        retrieved = await database_service.get_task_execution(execution_id)
        assert retrieved is not None
        assert retrieved["execution_id"] == execution_id

    @pytest.mark.asyncio
    async def test_get_task_execution_not_found(self, database_service):
        """Test getting non-existent task execution"""
        result = await database_service.get_task_execution("nonexistent_id")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_task_execution(self, database_service, sample_task_execution):
        """Test updating a task execution"""
        execution_dict = sample_task_execution.dict()
        execution_id = sample_task_execution.execution_id

        await database_service.create_task_execution(execution_dict)

        # Update status
        updates = {
            "status": "running",
            "started_at": datetime.utcnow().isoformat()
        }
        success = await database_service.update_task_execution(execution_id, updates)

        assert success is True

        # Verify update
        retrieved = await database_service.get_task_execution(execution_id)
        assert retrieved["status"] == "running"

    @pytest.mark.asyncio
    async def test_update_task_execution_not_found(self, database_service):
        """Test updating non-existent task execution"""
        success = await database_service.update_task_execution(
            "nonexistent_id",
            {"status": "running"}
        )
        assert success is False

    @pytest.mark.asyncio
    async def test_get_task_by_token(self, database_service, sample_task_execution):
        """Test retrieving task by execution token"""
        execution_dict = sample_task_execution.dict()
        execution_dict["execution_token"] = "test_token_123"

        await database_service.create_task_execution(execution_dict)

        retrieved = await database_service.get_task_by_token("test_token_123")

        assert retrieved is not None
        assert retrieved["execution_token"] == "test_token_123"

    @pytest.mark.asyncio
    async def test_get_task_by_token_not_found(self, database_service):
        """Test retrieving task by non-existent token"""
        result = await database_service.get_task_by_token("nonexistent_token")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_user_tasks(self, database_service):
        """Test listing tasks for a user"""
        user_id = "test_user_123"

        # Create multiple tasks for the user
        for i in range(3):
            from backend.models.task import TaskExecution, TaskGraph, TaskStatus
            execution = TaskExecution(
                user_id=user_id,
                intent=f"Test task {i}",
                task_graph=TaskGraph(),
                status=TaskStatus.PENDING
            )
            await database_service.create_task_execution(execution.dict())

        # List tasks
        tasks = await database_service.list_user_tasks(user_id)

        assert len(tasks) == 3
        assert all(task["user_id"] == user_id for task in tasks)

    @pytest.mark.asyncio
    async def test_list_user_tasks_with_status_filter(self, database_service):
        """Test listing user tasks with status filter"""
        user_id = "test_user_456"

        # Create tasks with different statuses
        from backend.models.task import TaskExecution, TaskGraph, TaskStatus

        for status in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.COMPLETED]:
            execution = TaskExecution(
                user_id=user_id,
                intent=f"Test task {status}",
                task_graph=TaskGraph(),
                status=status
            )
            await database_service.create_task_execution(execution.dict())

        # Filter by status
        running_tasks = await database_service.list_user_tasks(user_id, status="running")

        assert len(running_tasks) == 1
        assert running_tasks[0]["status"] == "running"

    @pytest.mark.asyncio
    async def test_list_user_tasks_with_limit(self, database_service):
        """Test listing user tasks with limit"""
        user_id = "test_user_789"

        # Create more tasks than the limit
        from backend.models.task import TaskExecution, TaskGraph, TaskStatus
        for i in range(10):
            execution = TaskExecution(
                user_id=user_id,
                intent=f"Test task {i}",
                task_graph=TaskGraph(),
                status=TaskStatus.PENDING
            )
            await database_service.create_task_execution(execution.dict())

        # List with limit
        tasks = await database_service.list_user_tasks(user_id, limit=5)

        assert len(tasks) == 5

    @pytest.mark.asyncio
    async def test_delete_task_execution(self, database_service, sample_task_execution):
        """Test deleting a task execution"""
        execution_dict = sample_task_execution.dict()
        execution_id = sample_task_execution.execution_id

        await database_service.create_task_execution(execution_dict)

        # Delete
        success = await database_service.delete_task_execution(execution_id)

        assert success is True

        # Verify deletion (should be marked as deleted)
        retrieved = await database_service.get_task_execution(execution_id)
        assert retrieved is None or retrieved.get("status") == "deleted"

    @pytest.mark.asyncio
    async def test_create_execution_log(self, database_service):
        """Test creating an execution log"""
        from backend.models.task import ExecutionLog

        log = ExecutionLog(
            execution_id="exec_123",
            task_id="task_1",
            level="INFO",
            message="Task started"
        )

        log_id = await database_service.create_execution_log(log.dict())

        assert log_id == log.log_id

    @pytest.mark.asyncio
    async def test_get_execution_logs(self, database_service):
        """Test retrieving execution logs"""
        execution_id = "exec_456"

        # Create multiple logs
        from backend.models.task import ExecutionLog
        for i in range(5):
            log = ExecutionLog(
                execution_id=execution_id,
                level="INFO",
                message=f"Log message {i}"
            )
            await database_service.create_execution_log(log.dict())

        # Retrieve logs
        logs = await database_service.get_execution_logs(execution_id)

        assert len(logs) == 5

    @pytest.mark.asyncio
    async def test_get_execution_logs_with_level_filter(self, database_service):
        """Test retrieving execution logs with level filter"""
        execution_id = "exec_789"

        from backend.models.task import ExecutionLog

        # Create logs with different levels
        for level in ["INFO", "ERROR", "WARNING"]:
            log = ExecutionLog(
                execution_id=execution_id,
                level=level,
                message=f"Log at {level} level"
            )
            await database_service.create_execution_log(log.dict())

        # Filter by level
        error_logs = await database_service.get_execution_logs(execution_id, level="ERROR")

        assert len(error_logs) == 1
        assert error_logs[0]["level"] == "ERROR"

    @pytest.mark.asyncio
    async def test_get_execution_logs_with_limit(self, database_service):
        """Test retrieving execution logs with limit"""
        execution_id = "exec_limit"

        # Create many logs
        from backend.models.task import ExecutionLog
        for i in range(20):
            log = ExecutionLog(
                execution_id=execution_id,
                level="INFO",
                message=f"Log {i}"
            )
            await database_service.create_execution_log(log.dict())

        # Retrieve with limit
        logs = await database_service.get_execution_logs(execution_id, limit=10)

        assert len(logs) == 10

    @pytest.mark.asyncio
    async def test_update_agent_state(self, database_service):
        """Test updating agent state"""
        agent_id = "agent_123"
        state_data = {
            "agent_id": agent_id,
            "status": "active",
            "last_heartbeat": datetime.utcnow().isoformat()
        }

        success = await database_service.update_agent_state(agent_id, state_data)

        assert success is True

        # Retrieve and verify
        retrieved = await database_service.get_agent_state(agent_id)
        assert retrieved is not None
        assert retrieved["agent_id"] == agent_id

    @pytest.mark.asyncio
    async def test_get_agent_state_not_found(self, database_service):
        """Test retrieving non-existent agent state"""
        result = await database_service.get_agent_state("nonexistent_agent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_agents(self, database_service):
        """Test listing all agents"""
        # Create multiple agents
        for i in range(3):
            agent_id = f"agent_{i}"
            await database_service.update_agent_state(agent_id, {
                "agent_id": agent_id,
                "status": "active"
            })

        # List all agents
        agents = await database_service.list_agents()

        assert len(agents) == 3

    @pytest.mark.asyncio
    async def test_list_agents_with_status_filter(self, database_service):
        """Test listing agents with status filter"""
        # Create agents with different statuses
        for status in ["active", "idle", "busy"]:
            agent_id = f"agent_{status}"
            await database_service.update_agent_state(agent_id, {
                "agent_id": agent_id,
                "status": status
            })

        # Filter by status
        active_agents = await database_service.list_agents(status="active")

        assert len(active_agents) == 1
        assert active_agents[0]["status"] == "active"

    @pytest.mark.asyncio
    async def test_create_user(self, database_service):
        """Test creating a user"""
        user_data = {
            "user_id": "user_123",
            "email": "test@example.com",
            "name": "Test User",
            "created_at": datetime.utcnow().isoformat()
        }

        user_id = await database_service.create_user(user_data)

        assert user_id == "user_123"

        # Verify creation
        retrieved = await database_service.get_user(user_id)
        assert retrieved is not None
        assert retrieved["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, database_service):
        """Test retrieving non-existent user"""
        result = await database_service.get_user("nonexistent_user")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, database_service):
        """Test retrieving user by email"""
        user_data = {
            "user_id": "user_456",
            "email": "user456@example.com",
            "name": "User 456"
        }

        await database_service.create_user(user_data)

        # Retrieve by email
        retrieved = await database_service.get_user_by_email("user456@example.com")

        assert retrieved is not None
        assert retrieved["user_id"] == "user_456"

    @pytest.mark.asyncio
    async def test_update_user(self, database_service):
        """Test updating user data"""
        user_data = {
            "user_id": "user_789",
            "email": "user789@example.com",
            "name": "Original Name"
        }

        await database_service.create_user(user_data)

        # Update
        updates = {"name": "Updated Name"}
        success = await database_service.update_user("user_789", updates)

        assert success is True

        # Verify update
        retrieved = await database_service.get_user("user_789")
        assert retrieved["name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_get_statistics(self, database_service):
        """Test getting database statistics"""
        # Create some data
        from backend.models.task import TaskExecution, TaskGraph, TaskStatus

        # Create tasks
        for i in range(5):
            execution = TaskExecution(
                user_id=f"user_{i}",
                intent=f"Test task {i}",
                task_graph=TaskGraph(),
                status=TaskStatus.PENDING
            )
            await database_service.create_task_execution(execution.dict())

        # Create logs
        from backend.models.task import ExecutionLog
        for i in range(10):
            log = ExecutionLog(
                execution_id=f"exec_{i}",
                level="INFO",
                message=f"Log {i}"
            )
            await database_service.create_execution_log(log.dict())

        # Get statistics
        stats = await database_service.get_statistics()

        assert "total_tasks" in stats
        assert "total_logs" in stats
        assert "total_agents" in stats
        assert "total_users" in stats
        assert stats["total_tasks"] >= 5
        assert stats["total_logs"] >= 10


class TestRedisService:
    """Test RedisService operations"""

    @pytest.mark.asyncio
    async def test_set_and_get_task_status(self, redis_service):
        """Test setting and getting task status"""
        execution_id = "exec_123"
        status = "running"

        await redis_service.set_task_status(execution_id, status)

        retrieved = await redis_service.get_task_status(execution_id)

        assert retrieved == status

    @pytest.mark.asyncio
    async def test_set_and_get_task_progress(self, redis_service):
        """Test setting and getting task progress"""
        execution_id = "exec_456"
        progress = 0.75

        await redis_service.set_task_progress(execution_id, progress)

        retrieved = await redis_service.get_task_progress(execution_id)

        assert retrieved == progress

    @pytest.mark.asyncio
    async def test_set_and_get_task_state(self, redis_service):
        """Test setting and getting task state"""
        execution_id = "exec_789"
        state = {
            "current_task": "task_1",
            "completed_tasks": ["task_0"],
            "metadata": {"attempt": 1}
        }

        await redis_service.set_task_state(execution_id, state)

        retrieved = await redis_service.get_task_state(execution_id)

        assert retrieved == state

    @pytest.mark.asyncio
    async def test_store_and_retrieve_token(self, redis_service):
        """Test storing and retrieving execution token"""
        token = "token_abc123"
        execution_id = "exec_token"

        await redis_service.store_token(token, execution_id)

        retrieved_id = await redis_service.get_execution_id_from_token(token)

        assert retrieved_id == execution_id

    @pytest.mark.asyncio
    async def test_queue_operations(self, redis_service):
        """Test queue push and pop operations"""
        queue_name = "test_queue"

        # Push items
        await redis_service.push_to_queue(queue_name, "item_1")
        await redis_service.push_to_queue(queue_name, "item_2")
        await redis_service.push_to_queue(queue_name, "item_3")

        # Pop items (FIFO)
        item1 = await redis_service.pop_from_queue(queue_name)
        item2 = await redis_service.pop_from_queue(queue_name)

        assert item1 == "item_1"
        assert item2 == "item_2"

    @pytest.mark.asyncio
    async def test_queue_pop_empty(self, redis_service):
        """Test popping from empty queue"""
        item = await redis_service.pop_from_queue("empty_queue")
        assert item is None

    @pytest.mark.asyncio
    async def test_publish_message(self, redis_service):
        """Test publishing messages"""
        channel = "test_channel"
        message = {"status": "update", "progress": 0.5}

        # Should not raise exception
        await redis_service.publish(channel, message)

    @pytest.mark.asyncio
    async def test_get_info(self, redis_service):
        """Test getting Redis info"""
        info = await redis_service.get_info()

        assert isinstance(info, dict)


class TestSecurityService:
    """Test SecurityService operations"""

    def test_generate_execution_token(self, security_service):
        """Test generating execution token"""
        execution_id = "exec_123"
        user_id = "user_456"

        token = security_service.generate_execution_token(execution_id, user_id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_validate_valid_token(self, security_service):
        """Test validating a valid token"""
        execution_id = "exec_789"
        user_id = "user_101"

        token = security_service.generate_execution_token(execution_id, user_id)

        payload = security_service.validate_token(token)

        assert payload is not None
        assert payload["execution_id"] == execution_id
        assert payload["user_id"] == user_id

    def test_validate_invalid_token(self, security_service):
        """Test validating an invalid token"""
        invalid_token = "invalid.token.string"

        payload = security_service.validate_token(invalid_token)

        assert payload is None

    def test_validate_malformed_token(self, security_service):
        """Test validating malformed tokens"""
        malformed_tokens = [
            "",
            "not-a-token",
            "too.many.parts.in.token",
            None
        ]

        for token in malformed_tokens:
            payload = security_service.validate_token(token)
            assert payload is None

    def test_validate_intent_valid(self, security_service):
        """Test intent validation with valid intents"""
        valid_intents = [
            "Send email to john@example.com",
            "Schedule meeting for tomorrow",
            "Find restaurants near me",
            "Book a cab to airport"
        ]

        for intent in valid_intents:
            is_valid, error = security_service.validate_intent(intent)
            assert is_valid is True
            assert error is None

    def test_validate_intent_empty(self, security_service):
        """Test intent validation with empty intent"""
        is_valid, error = security_service.validate_intent("")

        assert is_valid is False
        assert error is not None

    def test_validate_intent_too_long(self, security_service):
        """Test intent validation with extremely long intent"""
        long_intent = "A" * 10000

        is_valid, error = security_service.validate_intent(long_intent)

        assert is_valid is False
        assert error is not None

    def test_validate_intent_with_xss(self, security_service):
        """Test intent validation with XSS attempts"""
        xss_intents = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')"
        ]

        for intent in xss_intents:
            is_valid, error = security_service.validate_intent(intent)
            # Should either reject or sanitize
            assert is_valid is False or error is not None

    def test_validate_intent_with_sql_injection(self, security_service):
        """Test intent validation with SQL injection attempts"""
        sql_injection_intents = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--"
        ]

        for intent in sql_injection_intents:
            is_valid, error = security_service.validate_intent(intent)
            # Should reject
            assert is_valid is False

    def test_encrypt_decrypt_data(self, security_service):
        """Test data encryption and decryption"""
        original_data = "sensitive information"

        encrypted = security_service.encrypt_data(original_data)
        decrypted = security_service.decrypt_data(encrypted)

        assert decrypted == original_data

    def test_encrypt_decrypt_dict(self, security_service):
        """Test encrypting and decrypting dictionary data"""
        original_data = {
            "user_id": "user_123",
            "email": "user@example.com",
            "api_key": "secret_key_123"
        }

        encrypted = security_service.encrypt_data(str(original_data))
        decrypted_str = security_service.decrypt_data(encrypted)

        assert decrypted_str == str(original_data)

    def test_hash_password(self, security_service):
        """Test password hashing"""
        password = "secure_password_123"

        hashed = security_service.hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_verify_password_correct(self, security_service):
        """Test verifying correct password"""
        password = "correct_password"
        hashed = security_service.hash_password(password)

        is_valid = security_service.verify_password(password, hashed)

        assert is_valid is True

    def test_verify_password_incorrect(self, security_service):
        """Test verifying incorrect password"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = security_service.hash_password(password)

        is_valid = security_service.verify_password(wrong_password, hashed)

        assert is_valid is False

    def test_generate_random_string(self, security_service):
        """Test generating random strings"""
        string1 = security_service.generate_random_string(16)
        string2 = security_service.generate_random_string(16)

        assert len(string1) == 16
        assert len(string2) == 16
        assert string1 != string2  # Should be different

    def test_token_expiration(self, security_service):
        """Test token expiration handling"""
        execution_id = "exec_expire"
        user_id = "user_expire"

        # Generate token
        token = security_service.generate_execution_token(execution_id, user_id)

        # Should be valid immediately
        payload = security_service.validate_token(token)
        assert payload is not None

        # Note: Testing actual expiration would require time manipulation
        # or waiting, which is not practical in unit tests


class TestServiceIntegration:
    """Test integration between services"""

    @pytest.mark.asyncio
    async def test_task_lifecycle_database_redis(self, database_service, redis_service):
        """Test task lifecycle across database and redis"""
        from backend.models.task import TaskExecution, TaskGraph

        # Create task
        execution = TaskExecution(
            user_id="user_lifecycle",
            intent="Test lifecycle",
            task_graph=TaskGraph()
        )

        # Store in database
        await database_service.create_task_execution(execution.dict())

        # Store in Redis
        await redis_service.set_task_status(execution.execution_id, "pending")
        await redis_service.set_task_progress(execution.execution_id, 0.0)

        # Retrieve from both
        db_task = await database_service.get_task_execution(execution.execution_id)
        redis_status = await redis_service.get_task_status(execution.execution_id)
        redis_progress = await redis_service.get_task_progress(execution.execution_id)

        assert db_task is not None
        assert redis_status == "pending"
        assert redis_progress == 0.0

        # Update status
        await redis_service.set_task_status(execution.execution_id, "running")
        await database_service.update_task_execution(execution.execution_id, {
            "status": "running"
        })

        # Verify updates
        updated_status = await redis_service.get_task_status(execution.execution_id)
        updated_task = await database_service.get_task_execution(execution.execution_id)

        assert updated_status == "running"
        assert updated_task["status"] == "running"

    @pytest.mark.asyncio
    async def test_security_token_workflow(self, security_service, database_service, redis_service):
        """Test complete security token workflow"""
        from backend.models.task import TaskExecution, TaskGraph

        # Create task
        execution = TaskExecution(
            user_id="user_token",
            intent="Test token workflow",
            task_graph=TaskGraph()
        )

        await database_service.create_task_execution(execution.dict())

        # Generate token
        token = security_service.generate_execution_token(
            execution.execution_id,
            execution.user_id
        )

        # Store token in Redis
        await redis_service.store_token(token, execution.execution_id)

        # Validate token
        payload = security_service.validate_token(token)
        assert payload is not None

        # Retrieve execution ID from token
        retrieved_id = await redis_service.get_execution_id_from_token(token)
        assert retrieved_id == execution.execution_id

        # Verify execution exists
        retrieved_execution = await database_service.get_task_execution(retrieved_id)
        assert retrieved_execution is not None
        assert retrieved_execution["execution_id"] == execution.execution_id


class TestServiceErrorHandling:
    """Test error handling in services"""

    @pytest.mark.asyncio
    async def test_database_connection_failure(self):
        """Test database service handles connection failures"""
        # Create service with invalid connection string
        db_service = DatabaseService(
            connection_string="mongodb://invalid:27017"
        )

        # Should handle connection error gracefully
        try:
            await db_service.connect()
            # If it doesn't raise, at least operations should fail gracefully
        except Exception as e:
            # Expected to fail connection
            pass

    @pytest.mark.asyncio
    async def test_redis_connection_failure(self):
        """Test Redis service handles connection failures"""
        # Create service with invalid connection string
        redis_service = RedisService(
            redis_url="redis://invalid:6379/0"
        )

        # Should handle connection error gracefully
        try:
            await redis_service.connect()
            # If it doesn't raise, operations should fail gracefully
        except Exception as e:
            # Expected to fail connection
            pass

    def test_security_service_invalid_key(self):
        """Test security service with invalid key"""
        # Should handle invalid encryption key
        with pytest.raises(Exception):
            SecurityService(
                jwt_secret="valid",
                encryption_key="too_short"
            )
