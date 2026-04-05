# ZIEL-MAS Backend Test Suite

Comprehensive, rigorous testing suite for the ZIEL-MAS backend system.

## Overview

This test suite provides thorough coverage of all backend components including:
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end API testing
- **Security Tests**: Vulnerability and penetration testing
- **Performance Tests**: Load, stress, and optimization testing

## Test Structure

```
backend/tests/
├── conftest.py                      # Test fixtures and configuration
├── test_models.py                   # Pydantic model tests
├── test_services.py                 # Database, cache, and security service tests
├── test_agents.py                   # Agent implementation tests
├── test_core.py                     # Controller and execution engine tests
├── test_api_integration.py          # API endpoint integration tests
├── test_security.py                 # Security and vulnerability tests
├── test_performance.py              # Performance and load tests
└── README.md                        # This file
```

## Test Categories

### 1. Unit Tests (`test_models.py`, `test_services.py`, `test_agents.py`, `test_core.py`)

**Purpose**: Test individual components in isolation

**Coverage**:
- Pydantic model validation and serialization
- Database operations (CRUD)
- Redis cache operations
- Security service functions
- Agent execution logic
- Controller agent planning
- Execution engine workflow

**Example**:
```bash
python run_tests.py --unit
```

### 2. Integration Tests (`test_api_integration.py`)

**Purpose**: Test complete workflows and API endpoints

**Coverage**:
- Health check endpoint
- Task creation workflow
- Task execution via token
- Status monitoring
- Task cancellation
- Log retrieval
- User task listing
- Statistics endpoint
- CORS headers
- Error handling

**Example**:
```bash
python run_tests.py --integration
```

### 3. Security Tests (`test_security.py`)

**Purpose**: Identify and prevent security vulnerabilities

**Coverage**:
- SQL injection prevention
- XSS (Cross-Site Scripting) prevention
- Command injection prevention
- Path traversal prevention
- LDAP injection prevention
- XML injection prevention
- Header injection prevention
- Input validation
- Authentication/authorization
- Data encryption
- Password security
- Rate limiting
- Session management

**Example**:
```bash
python run_tests.py --security
```

### 4. Performance Tests (`test_performance.py`)

**Purpose**: Ensure system performance and scalability

**Coverage**:
- Database bulk operations
- Redis performance
- Concurrent operations
- Agent response times
- Execution engine throughput
- Load testing
- Memory leak detection
- Scalability testing
- Caching effectiveness

**Example**:
```bash
python run_tests.py --performance
```

## Prerequisites

### Required Packages

```bash
pip install pytest pytest-asyncio pytest-cov httpx mongomock
```

### Environment Setup

1. **MongoDB** (optional, will use mongomock if not available):
```bash
# macOS
brew install mongodb-community
brew services start mongodb-community

# Linux
sudo apt-get install mongodb
sudo systemctl start mongodb

# Or use Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

2. **Redis** (optional, will use mock if not available):
```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt-get install redis-server
sudo systemctl start redis

# Or use Docker
docker run -d -p 6379:6379 --name redis redis:latest
```

3. **Environment Variables** (optional):
```bash
export TEST_MONGODB_URI="mongodb://localhost:27017/test_ziel_mas"
export TEST_REDIS_URI="redis://localhost:6379/1"
export TEST_GLM_API_KEY="your-test-api-key"
```

## Running Tests

### Using the Test Runner (Recommended)

```bash
# Run all tests
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --security
python run_tests.py --performance

# Run with coverage report
python run_tests.py --coverage

# Run specific test file
python run_tests.py --file test_models.py

# Run with verbose output
python run_tests.py --all --verbose

# Run quick smoke tests
python run_tests.py --quick
```

### Using pytest Directly

```bash
# Run all tests
pytest backend/tests/ -v

# Run specific test file
pytest backend/tests/test_models.py -v

# Run specific test
pytest backend/tests/test_models.py::TestTaskStatus::test_task_status_values -v

# Run with coverage
pytest backend/tests/ --cov=backend --cov-report=html

# Run only marked tests
pytest backend/tests/ -m "not slow" -v
```

## Test Fixtures

The `conftest.py` file provides shared fixtures:

- `mock_database`: In-memory MongoDB mock
- `mock_redis`: Mock Redis client
- `database_service`: Database service with mock backend
- `redis_service`: Redis service with mock backend
- `security_service`: Security service for testing
- `controller_agent`: Controller agent instance
- `execution_engine`: Execution engine instance
- `sample_task_execution`: Sample task execution for testing
- `sample_task_graph`: Sample task graph for testing
- `test_user_data`: Sample user data
- `test_task_requests`: Sample task requests
- `malicious_intents`: Malicious intent examples for security testing

## Understanding Test Results

### Test Output Format

```
backend/tests/test_models.py::TestTaskStatus::test_task_status_values PASSED
backend/tests/test_models.py::TestTaskNode::test_task_node_creation_with_defaults PASSED
backend/tests/test_services.py::TestDatabaseService::test_create_task_execution PASSED

========================= 150 passed in 5.23s =========================
```

### Coverage Report

When running with `--coverage`:

```
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
backend/models/task.py        120      5    96%   23-27
backend/services/database.py  200     10    95%   45-50
backend/core/controller.py    150      8    95%   78-82
---------------------------------------------------------
TOTAL                         800     50    94%
```

## Writing New Tests

### Test Structure

```python
import pytest
from backend.models.task import TaskNode, AgentType

class TestMyFeature:
    """Test description"""

    @pytest.mark.asyncio
    async def test_my_functionality(self, sample_fixture):
        """Test specific functionality"""
        # Arrange
        input_data = {"test": "data"}

        # Act
        result = await my_function(input_data)

        # Assert
        assert result is not None
        assert result.status == "success"
```

### Best Practices

1. **Use descriptive test names**: `test_create_task_with_valid_inputs`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Test edge cases**: Empty inputs, null values, boundary conditions
4. **Test error conditions**: Invalid inputs, network failures, timeouts
5. **Use fixtures**: Share common test data via fixtures
6. **Keep tests independent**: Each test should run in isolation
7. **Mock external dependencies**: Don't rely on external services
8. **Use async/await**: For async operations, use `@pytest.mark.asyncio`

### Test Categories

```python
@pytest.mark.unit  # Unit test
@pytest.mark.integration  # Integration test
@pytest.mark.security  # Security test
@pytest.mark.performance  # Performance test
@pytest.mark.slow  # Slow-running test
async def test_my_test(self):
    pass
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mongodb:
        image: mongo:latest
        ports:
          - 27017:27017
      redis:
        image: redis:latest
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        run: python run_tests.py --all --verbose

      - name: Generate coverage
        run: python run_tests.py --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Troubleshooting

### Common Issues

**1. Tests fail with connection errors**
```bash
# Solution: Tests use mocks by default, but if you want real services:
export TEST_MONGODB_URI="mongodb://localhost:27017/test"
export TEST_REDIS_URI="redis://localhost:6379/1"
```

**2. Async tests hang**
```bash
# Solution: Ensure pytest-asyncio is installed
pip install pytest-asyncio
```

**3. Import errors**
```bash
# Solution: Run tests from project root
cd /path/to/project
python run_tests.py --all
```

**4. MongoDB/Redis not available**
```bash
# Solution: Tests will use mocks automatically, no action needed
# But if you want real services:
docker-compose up -d mongodb redis
```

## Test Metrics

### Coverage Goals

- **Unit Tests**: >90% coverage
- **Integration Tests**: >80% coverage
- **Security Tests**: 100% of critical paths
- **Performance Tests**: All key operations

### Performance Benchmarks

- **Database Operations**: <100ms per operation
- **Redis Operations**: <10ms per operation
- **API Response Time**: <500ms for 95% of requests
- **Task Execution**: <5s for simple tasks
- **Concurrent Load**: Support 100+ concurrent users

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain >90% code coverage
4. Add security tests for user inputs
5. Add performance tests for critical paths
6. Update this README with new test categories

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Pydantic Testing Guide](https://docs.pydantic.dev/latest/concepts/testing/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)

## License

This test suite is part of the ZIEL-MAS project and follows the same license.
