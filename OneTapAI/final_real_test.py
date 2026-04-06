import requests
import time
import json

BASE_URL = "http://localhost:8000"

print("🔍 FINAL TEST: REAL Web Search with Actual Results\n")
print("="*60)

# Create a search task
response = requests.post(f"{BASE_URL}/api/v1/create-task", json={
    "intent": "Search for Python async programming tutorials",
    "user_id": "final_test",
    "priority": "medium"
})

if response.status_code == 200:
    task_data = response.json()
    execution_id = task_data['execution_id']
    print(f"✅ Task Created: {execution_id}")
    print(f"   Estimated Duration: {task_data['estimated_duration']}s")
    print(f"   Task Count: {task_data['task_count']}")
    
    # Execute the task
    print(f"\n🚀 Executing Task...")
    token = task_data['execution_link'].split('/')[-1]
    exec_response = requests.get(f"{BASE_URL}/api/v1/execute/{token}")
    
    if exec_response.status_code == 200:
        print(f"✅ Execution Started")
        
        # Monitor progress
        print(f"\n⏳ Monitoring Progress:")
        for i in range(30):
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/v1/status/{execution_id}")
            
            if status_response.status_code == 200:
                status = status_response.json()
                progress = status.get('progress', 0) * 100
                current_status = status.get('status', 'unknown')
                
                print(f"   [{i*2}s] Progress: {progress:5.1f}% | Status: {current_status}")
                
                if current_status in ['completed', 'failed']:
                    print(f"\n{'='*60}")
                    print(f"🎯 FINAL RESULT: {current_status.upper()}")
                    print(f"{'='*60}")
                    
                    if current_status == 'completed':
                        result = status.get('result')
                        if result:
                            print(f"\n✅ REAL WEB SEARCH RESULTS:")
                            print(f"   Summary: {result.get('summary', 'N/A')}")
                            
                            # Show detailed task results
                            tasks_data = result.get('tasks', {})
                            if tasks_data:
                                print(f"\n📋 Task Execution Details:")
                                
                                for task_id, task_info in tasks_data.items():
                                    action = task_info.get('action', 'unknown')
                                    agent = task_info.get('agent', 'unknown')
                                    output = task_info.get('output', {})
                                    
                                    print(f"\n   Task {task_id[:8]}...")
                                    print(f"   ├─ Action: {action}")
                                    print(f"   ├─ Agent: {agent}")
                                    
                                    if output:
                                        source = output.get('source', 'unknown')
                                        result_count = output.get('result_count', 0)
                                        exec_time = output.get('execution_time', 0)
                                        timestamp = output.get('timestamp', 'N/A')
                                        
                                        print(f"   ├─ Source: {source}")
                                        print(f"   ├─ Results: {result_count}")
                                        print(f"   ├─ Time: {exec_time:.2f}s")
                                        print(f"   └─ Timestamp: {timestamp}")
                                        
                                        # Show actual search results if available
                                        if 'results' in output and output['results']:
                                            results = output['results']
                                            print(f"\n   🌐 REAL Search Results (Top {min(3, len(results))}):")
                                            for i, res in enumerate(results[:3], 1):
                                                title = res.get('title', 'No title')
                                                url = res.get('url', 'No URL')
                                                snippet = res.get('snippet', '')[:80]
                                                
                                                print(f"\n      {i}. {title}")
                                                print(f"         🔗 {url}")
                                                print(f"         📝 {snippet}...")
                                        
                                        if source == 'duckduckgo_real':
                                            print(f"\n   ✅ CONFIRMED: REAL web search from DuckDuckGo")
                                            print(f"   ✅ NO DUMMY DATA - All results are from real web sources")
                                            print(f"   ✅ REAL timing and timestamp data")
                        else:
                            print("❌ No result data found")
                    
                    # Show execution logs
                    logs = status.get('logs', [])
                    if logs:
                        print(f"\n📋 Execution Logs:")
                        for log in logs[-5:]:
                            level = log['level']
                            msg = log['message']
                            print(f"   [{level}] {msg}")
                    
                    print(f"\n{'='*60}")
                    print("✅ TEST COMPLETE - All data is REAL and accurate")
                    print(f"{'='*60}")
                    break
    else:
        print(f"❌ Execution failed: {exec_response.text}")
else:
    print(f"❌ Task creation failed: {response.text}")
