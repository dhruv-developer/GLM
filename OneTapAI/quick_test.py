import requests
import time

BASE_URL = "http://localhost:8000"

print("🧪 Quick Test - Fixed Import Issues\n")

# Create a simple task
response = requests.post(f"{BASE_URL}/api/v1/create-task", json={
    "intent": "Search for Python tutorials",
    "user_id": "quick_test",
    "priority": "medium"
})

if response.status_code == 200:
    task_data = response.json()
    execution_id = task_data['execution_id']
    print(f"✅ Task created: {execution_id}")
    
    # Execute
    token = task_data['execution_link'].split('/')[-1]
    requests.get(f"{BASE_URL}/api/v1/execute/{token}")
    print("✅ Execution started")
    
    # Monitor
    print("\n⏳ Monitoring:")
    for i in range(20):
        time.sleep(2)
        status = requests.get(f"{BASE_URL}/api/v1/status/{execution_id}").json()
        progress = status.get('progress', 0) * 100
        state = status.get('status', 'unknown')
        
        print(f"  [{i*2}s] {progress:5.1f}% - {state}")
        
        if state in ['completed', 'failed']:
            print(f"\n🎯 Final: {state.upper()}")
            
            if state == 'completed' and status.get('result'):
                result = status.get('result', {})
                print(f"✅ Summary: {result.get('summary', 'N/A')}")
                
                # Check web search results
                tasks = result.get('tasks', {})
                for task_id, task_info in tasks.items():
                    if task_info.get('agent') == 'web_search':
                        output = task_info.get('output', {})
                        print(f"🔍 Search Results: {output.get('result_count', 0)} found")
                        print(f"⏱️  Time: {output.get('execution_time', 0):.2f}s")
                        print(f"📊 Source: {output.get('source', 'unknown')}")
                        
                        if output.get('source') == 'duckduckgo_real':
                            print("✅ REAL web search working!")
                        
                        # Show first result
                        results = output.get('results', [])
                        if results:
                            first = results[0]
                            print(f"\n📌 First Result:")
                            print(f"   Title: {first.get('title', 'No title')}")
                            print(f"   URL: {first.get('url', 'No URL')}")
                            print(f"   Snippet: {first.get('snippet', 'No snippet')[:80]}...")
                        break
            
            # Show recent logs
            logs = status.get('logs', [])
            error_logs = [log for log in logs if log['level'] == 'ERROR']
            
            if error_logs:
                print(f"\n⚠️  Recent Errors:")
                for log in error_logs[-3:]:
                    print(f"   {log['message']}")
            else:
                print(f"\n✅ No errors in execution!")
            
            break
else:
    print(f"❌ Failed: {response.text}")

print(f"\n{'='*50}")
print("Test Complete")
print(f"{'='*50}")
