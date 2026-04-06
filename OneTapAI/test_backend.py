"""
ZIEL-MAS Backend Testing Script
Tests all API endpoints to verify backend functionality
"""

import asyncio
import httpx
import json
from typing import Optional, Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_001"

# Colors for output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_success(message: str):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def print_header(message: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

class BackendTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = None
        self.test_data = {}

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()

    async def test_health_check(self) -> bool:
        """Test health check endpoint"""
        print_info("Testing health check endpoint...")

        try:
            response = await self.client.get(f"{self.base_url}/health")

            if response.status_code == 200:
                data = response.json()
                print_success(f"Health check passed - Status: {data.get('status', 'unknown')}")

                # Check services
                services = data.get('services', {})
                redis_status = services.get('redis', 'unknown')
                db_status = services.get('database', 'unknown')

                print(f"  - Redis: {redis_status}")
                print(f"  - Database: {db_status}")

                return True
            else:
                print_error(f"Health check failed with status {response.status_code}")
                return False

        except Exception as e:
            print_error(f"Health check failed with error: {str(e)}")
            return False

    async def test_create_task(self, intent: str, priority: str = "medium") -> Optional[Dict[str, Any]]:
        """Test task creation endpoint"""
        print_info(f"Creating task with intent: '{intent}'...")

        try:
            payload = {
                "intent": intent,
                "priority": priority,
                "user_id": TEST_USER_ID
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/create-task",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                print_success(f"Task created successfully")
                print(f"  - Execution ID: {data.get('execution_id')}")
                print(f"  - Execution Link: {data.get('execution_link')}")
                print(f"  - Task Count: {data.get('task_count')}")

                # Save for later tests
                self.test_data['execution_id'] = data.get('execution_id')
                self.test_data['execution_link'] = data.get('execution_link')

                return data
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                print_error(f"Task creation failed: {error_detail}")
                return None

        except Exception as e:
            print_error(f"Task creation failed with error: {str(e)}")
            return None

    async def test_get_task_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Test task status endpoint"""
        print_info(f"Getting status for execution: {execution_id}...")

        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/status/{execution_id}"
            )

            if response.status_code == 200:
                data = response.json()
                print_success(f"Status retrieved successfully")
                print(f"  - Status: {data.get('status')}")
                print(f"  - Progress: {data.get('progress', 0)*100:.1f}%")
                print(f"  - Completed Tasks: {data.get('completed_tasks')}/{data.get('total_tasks')}")

                return data
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                print_error(f"Status retrieval failed: {error_detail}")
                return None

        except Exception as e:
            print_error(f"Status retrieval failed with error: {str(e)}")
            return None

    async def test_execute_task(self, token: str) -> bool:
        """Test task execution endpoint"""
        print_info(f"Executing task with token: {token[:20]}...")

        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/execute/{token}"
            )

            if response.status_code == 200:
                data = response.json()
                print_success(f"Task execution started")
                print(f"  - Message: {data.get('message')}")
                print(f"  - Monitor Link: {data.get('monitor_link')}")
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                print_error(f"Task execution failed: {error_detail}")
                return False

        except Exception as e:
            print_error(f"Task execution failed with error: {str(e)}")
            return False

    async def test_get_user_tasks(self) -> bool:
        """Test user tasks endpoint"""
        print_info(f"Getting tasks for user: {TEST_USER_ID}...")

        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/user/{TEST_USER_ID}/tasks"
            )

            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {data.get('count', 0)} tasks")

                tasks = data.get('tasks', [])
                if tasks:
                    print(f"  Recent tasks:")
                    for i, task in enumerate(tasks[:3], 1):
                        print(f"    {i}. {task.get('intent', 'No intent')} - {task.get('status', 'unknown')}")

                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                print_error(f"User tasks retrieval failed: {error_detail}")
                return False

        except Exception as e:
            print_error(f"User tasks retrieval failed with error: {str(e)}")
            return False

    async def test_get_statistics(self) -> bool:
        """Test statistics endpoint"""
        print_info("Getting system statistics...")

        try:
            response = await self.client.get(f"{self.base_url}/api/v1/stats")

            if response.status_code == 200:
                data = response.json()
                print_success("Statistics retrieved successfully")

                db_stats = data.get('database', {})
                if db_stats:
                    print(f"  - Total Tasks: {db_stats.get('total_tasks', 0)}")
                    print(f"  - Completed: {db_stats.get('completed_tasks', 0)}")
                    print(f"  - Failed: {db_stats.get('failed_tasks', 0)}")
                    print(f"  - Success Rate: {db_stats.get('success_rate', 0)*100:.1f}%")

                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                print_error(f"Statistics retrieval failed: {error_detail}")
                return False

        except Exception as e:
            print_error(f"Statistics retrieval failed with error: {str(e)}")
            return False

    async def test_get_task_logs(self, execution_id: str) -> bool:
        """Test task logs endpoint"""
        print_info(f"Getting logs for execution: {execution_id}...")

        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/logs/{execution_id}?limit=10"
            )

            if response.status_code == 200:
                data = response.json()
                log_count = data.get('count', 0)
                print_success(f"Retrieved {log_count} log entries")

                logs = data.get('logs', [])
                if logs:
                    print(f"  Recent logs:")
                    for log in logs[:3]:
                        print(f"    - [{log.get('level')}] {log.get('message')}")

                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                print_error(f"Logs retrieval failed: {error_detail}")
                return False

        except Exception as e:
            print_error(f"Logs retrieval failed with error: {str(e)}")
            return False

    async def test_cancel_task(self, execution_id: str) -> bool:
        """Test task cancellation endpoint"""
        print_info(f"Cancelling task: {execution_id}...")

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/cancel/{execution_id}"
            )

            if response.status_code == 200:
                data = response.json()
                print_success(f"Task cancelled successfully")
                print(f"  - Message: {data.get('message')}")
                return True
            else:
                error_detail = response.json().get('detail', 'Unknown error')
                print_error(f"Task cancellation failed: {error_detail}")
                return False

        except Exception as e:
            print_error(f"Task cancellation failed with error: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all backend tests"""
        print_header("ZIEL-MAS Backend Testing Suite")
        print(f"Testing backend at: {self.base_url}")
        print(f"Test User ID: {TEST_USER_ID}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        results = []

        # Test 1: Health Check
        print_header("Test 1: Health Check")
        result = await self.test_health_check()
        results.append(("Health Check", result))

        if not result:
            print_warning("Backend health check failed. Skipping remaining tests.")
            return

        # Test 2: Get Statistics
        print_header("Test 2: System Statistics")
        result = await self.test_get_statistics()
        results.append(("Statistics", result))

        # Test 3: Create Task
        print_header("Test 3: Task Creation")
        task_data = await self.test_create_task("Send a test email to john@example.com")
        results.append(("Create Task", task_data is not None))

        if not task_data:
            print_warning("Task creation failed. Skipping related tests.")
        else:
            execution_id = task_data.get('execution_id')

            # Test 4: Get Task Status
            print_header("Test 4: Task Status")
            result = await self.test_get_task_status(execution_id)
            results.append(("Get Task Status", result is not None))

            # Test 5: Get Task Logs
            print_header("Test 5: Task Logs")
            result = await self.test_get_task_logs(execution_id)
            results.append(("Get Task Logs", result))

            # Test 6: Execute Task (if token available)
            execution_link = task_data.get('execution_link', '')
            if execution_link:
                token = execution_link.split('/')[-1]
                print_header("Test 6: Task Execution")
                result = await self.test_execute_task(token)
                results.append(("Execute Task", result))

            # Test 7: Cancel Task
            print_header("Test 7: Task Cancellation")
            result = await self.test_cancel_task(execution_id)
            results.append(("Cancel Task", result))

        # Test 8: Get User Tasks
        print_header("Test 8: User Tasks")
        result = await self.test_get_user_tasks()
        results.append(("Get User Tasks", result))

        # Print Summary
        print_header("Test Summary")
        passed = sum(1 for _, result in results if result)
        total = len(results)

        for test_name, result in results:
            status = f"{Colors.GREEN}PASSED{Colors.RESET}" if result else f"{Colors.RED}FAILED{Colors.RESET}"
            print(f"{test_name:<30} {status}")

        print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")

        if passed == total:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed. Check backend logs.{Colors.RESET}")

async def main():
    """Main test runner"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        ZIEL-MAS Backend Automated Testing Suite           ║")
    print("║                                                            ║")
    print("║  This script tests all backend API endpoints              ║")
    print("║  Make sure the backend is running before testing          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")

    async with BackendTester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {str(e)}{Colors.RESET}")
