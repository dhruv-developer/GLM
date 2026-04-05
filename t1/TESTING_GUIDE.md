# ZIEL-MAS Backend Testing Guide

This guide explains how to test the ZIEL-MAS backend using the provided test scripts.

## Test Files

We provide three different testing approaches:

### 1. **test_backend.py** - Async Testing Suite (Recommended)
Full-featured async testing with detailed output and color-coded results.

**Features:**
- Comprehensive endpoint testing
- Detailed error messages
- Color-coded output
- Test data preservation between tests
- Complete workflow testing

**Requirements:**
- Python 3.7+
- httpx (`pip install httpx`)

**Usage:**
```bash
python test_backend.py
```

### 2. **test_backend_simple.py** - Simple Synchronous Testing
Easier to understand synchronous version for quick testing.

**Features:**
- Simple synchronous code
- Same test coverage as async version
- Easier to debug
- No async/await complexity

**Requirements:**
- Python 3.6+
- requests (`pip install requests`)

**Usage:**
```bash
python test_backend_simple.py
```

### 3. **backend/test_api.py** - Pytest Unit Tests
Professional pytest-based testing suite for CI/CD integration.

**Features:**
- Pytest framework integration
- Unit and integration tests
- Fixture-based setup
- Easy to extend
- CI/CD ready

**Requirements:**
- Python 3.7+
- pytest (`pip install pytest pytest-asyncio`)
- httpx (`pip install httpx`)

**Usage:**
```bash
cd backend
pytest test_api.py -v
```

Or run all tests:
```bash
pytest test_api.py -v -s
```

## Quick Start

### Option 1: Run Async Tests (Recommended)
```bash
# Install dependencies
pip install httpx

# Start backend (in another terminal)
cd backend
python -m uvicorn api.main:app --reload

# Run tests
python test_backend.py
```

### Option 2: Run Simple Tests
```bash
# Install dependencies
pip install requests

# Start backend (in another terminal)
cd backend
python -m uvicorn api.main:app --reload

# Run tests
python test_backend_simple.py
```

### Option 3: Run Pytest
```bash
# Install dependencies
pip install pytest pytest-asyncio httpx

# Start backend (in another terminal)
cd backend
python -m uvicorn api.main:app --reload

# Run tests
cd backend
pytest test_api.py -v -s
```

## Test Coverage

All test scripts cover the following endpoints:

### Health & Status
- ✅ `GET /health` - Health check endpoint
- ✅ `GET /api/v1/stats` - System statistics

### Task Management
- ✅ `POST /api/v1/create-task` - Create new task
- ✅ `GET /api/v1/status/{id}` - Get task status
- ✅ `POST /api/v1/cancel/{id}` - Cancel task

### Task Execution
- ✅ `GET /api/v1/execute/{token}` - Execute task via token

### Data Retrieval
- ✅ `GET /api/v1/user/{id}/tasks` - Get user tasks
- ✅ `GET /api/v1/logs/{id}` - Get execution logs

## Understanding Test Results

### Success Example
```
✓ Health check passed - Status: healthy
  - Redis: connected
  - Database: connected
✓ Task created successfully
  - Execution ID: exec_507f1f77bcf86cd799439011
  - Execution Link: /execute/token_abc123...
  - Task Count: 3
```

### Failure Example
```
✗ Task creation failed: Invalid GLM API key
✗ Status retrieval failed: Task execution not found
```

## Test Workflow

### Complete Test Sequence

1. **Health Check** - Verify backend is running
2. **Statistics** - Get system statistics
3. **Create Task** - Create a test task
4. **Get Status** - Check task status
5. **Get Logs** - Retrieve task logs
6. **Execute Task** - Execute via token
7. **Cancel Task** - Cancel the task
8. **User Tasks** - List user's tasks

## Troubleshooting

### "Connection refused" Error
**Problem:** Cannot connect to backend

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend if not running
cd backend
python -m uvicorn api.main:app --reload
```

### "Task creation failed" Error
**Problem:** GLM API key not configured

**Solution:**
```bash
# Add GLM API key to backend/.env
cd backend
echo "GLM_API_KEY=your_actual_api_key_here" >> .env
```

### Import Errors
**Problem:** Missing dependencies

**Solution:**
```bash
# For async tests
pip install httpx

# For simple tests
pip install requests

# For pytest
pip install pytest pytest-asyncio httpx
```

### "MongoDB connection failed" Error
**Problem:** MongoDB not running

**Solution:**
```bash
# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Or run directly
mongod --fork --logpath /tmp/mongodb.log
```

### "Redis connection failed" Error
**Problem:** Redis not running

**Solution:**
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Or run directly
redis-server --daemonize yes
```

## Advanced Usage

### Custom Test Configuration

Edit the test files to customize:

```python
# In test_backend.py or test_backend_simple.py
BASE_URL = "http://localhost:8000"  # Change backend URL
TEST_USER_ID = "test_user_001"      # Change test user ID
```

### Running Specific Tests

With pytest:
```bash
# Run only health check test
pytest test_api.py::test_health_check -v

# Run only task creation tests
pytest test_api.py::test_create_task -v

# Run only integration tests
pytest test_api.py -k "workflow" -v
```

### Verbose Output

```bash
# Pytest with verbose output
pytest test_api.py -v -s

# See all print statements
pytest test_api.py -v -s --capture=no
```

### Parallel Testing

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest test_api.py -n auto
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test Backend

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mongo:
        image: mongo:latest
        ports:
          - 27017:27017

      redis:
        image: redis:latest
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-asyncio httpx

      - name: Run tests
        run: |
          cd backend
          pytest test_api.py -v
```

## Best Practices

### Before Running Tests
1. ✅ Ensure MongoDB is running
2. ✅ Ensure Redis is running
3. ✅ Configure GLM API key (if testing task creation)
4. ✅ Start backend server
5. ✅ Install required dependencies

### Writing New Tests
1. Use descriptive test names
2. Test both success and failure cases
3. Use fixtures for common setup
4. Keep tests independent
5. Mock external dependencies when possible

### Test Organization
```
backend/
├── test_api.py              # API endpoint tests
├── test_unit.py             # Unit tests (future)
├── test_integration.py      # Integration tests (future)
└── test_e2e.py              # End-to-end tests (future)
```

## Performance Testing

### Load Testing with Locust

```python
from locust import HttpUser, task, between

class ZIELMASUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def health_check(self):
        self.client.get("/health")

    @task(3)
    def get_stats(self):
        self.client.get("/api/v1/stats")
```

Run with:
```bash
locust -f locustfile.py --host=http://localhost:8000
```

## Next Steps

1. **Add More Tests:** Create tests for new features
2. **Test Coverage:** Use `pytest-cov` to measure coverage
3. **Mock External APIs:** Mock GLM API calls
4. **Performance Tests:** Add load testing
5. **E2E Tests:** Create end-to-end test suite

## Support

For issues or questions:
- Check backend logs: `tail -f backend.log`
- Run health check: `curl http://localhost:8000/health`
- Check service status: `./test-connection.sh`

## Test Results Summary

Expected output when all tests pass:
```
╔════════════════════════════════════════════════════════════╗
║                   Test Summary                              ║
╚════════════════════════════════════════════════════════════╝

Health Check                    PASSED
Statistics                      PASSED
Create Task                     PASSED
Get Task Status                 PASSED
Get Task Logs                   PASSED
Execute Task                    PASSED
Cancel Task                     PASSED
Get User Tasks                  PASSED

Results: 8/8 tests passed

🎉 All tests passed!
```
