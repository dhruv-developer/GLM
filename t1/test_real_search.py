import requests
import time
import json

BASE_URL = "http://localhost:8000"

print("=== Testing REAL Web Search ===\n")

# Create a real search task
response = requests.post(f"{BASE_URL}/api/v1/create-task", json={
    "intent": "Search for Python async programming tutorials",
    "user_id": "test_user",
    "priority": "medium"
})

if response.status_code == 200:
    task_data = response.json()
    execution_id = task_data['execution_id']
    print(f"✓ Task created: {execution_id}")
    
    # Execute the task
    token = task_data['execution_link'].split('/')[-1]
    exec_response = requests.get(f"{BASE_URL}/api/v1/execute/{token}")
    print(f"✓ Execution started")
    
    # Wait for completion and check results
    print("\n⏳ Waiting for task to complete...")
    for i in range(30):
        time.sleep(2)
        status = requests.get(f"{BASE_URL}/api/v1/status/{execution_id}").json()
        progress = status.get('progress', 0) * 100
        
        print(f"  Progress: {progress:.1f}% | Status: {status['status']}")
        
        if status['status'] in ['completed', 'failed']:
            print(f"\n{'='*50}")
            print(f"FINAL STATUS: {status['status'].upper()}")
            print(f"{'='*50}")
            
            if status['status'] == 'completed' and status.get('result'):
                result = status['result']
                print(f"\n✅ REAL Search Results:")
                print(f"  Query: {result.get('tasks', {}).get('summary', 'N/A')}")
                
                # Show actual search results
                if 'tasks' in result and '2' in result['tasks'].get('tasks', {}):
                    search_task = result['tasks']['tasks']['2']
                    if search_task and 'output' in search_task:
                        output = search_task['output']
                        print(f"\n  Source: {output.get('source', 'unknown')}")
                        print(f"  Results Found: {output.get('result_count', 0)}")
                        print(f"  Execution Time: {output.get('execution_time', 0):.2f}s")
                        print(f"  Timestamp: {output.get('timestamp', 'N/A')}")
                        
                        # Show actual search results
                        results = output.get('results', [])
                        print(f"\n  Top {min(3, len(results))} REAL Search Results:")
                        for i, result in enumerate(results[:3], 1):
                            print(f"    {i}. {result.get('title', 'No title')}")
                            print(f"       URL: {result.get('url', 'No URL')}")
                            print(f"       {result.get('snippet', 'No snippet')[:100]}...")
                            print()
                        
                        if output.get('source') == 'duckduckgo_real':
                            print("  ✅ CONFIRMED: REAL web search from DuckDuckGo")
                        else:
                            print(f"  ⚠️  Source: {output.get('source', 'unknown')}")
            
            # Show logs
            logs = status.get('logs', [])
            if logs:
                print(f"\n📋 Recent Execution Logs:")
                for log in logs[-3:]:
                    print(f"  [{log['level']}] {log['message']}")
            
            break
else:
    print(f"✗ Task creation failed: {response.text}")

print(f"\n{'='*50}")
print("Test Complete")
print(f"{'='*50}")
