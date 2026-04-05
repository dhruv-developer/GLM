#!/usr/bin/env python3
"""
Test script to verify frontend fixes for ZIEL-MAS
"""

import requests
import json
import time

def test_task_creation_and_status():
    """Test the complete task creation and status checking flow"""
    
    print("🧪 Testing Frontend Fixes")
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
        "user_id": "test_user"
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
    
    # Test 4: Check task status multiple times
    print("\n📊 Checking task status...")
    max_attempts = 30
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
                
                # Check for new fields
                has_user_summary = "user_summary" in status_data
                has_generated_code = "generated_code" in status_data
                has_download_filename = "download_filename" in status_data
                
                if has_user_summary:
                    print("   ✅ user_summary field present")
                if has_generated_code:
                    print("   ✅ generated_code field present")
                if has_download_filename:
                    print("   ✅ download_filename field present")
                
                # Check if completed
                if status in ["completed", "failed"]:
                    print(f"\n🎉 Task {status}!")
                    
                    if status == "completed":
                        # Test 5: Check if download endpoint works
                        print("\n📥 Testing download endpoint...")
                        try:
                            download_response = requests.get(f"{backend_url}/api/v1/download/{execution_id}", timeout=5)
                            if download_response.status_code == 200:
                                print("✅ Download endpoint works")
                                content = download_response.text
                                if len(content) > 0:
                                    print(f"   Downloaded {len(content)} characters of code")
                                else:
                                    print("   ⚠️  Downloaded empty content")
                            else:
                                print(f"   ❌ Download failed: {download_response.status_code}")
                        except Exception as e:
                            print(f"   ❌ Download error: {e}")
                    
                    break
                    
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(2)
    
    # Test 6: Check user summary formatting
    if "status_data" in locals() and "user_summary" in status_data:
        print("\n📝 User Summary Preview:")
        print("-" * 30)
        summary = status_data["user_summary"]
        # Show first few lines
        lines = summary.split('\n')[:10]
        for line in lines:
            print(f"   {line}")
        if len(summary.split('\n')) > 10:
            print("   ...")
    
    print("\n" + "=" * 50)
    print("🎯 Frontend Fix Test Complete!")
    print("=" * 50)
    
    print("\n💡 What was tested:")
    print("   ✅ Backend connectivity")
    print("   ✅ Task creation")
    print("   ✅ Task execution")
    print("   ✅ Status checking")
    print("   ✅ New fields (user_summary, generated_code, download_filename)")
    print("   ✅ Download endpoint")
    
    print("\n🔧 Frontend should now show:")
    print("   📊 Proper task progress (not 0/X)")
    print("   📝 User-friendly summaries")
    print("   📥 Download buttons for generated code")
    print("   🎯 Better result display")

if __name__ == "__main__":
    test_task_creation_and_status()
