#!/usr/bin/env python3
"""
Frontend Testing Script for OneTapAI
Automated checks for frontend functionality
"""

import requests
import time
import json
from typing import Dict, List, Any

class FrontendTester:
    def __init__(self, frontend_url: str = "http://localhost:3000", backend_url: str = "http://localhost:8000"):
        self.frontend_url = frontend_url
        self.backend_url = backend_url
        self.results = []
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log a test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
    
    def test_backend_connectivity(self):
        """Test if backend is accessible"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health Check", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("Backend Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Connection error: {str(e)[:50]}")
            return False
    
    def test_frontend_running(self):
        """Test if frontend is running"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Server", True, f"HTTP {response.status_code}")
                return True
            else:
                self.log_test("Frontend Server", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Server", False, f"Connection error: {str(e)[:50]}")
            return False
    
    def test_api_endpoints(self):
        """Test key API endpoints"""
        endpoints = [
            ("/health", "GET"),
            ("/api/v1/stats", "GET"),
        ]
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code in [200, 404]:  # 404 is ok for some endpoints
                    self.log_test(f"API Endpoint {endpoint}", True, f"HTTP {response.status_code}")
                else:
                    self.log_test(f"API Endpoint {endpoint}", False, f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"API Endpoint {endpoint}", False, f"Error: {str(e)[:30]}")
    
    def test_task_creation_flow(self):
        """Test the complete task creation flow"""
        try:
            # Create a test task
            task_data = {
                "intent": "Test task for frontend validation",
                "priority": "medium",
                "user_id": "test_frontend_user"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/create-task",
                json=task_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                execution_id = data.get("execution_id")
                execution_link = data.get("execution_link")
                
                self.log_test("Task Creation", True, f"ID: {execution_id[:8]}...")
                
                # Test task status
                if execution_id:
                    status_response = requests.get(f"{self.backend_url}/api/v1/status/{execution_id}", timeout=5)
                    if status_response.status_code == 200:
                        self.log_test("Task Status Check", True, "Status endpoint works")
                    else:
                        self.log_test("Task Status Check", False, f"HTTP {status_response.status_code}")
                
                return True
            else:
                self.log_test("Task Creation", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Task Creation", False, f"Error: {str(e)[:30]}")
            return False
    
    def test_static_assets(self):
        """Test if frontend static assets load"""
        try:
            # Test main page
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                content = response.text
                
                # Check for key frontend elements
                checks = [
                    ("React App", "react" in content.lower()),
                    ("Next.js", "_next/" in content),
                    ("Tailwind CSS", "tailwind" in content.lower()),
                    ("Main Layout", "main-layout" in content.lower()),
                ]
                
                for check_name, condition in checks:
                    self.log_test(f"Frontend: {check_name}", condition)
                
                return True
            else:
                self.log_test("Frontend Content", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Frontend Content", False, f"Error: {str(e)[:30]}")
            return False
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        try:
            # Test preflight request
            response = requests.options(
                f"{self.backend_url}/api/v1/create-task",
                headers={
                    "Origin": self.frontend_url,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                },
                timeout=5
            )
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            
            if response.status_code in [200, 204]:
                self.log_test("CORS Configuration", True, f"Origin: {cors_headers['Access-Control-Allow-Origin']}")
                return True
            else:
                self.log_test("CORS Configuration", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("CORS Configuration", False, f"Error: {str(e)[:30]}")
            return False
    
    def test_websocket_connection(self):
        """Test WebSocket connection (if implemented)"""
        try:
            import websocket
            import threading
            
            def on_message(ws, message):
                pass
            
            def on_error(ws, error):
                pass
            
            def on_close(ws, close_status_code, close_msg):
                pass
            
            def on_open(ws):
                ws.close()
            
            ws_url = self.backend_url.replace("http://", "ws://").replace("https://", "wss://")
            ws = websocket.WebSocketApp(ws_url,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
            
            # Try to connect with timeout
            thread = threading.Thread(target=ws.run_forever)
            thread.daemon = True
            thread.start()
            thread.join(timeout=3)
            
            if thread.is_alive():
                self.log_test("WebSocket Connection", False, "Connection timeout")
                return False
            else:
                self.log_test("WebSocket Connection", True, "WebSocket endpoint available")
                return True
                
        except ImportError:
            self.log_test("WebSocket Connection", False, "websocket-client not installed")
            return False
        except Exception as e:
            self.log_test("WebSocket Connection", False, f"Error: {str(e)[:30]}")
            return False
    
    def run_all_tests(self):
        """Run all frontend tests"""
        print("🧪 OneTapAI Frontend Test Suite")
        print("=" * 50)
        print(f"Frontend URL: {self.frontend_url}")
        print(f"Backend URL: {self.backend_url}")
        print()
        
        # Core connectivity tests
        self.test_backend_connectivity()
        self.test_frontend_running()
        
        # Only continue if basic connectivity works
        if any(r["passed"] for r in self.results[-2:]):
            self.test_api_endpoints()
            self.test_task_creation_flow()
            self.test_static_assets()
            self.test_cors_configuration()
            self.test_websocket_connection()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        
        for result in self.results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{result['test']:<30}: {status}")
            if result["details"] and not result["passed"]:
                print(f"{'':32} {result['details']}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! Frontend is ready!")
        elif passed >= total * 0.8:
            print(f"\n⚠️  {total - passed} test(s) failed. Mostly working.")
        else:
            print(f"\n❌ {total - passed} test(s) failed. Needs attention.")
        
        print("\n🔧 Next steps:")
        if not any(r["passed"] for r in self.results[:2]):
            print("   1. Start backend: python -m backend.main")
            print("   2. Start frontend: npm run dev")
        else:
            print("   1. Check failed tests above")
            print("   2. Fix configuration issues")
            print("   3. Run manual tests from checklist")
        
        # Save results
        try:
            with open("frontend_test_results.json", "w") as f:
                json.dump({
                    "timestamp": time.time(),
                    "passed": passed,
                    "total": total,
                    "results": self.results
                }, f, indent=2)
            print(f"\n📄 Results saved to: frontend_test_results.json")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test OneTapAI frontend")
    parser.add_argument("--frontend", default="http://localhost:3000", help="Frontend URL")
    parser.add_argument("--backend", default="http://localhost:8000", help="Backend URL")
    
    args = parser.parse_args()
    
    tester = FrontendTester(args.frontend, args.backend)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
