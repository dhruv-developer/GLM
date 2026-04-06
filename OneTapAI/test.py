#!/usr/bin/env python3
"""
Comprehensive test script for ZIEL-MAS API endpoints
Tests all available endpoints with sample data
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        
    def print_test_header(self, test_name: str):
        """Print a formatted test header"""
        print(f"\n{'='*60}")
        print(f"Testing: {test_name}")
        print(f"{'='*60}")
        
    def print_response(self, response: requests.Response, test_name: str):
        """Print formatted response information"""
        print(f"\n{test_name} Response:")
        print(f"Status Code: {response.status_code}")
        try:
            data = response.json()
            print(f"Response Body:\n{json.dumps(data, indent=2)}")
        except:
            print(f"Response Body: {response.text}")
    
    def test_health_check(self):
        """Test the health check endpoint"""
        self.print_test_header("Health Check")
        try:
            response = self.session.get(f"{self.base_url}/health")
            self.print_response(response, "Health Check")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_create_task(self):
        """Test task creation endpoint"""
        self.print_test_header("Create Task")
        
        # Sample task creation data
        task_data = {
            "intent": "Create a simple web scraper to extract product prices from an e-commerce website",
            "priority": "medium",
            "user_id": "test_user_123"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/v1/create-task", json=task_data)
            self.print_response(response, "Create Task")
            
            if response.status_code == 200:
                data = response.json()
                return data.get("execution_id"), data.get("execution_link")
            return None, None
        except Exception as e:
            print(f"Error: {e}")
            return None, None
    
    def test_execute_task(self, execution_link: Optional[str] = None):
        """Test task execution endpoint"""
        self.print_test_header("Execute Task")
        
        if not execution_link:
            print("No execution link provided, skipping execute task test")
            return None
            
        try:
            # Extract token from execution link or use full link
            if execution_link.startswith("/execute/"):
                token = execution_link.split("/")[-1]
                url = f"{self.base_url}/api/v1/execute/{token}"
            else:
                url = f"{self.base_url}{execution_link}"
            
            response = self.session.get(url)
            self.print_response(response, "Execute Task")
            
            if response.status_code == 200:
                data = response.json()
                return data.get("execution_id")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def test_task_status(self, execution_id: str):
        """Test task status endpoint"""
        self.print_test_header("Task Status")
        
        if not execution_id:
            print("No execution_id provided, skipping status test")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/api/v1/status/{execution_id}")
            self.print_response(response, "Task Status")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_cancel_task(self, execution_id: str):
        """Test task cancellation endpoint"""
        self.print_test_header("Cancel Task")
        
        if not execution_id:
            print("No execution_id provided, skipping cancel test")
            return False
            
        try:
            response = self.session.post(f"{self.base_url}/api/v1/cancel/{execution_id}")
            self.print_response(response, "Cancel Task")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_get_task_logs(self, execution_id: str):
        """Test get task logs endpoint"""
        self.print_test_header("Get Task Logs")
        
        if not execution_id:
            print("No execution_id provided, skipping logs test")
            return False
            
        try:
            response = self.session.get(f"{self.base_url}/api/v1/logs/{execution_id}")
            self.print_response(response, "Get Task Logs")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_get_user_tasks(self):
        """Test get user tasks endpoint"""
        self.print_test_header("Get User Tasks")
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/user/test_user_123/tasks")
            self.print_response(response, "Get User Tasks")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_get_statistics(self):
        """Test statistics endpoint"""
        self.print_test_header("Get Statistics")
        
        try:
            response = self.session.get(f"{self.base_url}/api/v1/stats")
            self.print_response(response, "Get Statistics")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_docs_endpoint(self):
        """Test API documentation endpoint"""
        self.print_test_header("API Documentation")
        
        try:
            response = self.session.get(f"{self.base_url}/docs")
            print(f"Docs Response Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ API Documentation is accessible")
                return True
            else:
                print("❌ API Documentation not accessible")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all API tests in sequence"""
        print(f"🚀 Starting ZIEL-MAS API Tests")
        print(f"Target URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        results = {}
        
        # Test 1: Health Check
        results['health'] = self.test_health_check()
        time.sleep(1)
        
        # Test 2: API Documentation
        results['docs'] = self.test_docs_endpoint()
        time.sleep(1)
        
        # Test 3: Create Task
        execution_id, execution_link = self.test_create_task()
        results['create_task'] = execution_id is not None
        time.sleep(2)
        
        # Test 4: Execute Task (if we have an execution link)
        if execution_link:
            exec_id = self.test_execute_task(execution_link)
            if exec_id:
                execution_id = exec_id
            results['execute_task'] = exec_id is not None
            time.sleep(3)
        else:
            results['execute_task'] = False
        
        # Test 5: Task Status (if we have an execution_id)
        if execution_id:
            results['task_status'] = self.test_task_status(execution_id)
            time.sleep(1)
            
            # Test 6: Get Task Logs
            results['task_logs'] = self.test_get_task_logs(execution_id)
            time.sleep(1)
            
            # Test 7: Cancel Task
            results['cancel_task'] = self.test_cancel_task(execution_id)
            time.sleep(1)
        else:
            results['task_status'] = False
            results['task_logs'] = False
            results['cancel_task'] = False
        
        # Test 8: Get User Tasks
        results['user_tasks'] = self.test_get_user_tasks()
        time.sleep(1)
        
        # Test 9: Get Statistics
        results['statistics'] = self.test_get_statistics()
        time.sleep(1)
        
        # Print summary
        self.print_test_summary(results)
        
        return results
    
    def print_test_summary(self, results: Dict[str, bool]):
        """Print test results summary"""
        print(f"\n{'='*60}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*60}")
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():<20}: {status}")
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed!")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")


def main():
    """Main function to run the tests"""
    print("ZIEL-MAS API Test Suite")
    print("========================")
    print("Make sure the server is running on http://localhost:8000")
    print("Press Ctrl+C to interrupt tests\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ Server is accessible")
    except requests.exceptions.RequestException:
        print("❌ Server is not running or not accessible!")
        print("Please start the server with: python -m backend.main")
        return
    
    # Create tester and run tests
    tester = APITester()
    
    try:
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        exit_code = 0 if all(results.values()) else 1
        exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        exit(1)


if __name__ == "__main__":
    main()
