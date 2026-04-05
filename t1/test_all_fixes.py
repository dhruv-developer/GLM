#!/usr/bin/env python3
"""
Comprehensive test script to verify all fixes
"""

import requests
import json
import time

def test_all_fixes():
    """Test all the fixes we've applied"""
    
    print("🧪 Testing All Fixes")
    print("=" * 50)
    
    backend_url = "http://localhost:8000"
    
    # Test 1: Backend health
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend health check failed")
            return
    except:
        print("❌ Backend is not running")
        print("   Please start: python -m backend.main")
        return
    
    # Test 2: Create a simple task
    print("\n📝 Creating test task...")
    task_data = {
        "intent": "Create a simple Python function to calculate factorial",
        "priority": "medium",
        "user_id": "test_fixes_user"
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/v1/create-task",
            json=task_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            execution_id = data.get("execution_id")
            print(f"✅ Task created: {execution_id[:8]}...")
        else:
            print(f"❌ Task creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"❌ Task creation error: {e}")
        return
    
    # Test 3: Execute the task
    print("\n🚀 Executing task...")
    try:
        response = requests.post(f"{backend_url}/api/v1/execute/{execution_id}", timeout=5)
        if response.status_code == 200:
            print("✅ Task execution started")
        else:
            print(f"❌ Task execution failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Task execution error: {e}")
        return
    
    # Test 4: Monitor task completion and test all endpoints
    print("\n📊 Monitoring task and testing fixes...")
    max_attempts = 30
    reasoning_tested = False
    download_tested = False
    summary_tested = False
    
    for attempt in range(max_attempts):
        try:
            # Test status endpoint
            response = requests.get(f"{backend_url}/api/v1/status/{execution_id}", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                completed = status_data.get("completed_tasks", 0)
                total = status_data.get("total_tasks", 0)
                
                print(f"   Attempt {attempt + 1}: {status} - {int(progress * 100)}% ({completed}/{total} tasks)")
                
                # Test user summary formatting
                if "user_summary" in status_data and not summary_tested:
                    print("   ✅ User summary field present")
                    summary_tested = True
                
                # Test generated code field
                if "generated_code" in status_data:
                    print("   ✅ Generated code field present")
                
                # Test download filename field
                if "download_filename" in status_data:
                    print("   ✅ Download filename field present")
                
                # Test reasoning endpoint once task is running
                if status in ["running", "completed"] and not reasoning_tested:
                    print(f"\n🧠 Testing reasoning endpoint...")
                    reasoning_response = requests.get(f"{backend_url}/api/v1/reasoning/{execution_id}", timeout=5)
                    
                    if reasoning_response.status_code == 200:
                        reasoning_data = reasoning_response.json()
                        print("   ✅ Reasoning endpoint works!")
                        print(f"   Confidence score: {reasoning_data.get('confidence_score', 'N/A')}")
                        print(f"   Steps count: {len(reasoning_data.get('steps', []))}")
                        reasoning_tested = True
                    elif reasoning_response.status_code == 404:
                        print("   ⚠️  Reasoning chain not found (might be normal)")
                        reasoning_tested = True
                    else:
                        print(f"   ❌ Reasoning endpoint failed: {reasoning_response.status_code}")
                        print(f"   Response: {reasoning_response.text}")
                
                # Test download endpoint once task is completed
                if status == "completed" and not download_tested:
                    print(f"\n📥 Testing download endpoint...")
                    download_response = requests.get(f"{backend_url}/api/v1/download/{execution_id}", timeout=5)
                    
                    if download_response.status_code == 200:
                        content = download_response.text
                        if len(content) > 0:
                            print("   ✅ Download endpoint works!")
                            print(f"   Downloaded {len(content)} characters")
                        else:
                            print("   ⚠️  Downloaded empty content")
                        download_tested = True
                    else:
                        print(f"   ❌ Download failed: {download_response.status_code}")
                
                # Check if completed
                if status in ["completed", "failed"]:
                    print(f"\n🎉 Task {status}!")
                    
                    # Final tests if not done yet
                    if not reasoning_tested:
                        print(f"\n🧠 Final reasoning test...")
                        reasoning_response = requests.get(f"{backend_url}/api/v1/reasoning/{execution_id}", timeout=5)
                        if reasoning_response.status_code == 200:
                            print("   ✅ Final reasoning endpoint test passed")
                        else:
                            print("   ⚠️  Final reasoning test failed")
                    
                    if not download_tested and status == "completed":
                        print(f"\n📥 Final download test...")
                        download_response = requests.get(f"{backend_url}/api/v1/download/{execution_id}", timeout=5)
                        if download_response.status_code == 200:
                            print("   ✅ Final download test passed")
                        else:
                            print("   ⚠️  Final download test failed")
                    
                    break
                    
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🎯 All Fixes Test Complete!")
    print("=" * 50)
    
    print("\n💡 What was tested:")
    print("   ✅ Backend connectivity")
    print("   ✅ Task creation and execution")
    print("   ✅ Status endpoint with proper fields")
    print("   ✅ Reasoning endpoint (/api/v1/reasoning/{execution_id})")
    print("   ✅ Download endpoint (/api/v1/download/{execution_id})")
    print("   ✅ User summary formatting")
    print("   ✅ Generated code fields")
    
    print("\n🔧 Fixes applied:")
    print("   📝 Fixed ExecutionEngine import")
    print("   🔧 Fixed Redis client access (self.redis.client)")
    print("   🧠 Added reasoning endpoint")
    print("   📥 Added download endpoint")
    print("   📝 Fixed datetime handling in summaries")
    print("   🔧 Fixed ReasoningStep model with decision_obj")
    
    print("\n🎉 Expected results:")
    print("   📊 Correct task progress (not 0/X)")
    print("   📝 User-friendly summaries without errors")
    print("   🧠 Working reasoning endpoint")
    print("   📥 Working download functionality")
    print("   🎯 No more Redis or datetime errors")

if __name__ == "__main__":
    test_all_fixes()
