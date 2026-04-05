# ZIEL-MAS API Testing Guide

## Overview
This guide provides instructions for testing all ZIEL-MAS API endpoints using the comprehensive test script.

## Prerequisites
- Python 3.7+
- MongoDB running on localhost:27017
- Redis running on localhost:6379
- All required dependencies installed (`pip install -r requirements.txt`)

## Quick Start

### 1. Start the Server
```bash
# Activate virtual environment
source venv312/bin/activate

# Start the server
python -m backend.main
```

The server should start on `http://localhost:8000`

### 2. Run the Test Suite
In a separate terminal:

```bash
# Activate virtual environment
source venv312/bin/activate

# Run all tests
python test.py
```

## Test Coverage

The test script covers the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check endpoint |
| `/docs` | GET | API documentation (Swagger UI) |
| `/api/v1/create-task` | POST | Create a new task from intent |
| `/api/v1/execute/{token}` | GET | Execute a task via secure token |
| `/api/v1/status/{execution_id}` | GET | Get task execution status |
| `/api/v1/cancel/{execution_id}` | POST | Cancel a running task |
| `/api/v1/logs/{execution_id}` | GET | Get task execution logs |
| `/api/v1/user/{user_id}/tasks` | GET | Get all tasks for a user |
| `/api/v1/stats` | GET | Get system statistics |

## Sample Test Output

```
🚀 Starting ZIEL-MAS API Tests
Target URL: http://localhost:8000
Timestamp: 2026-04-05T00:45:00.000000

============================================================
Testing: Health Check
============================================================

Health Check Response:
Status Code: 200
Response Body:
{
  "status": "healthy",
  "timestamp": "2026-04-05T00:45:00.123456",
  "services": {
    "redis": "connected",
    "database": "connected"
  }
}

... (other test outputs) ...

============================================================
TEST RESULTS SUMMARY
============================================================
Health Check        : ✅ PASS
Api Documentation   : ✅ PASS
Create Task         : ✅ PASS
Execute Task        : ✅ PASS
Task Status         : ✅ PASS
Task Logs           : ✅ PASS
Cancel Task         : ✅ PASS
User Tasks          : ✅ PASS
Statistics          : ✅ PASS

Total Tests: 9
Passed: 9
Failed: 0
Success Rate: 100.0%

🎉 All tests passed!
```

## Manual Testing

If you want to test endpoints manually, here are some sample curl commands:

### Health Check
```bash
curl -X GET "http://localhost:8000/health" -H "Content-Type: application/json"
```

### Create Task
```bash
curl -X POST "http://localhost:8000/api/v1/create-task" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "Create a web scraper for e-commerce prices",
    "priority": "medium",
    "user_id": "test_user_123"
  }'
```

### Get Task Status
```bash
curl -X GET "http://localhost:8000/api/v1/status/{execution_id}" \
  -H "Content-Type: application/json"
```

### Get Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/stats" \
  -H "Content-Type: application/json"
```

## Troubleshooting

### Server Not Running
```
❌ Server is not running or not accessible!
Please start the server with: python -m backend.main
```
**Solution**: Make sure the server is running on port 8000 before running tests.

### MongoDB Connection Failed
```
Failed to connect to MongoDB: [Errno 61] Connection refused
```
**Solution**: Start MongoDB service:
```bash
# macOS with Homebrew
brew services start mongodb-community

# Or use Docker
docker run -d -p 27017:27017 mongo
```

### Redis Connection Failed
```
Failed to connect to Redis: [Errno 61] Connection refused
```
**Solution**: Start Redis service:
```bash
# macOS with Homebrew
brew services start redis

# Or use Docker
docker run -d -p 6379:6379 redis
```

### Port Already in Use
```
ERROR: [Errno 48] error while attempting to bind on address ('0.0.0.0', 8000): address already in use
```
**Solution**: Kill the process using port 8000:
```bash
# Find process
lsof -i :8000

# Kill process (replace PID with actual process ID)
kill -9 <PID>
```

## Custom Tests

You can modify the `test.py` script to add custom test cases:

1. **Modify Test Data**: Update the `task_data` in `test_create_task()` method
2. **Add New Tests**: Add new test methods following the existing pattern
3. **Change Base URL**: Modify the `BASE_URL` constant at the top of the file

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These provide detailed endpoint documentation and allow you to test endpoints directly from your browser.
