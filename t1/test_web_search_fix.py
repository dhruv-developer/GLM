#!/usr/bin/env python3
"""
Test script to verify web search fixes
"""

import requests
import json
import time

def test_web_search_fix():
    """Test that web search now returns actual results"""
    
    print("🧪 Testing Web Search Fix")
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
    
    # Test 2: Create a search task
    print("\n🔍 Creating search task...")
    task_data = {
        "intent": "Find python programming tutorials",
        "priority": "medium",
        "user_id": "test_search_user"
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
    
    # Test 4: Monitor task and check search results
    print("\n📊 Monitoring search results...")
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
                
                print(f"   Attempt {attempt + 1}: {status} - {int(progress * 100)}% ({completed}/{total} tasks)")
                
                # Check for search results in the response
                if status_data.get("result"):
                    result = status_data.get("result", {})
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
                                        print(f"   📝 Note: {output.get('note', 'No note')}")
                
                # Check if completed
                if status in ["completed", "failed"]:
                    print(f"\n🎉 Task {status}!")
                    
                    if search_results_found:
                        print("   ✅ Web search is working!")
                        print("   ✅ Got actual search results!")
                    else:
                        print("   ⚠️  Web search returned no results")
                        print("   🔧 Check the debug_web_search.py script")
                    
                    break
                    
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Status check error: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🎯 Web Search Fix Test Complete!")
    print("=" * 50)
    
    print("\n💡 What was tested:")
    print("   ✅ Backend connectivity")
    print("   ✅ Search task creation and execution")
    print("   ✅ Search results monitoring")
    print("   ✅ Result parsing verification")
    
    print("\n🔧 Fixes applied:")
    print("   🔍 Improved DuckDuckGo HTML parsing")
    print("   📊 Added multiple CSS selectors")
    print("   🛠️  Better fallback handling")
    print("   📝 Enhanced error logging")
    
    print("\n🎉 Expected results:")
    print("   ✅ Search results should contain actual data")
    print("   ✅ Result count should be > 0")
    print("   ✅ Titles and URLs should be populated")
    print("   ✅ No more empty search results")
    
    print("\n🐛 Debug tools:")
    print("   📝 Run: python debug_web_search.py")
    print("   🔧 This tests DuckDuckGo parsing directly")

if __name__ == "__main__":
    test_web_search_fix()
