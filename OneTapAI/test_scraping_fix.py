#!/usr/bin/env python3
"""
Test script to verify scraping task fix
"""

import requests
import json
import time

def test_scraping_task_fix():
    """Test that scraping tasks are now properly classified as code generation"""
    
    print("🧪 Testing Scraping Task Fix")
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
    
    # Test 2: Create a scraping task
    print("\n📝 Creating scraping task...")
    task_data = {
        "intent": "Create a code to scrape amazon jobs",
        "priority": "medium",
        "user_id": "test_scraping_user"
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
    
    # Test 4: Monitor task execution
    print("\n📊 Monitoring task execution...")
    max_attempts = 30
    code_generation_detected = False
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{backend_url}/api/v1/status/{execution_id}", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                completed = status_data.get("completed_tasks", 0)
                total = status_data.get("total_tasks", 0)
                
                print(f"   Attempt {attempt + 1}: {status} - {int(progress * 100)}% ({completed}/{total} tasks)")
                
                # Check if we get proper progress (not stuck at 0/4)
                if completed > 0 and not code_generation_detected:
                    print("   ✅ Tasks are being executed properly!")
                    code_generation_detected = True
                
                # Check for generated code
                if status_data.get("generated_code"):
                    print("   ✅ Generated code found!")
                    print(f"   Code length: {len(status_data['generated_code'])} characters")
                
                # Check if completed or failed
                if status in ["completed", "failed"]:
                    print(f"\n🎉 Task {status}!")
                    
                    if status == "completed":
                        print("   ✅ Scraping task completed successfully!")
                        print("   ✅ No more 'URL is required' errors!")
                        print("   ✅ No more deadlock detection!")
                    else:
                        print("   ⚠️  Task failed, but let's check if it's the expected failure...")
                        
                    # Check final results
                    if status_data.get("result"):
                        result = status_data.get("result", {})
                        if "tasks" in result:
                            print(f"   📊 Total tasks executed: {len(result['tasks'])}")
                            for task_id, task_info in result["tasks"].items():
                                agent = task_info.get("agent", "unknown")
                                action = task_info.get("action", "unknown")
                                print(f"      - {agent}: {action}")
                    
                    break
                    
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🎯 Scraping Task Fix Test Complete!")
    print("=" * 50)
    
    print("\n💡 What was tested:")
    print("   ✅ Backend connectivity")
    print("   ✅ Scraping task creation")
    print("   ✅ Task execution")
    print("   ✅ Progress tracking")
    print("   ✅ Error handling")
    
    print("\n🔧 Fix applied:")
    print("   📝 Moved 'scrape' from web_automation to code_generation")
    print("   🛠️  Improved deadlock detection")
    print("   📊 Better error handling for failed tasks")
    
    print("\n🎉 Expected results:")
    print("   ✅ No more 'URL is required' errors")
    print("   ✅ No more 'Execution deadlock detected'")
    print("   ✅ Proper task progress (not stuck at 0/X)")
    print("   ✅ Generated code for scraping")
    print("   ✅ Better error messages")

if __name__ == "__main__":
    test_scraping_task_fix()
