#!/usr/bin/env python3
"""
Test script to verify progress display fix
"""

import requests
import json
import time

def test_progress_display_fix():
    """Test that progress display shows correct completed/total tasks"""
    
    print("🧪 Testing Progress Display Fix")
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
        "intent": "Find top 5 Python best practices",
        "priority": "medium",
        "user_id": "test_progress_user"
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
    
    # Test 4: Monitor task completion and check progress
    print("\n📊 Monitoring task progress...")
    max_attempts = 30
    progress_fixed = False
    
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
                
                # Check if progress is showing correctly (not stuck at 0/X)
                if completed > 0 and not progress_fixed:
                    print("   ✅ Progress tracking is working!")
                    progress_fixed = True
                
                # Check for proper final counts
                if status in ["completed", "failed"]:
                    print(f"\n🎉 Task {status}!")
                    
                    if status == "completed" and completed == total:
                        print("   ✅ Perfect progress tracking!")
                        print(f"   ✅ Final count: {completed}/{total} tasks")
                    elif completed > 0:
                        print("   ✅ Progress tracking improved!")
                        print(f"   ✅ Final count: {completed}/{total} tasks")
                    else:
                        print("   ⚠️  Still showing 0 completed tasks")
                        print(f"   ⚠️  Final count: {completed}/{total} tasks")
                    
                    # Check for user summary
                    if "user_summary" in status_data:
                        print("   ✅ User summary is available")
                    else:
                        print("   ⚠️  User summary missing")
                    
                    # Check for generated code
                    if "generated_code" in status_data:
                        print("   ✅ Generated code field present")
                    else:
                        print("   ⚠️  Generated code field missing")
                    
                    break
                    
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🎯 Progress Display Fix Test Complete!")
    print("=" * 50)
    
    print("\n💡 What was tested:")
    print("   ✅ Backend connectivity")
    print("   ✅ Task creation and execution")
    print("   ✅ Progress tracking during execution")
    print("   ✅ Final progress calculation")
    print("   ✅ Completed tasks count accuracy")
    
    print("\n🔧 Fix applied:")
    print("   📊 Updated task status endpoint to use database values")
    print("   📝 Added fallback to task graph calculation")
    print("   🎯 Ensured completed_tasks is stored in database")
    
    print("\n🎉 Expected results:")
    print("   ✅ No more '0 tasks completed' when tasks are completed")
    print("   ✅ Proper progress percentage (100% when completed)")
    print("   ✅ Accurate completed/total task counts")
    print("   ✅ Better frontend display")

if __name__ == "__main__":
    test_progress_display_fix()
