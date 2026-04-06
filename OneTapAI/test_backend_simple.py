"""
ZIEL-MAS Backend Simple Testing Script
Synchronous version for quick testing
"""

import requests
import json
import time
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_001"

# Colors
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_success(msg): print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")
def print_error(msg): print(f"{Colors.RED}✗ {msg}{Colors.RESET}")
def print_info(msg): print(f"{Colors.BLUE}ℹ {msg}{Colors.RESET}")
def print_warning(msg): print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")

def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

class BackendTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_data = {}

    def test_health(self):
        """Test health check endpoint"""
        print_info("Testing health check...")

        try:
            response = self.session.get(f"{self.base_url}/health")

            if response.status_code == 200:
                data = response.json()
                print_success(f"Backend is healthy - Status: {data.get('status')}")
                return True
            else:
                print_error(f"Health check failed: {response.status_code}")
                return False

        except Exception as e:
            print_error(f"Connection failed: {str(e)}")
            return False

    def test_create_task(self, intent, priority="medium"):
        """Test task creation"""
        print_info(f"Creating task: '{intent}'")

        try:
            payload = {
                "intent": intent,
                "priority": priority,
                "user_id": TEST_USER_ID
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/create-task",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                print_success("Task created")
                print(f"  - Execution ID: {data.get('execution_id')}")
                print(f"  - Link: {data.get('execution_link')}")
                print(f"  - Tasks: {data.get('task_count')}")

                self.test_data['execution_id'] = data.get('execution_id')
                self.test_data['execution_link'] = data.get('execution_link')

                return data
            else:
                error = response.json().get('detail', 'Unknown error')
                print_error(f"Failed: {error}")
                return None

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None

    def test_get_status(self, execution_id):
        """Test getting task status"""
        print_info(f"Getting status for: {execution_id}")

        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/status/{execution_id}"
            )

            if response.status_code == 200:
                data = response.json()
                print_success("Status retrieved")
                print(f"  - Status: {data.get('status')}")
                print(f"  - Progress: {data.get('progress', 0)*100:.0f}%")
                print(f"  - Tasks: {data.get('completed_tasks')}/{data.get('total_tasks')}")
                return data
            else:
                error = response.json().get('detail', 'Unknown error')
                print_error(f"Failed: {error}")
                return None

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return None

    def test_execute_task(self, token):
        """Test task execution"""
        print_info(f"Executing task with token: {token[:20]}...")

        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/execute/{token}"
            )

            if response.status_code == 200:
                data = response.json()
                print_success("Task execution started")
                print(f"  - Message: {data.get('message')}")
                return True
            else:
                error = response.json().get('detail', 'Unknown error')
                print_error(f"Failed: {error}")
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_get_user_tasks(self):
        """Test getting user tasks"""
        print_info(f"Getting tasks for user: {TEST_USER_ID}")

        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/user/{TEST_USER_ID}/tasks"
            )

            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {data.get('count', 0)} tasks")
                return True
            else:
                error = response.json().get('detail', 'Unknown error')
                print_error(f"Failed: {error}")
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_get_stats(self):
        """Test getting statistics"""
        print_info("Getting system statistics...")

        try:
            response = self.session.get(f"{self.base_url}/api/v1/stats")

            if response.status_code == 200:
                data = response.json()
                print_success("Statistics retrieved")

                db_stats = data.get('database', {})
                if db_stats:
                    print(f"  - Total Tasks: {db_stats.get('total_tasks', 0)}")
                    print(f"  - Completed: {db_stats.get('completed_tasks', 0)}")
                    print(f"  - Success Rate: {db_stats.get('success_rate', 0)*100:.1f}%")

                return True
            else:
                error = response.json().get('detail', 'Unknown error')
                print_error(f"Failed: {error}")
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_get_logs(self, execution_id):
        """Test getting task logs"""
        print_info(f"Getting logs for: {execution_id}")

        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/logs/{execution_id}?limit=5"
            )

            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {data.get('count', 0)} logs")
                return True
            else:
                error = response.json().get('detail', 'Unknown error')
                print_error(f"Failed: {error}")
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_cancel_task(self, execution_id):
        """Test cancelling a task"""
        print_info(f"Cancelling task: {execution_id}")

        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/cancel/{execution_id}"
            )

            if response.status_code == 200:
                data = response.json()
                print_success("Task cancelled")
                return True
            else:
                error = response.json().get('detail', 'Unknown error')
                print_error(f"Failed: {error}")
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        print_header("ZIEL-MAS Backend Testing Suite")
        print(f"Backend URL: {self.base_url}")
        print(f"User ID: {TEST_USER_ID}\n")

        results = []

        # Test 1: Health Check
        print_header("Test 1: Health Check")
        result = self.test_health()
        results.append(("Health Check", result))

        if not result:
            print_warning("Backend not responding. Exiting.")
            return

        # Test 2: Statistics
        print_header("Test 2: Statistics")
        result = self.test_get_stats()
        results.append(("Statistics", result))

        # Test 3: Create Task
        print_header("Test 3: Create Task")
        task = self.test_create_task("Test: Send hello world email")
        results.append(("Create Task", task is not None))

        if task:
            exec_id = task.get('execution_id')

            # Test 4: Get Status
            print_header("Test 4: Get Status")
            result = self.test_get_status(exec_id)
            results.append(("Get Status", result is not None))

            # Test 5: Get Logs
            print_header("Test 5: Get Logs")
            result = self.test_get_logs(exec_id)
            results.append(("Get Logs", result))

            # Test 6: Execute Task
            link = task.get('execution_link', '')
            if link:
                token = link.split('/')[-1]
                print_header("Test 6: Execute Task")
                result = self.test_execute_task(token)
                results.append(("Execute Task", result))

            # Test 7: Cancel Task
            print_header("Test 7: Cancel Task")
            result = self.test_cancel_task(exec_id)
            results.append(("Cancel Task", result))

        # Test 8: User Tasks
        print_header("Test 8: Get User Tasks")
        result = self.test_get_user_tasks()
        results.append(("User Tasks", result))

        # Summary
        print_header("Summary")
        passed = sum(1 for _, r in results if r)
        total = len(results)

        for name, result in results:
            status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
            print(f"{name:<30} {status}")

        print(f"\n{Colors.BOLD}Results: {passed}/{total} passed{Colors.RESET}")

        if passed == total:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All tests passed!{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}⚠ Some tests failed{Colors.RESET}")

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           ZIEL-MAS Backend Test Suite                    ║")
    print("║           Simple Synchronous Version                      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")

    tester = BackendTester()
    tester.run_all_tests()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted{Colors.RESET}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Error: {str(e)}{Colors.RESET}")
