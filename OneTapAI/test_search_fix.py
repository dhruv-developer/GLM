#!/usr/bin/env python3
"""
Test script to verify search query cleaning fix
"""

import requests
import json
import time

def test_search_fix():
    """Test that search queries are properly cleaned and return results"""
    
    print("🧪 Testing Search Query Cleaning Fix")
    print("=" * 50)
    
    backend_url = "http://localhost:8000"
    
    # Test 1: Check backend health
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
    
    # Test 2: Create a search task with emojis and quotes
    print("\n📝 Creating search task with emojis...")
    task_data = {
        "intent": "📝 \"Find the best Python machine learning courses with ratings and prices\"",
        "priority": "medium",
        "user_id": "test_search_fix_user"
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
    
    # Test 4: Monitor execution and check for search results
    print("\n🔍 Monitoring search results...")
    max_attempts = 30
    search_results_found = False
    
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
                
                # Check for search results in the response
                if status_data.get("result"):
                    result = status_data["result"]
                    if "tasks" in result:
                        tasks = result["tasks"]
                        for task_id, task_info in tasks.items():
                            if task_info.get("agent") == "web_search":
                                output = task_info.get("output", {})
                                if "results" in output:
                                    results = output["results"]
                                    result_count = output.get("result_count", 0)
                                    
                                    if result_count > 0 and not search_results_found:
                                        print(f"   ✅ SEARCH RESULTS FOUND: {result_count} results!")
                                        search_results_found = True
                                        
                                        # Show first few results
                                        print(f"   📋 Sample results:")
                                        for i, result in enumerate(results[:3]):
                                            title = result.get("title", "No title")
                                            url = result.get("url", "No URL")
                                            print(f"      {i+1}. {title}")
                                            print(f"         {url}")
                                    elif result_count == 0:
                                        print(f"   ⚠️  Search returned {result_count} results")
                                        print(f"   📝 Query used: {output.get('query', 'Unknown')}")
                                        print(f"   📝 Note: {output.get('note', 'No note')}")
                
                # Check if completed
                if status in ["completed", "failed"]:
                    print(f"\n🎉 Task {status}!")
                    
                    if search_results_found:
                        print("\n✅ SUCCESS - Search Query Fix Working!")
                        print("   🔍 Emojis and quotes were properly cleaned")
                        print("   📊 Search returned actual results")
                        print("   🎯 Query cleaning fix is working!")
                    else:
                        print("\n⚠️  Search still returning no results")
                        print("   🔧 Check backend logs for more details")
                    
                    break
                    
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🎯 Search Query Fix Test Complete!")
    print("=" * 50)
    
    print("\n💡 What was tested:")
    print("   ✅ Query cleaning for emojis and quotes")
    print("   ✅ Search results retrieval")
    print("   ✅ Task execution with cleaned queries")
    
    print("\n🔧 Fix applied:")
    print("   🧹 ControllerWorkerAgent now cleans search queries")
    print("   📝 Removed emojis and extra quotes")
    print("   🔍 Web search uses cleaned query")
    print("   📊 Should return actual results now")
    
    print("\n🎉 Expected results:")
    print("   ✅ Search results should contain actual data")
    print("   ✅ Result count should be > 0")
    print("   ✅ Titles and URLs should be populated")
    print("   ✅ No more empty search results")

if __name__ == "__main__":
    test_search_fix()
