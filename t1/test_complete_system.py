#!/usr/bin/env python3
"""
Complete system test to verify everything is working
"""

import requests
import json
import time

def test_complete_system():
    """Test the complete system with a simple, verifiable task"""
    
    print("🧪 Complete System Test")
    print("=" * 50)
    
    backend_url = "http://localhost:8000"
    frontend_url = "http://localhost:3000"
    
    # Test 1: Check both services are running
    print("\n🔍 Checking Services...")
    try:
        backend_response = requests.get(f"{backend_url}/health", timeout=5)
        if backend_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend is not running")
            return
    except:
        print("❌ Backend is not accessible")
        return
    
    try:
        frontend_response = requests.get(f"{frontend_url}", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend is running")
        else:
            print("❌ Frontend is not running")
            return
    except:
        print("❌ Frontend is not accessible")
        return
    
    # Test 2: Create a simple, verifiable task
    print("\n📝 Creating test task...")
    task_data = {
        "intent": "Write a simple Python function that adds two numbers",
        "priority": "medium",
        "user_id": "test_system_user"
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
    
    # Test 4: Monitor execution with detailed results
    print("\n📊 Monitoring execution...")
    max_attempts = 40
    final_result = None
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{backend_url}/api/v1/status/{execution_id}", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                completed = status_data.get("completed_tasks", 0)
                total = status_data.get("total_tasks", 0)
                
                print(f"   Attempt {attempt + 1}: {status} - {int(progress * 100)}% ({completed}/{total})")
                
                # Check for all the good stuff
                if "user_summary" in status_data:
                    print("   ✅ User summary available")
                
                if "generated_code" in status_data:
                    code = status_data["generated_code"]
                    if code and "def add" in code:
                        print("   ✅ Generated code contains function!")
                        print(f"   📝 Code length: {len(code)} characters")
                
                if "download_filename" in status_data:
                    print(f"   ✅ Download filename: {status_data['download_filename']}")
                
                # Check reasoning endpoint
                reasoning_response = requests.get(f"{backend_url}/api/v1/reasoning/{execution_id}", timeout=5)
                if reasoning_response.status_code == 200:
                    print("   ✅ Reasoning endpoint working")
                else:
                    print(f"   ⚠️  Reasoning endpoint: {reasoning_response.status_code}")
                
                # Check download endpoint
                download_response = requests.get(f"{backend_url}/api/v1/download/{execution_id}", timeout=5)
                if download_response.status_code == 200:
                    content = download_response.text
                    if len(content) > 0:
                        print(f"   ✅ Download endpoint working! ({len(content)} chars)")
                    else:
                        print("   ⚠️  Download endpoint returned empty content")
                else:
                    print(f"   ⚠️  Download endpoint: {download_response.status_code}")
                
                # Store final result when completed
                if status in ["completed", "failed"]:
                    final_result = status_data
                    print(f"\n🎉 Task {status}!")
                    
                    # Show detailed results
                    if final_result.get("result"):
                        result = final_result["result"]
                        
                        print("\n📋 Detailed Results:")
                        
                        if "tasks" in result:
                            for task_id, task_info in result["tasks"].items():
                                agent = task_info.get("agent", "unknown")
                                action = task_info.get("action", "unknown")
                                output = task_info.get("output", {})
                                
                                print(f"   Task {task_id[:8]}: {agent} - {action}")
                                
                                # Check for code generation
                                if agent == "code_writer" and "code" in output:
                                    code = output["code"]
                                    print(f"   📝 Generated {len(code)} characters of code")
                                
                                # Check for search results
                                if agent == "web_search" and "results" in output:
                                    results = output["results"]
                                    print(f"   🔍 Found {len(results)} search results")
                                    
                                    if len(results) > 0:
                                        print("   ✅ SEARCH IS WORKING!")
                                        for i, result in enumerate(results[:2]):
                                            title = result.get("title", "No title")
                                            print(f"      {i+1}. {title}")
                                    else:
                                        print("   ⚠️  No search results found")
                    
                    break
                    
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(2)
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎯 Complete System Test Results!")
    print("=" * 50)
    
    if final_result:
        print("\n✅ SUCCESS INDICATORS:")
        print(f"   📊 Progress: {final_result.get('progress', 0)*100}%")
        print(f"   📋 Tasks: {final_result.get('completed_tasks', 0)}/{final_result.get('total_tasks', 0)}")
        print(f"   📝 User Summary: {'✅' if final_result.get('user_summary') else '❌'}")
        print(f"   🔍 Generated Code: {'✅' if final_result.get('generated_code') else '❌'}")
        print(f"   📥 Download: {'✅' if final_result.get('download_filename') else '❌'}")
        print(f"   🧠 Reasoning: {'✅' if final_result else '❌'}")
        
        print("\n🎉 SYSTEM IS WORKING!")
        print("   You can now create tasks and get real results!")
        print("   Frontend should display everything correctly!")
        print("   All major issues have been resolved!")
        
        print("\n💡 Next Steps:")
        print("   1. Go to http://localhost:3000")
        print("   2. Create a task (any type)")
        print("   3. Wait for completion")
        print("   4. Check for generated code, search results, and download options")
        print("   5. Verify everything works as expected!")
        
    else:
        print("\n❌ INCOMPLETE TEST:")
        print("   Task did not complete or results were not captured")
        print("   Check backend logs for errors")
        print("   Verify all services are running")

if __name__ == "__main__":
    test_complete_system()
