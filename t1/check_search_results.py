import requests
import time

BASE_URL = "http://localhost:8000"

# Create a simple search task
response = requests.post(f"{BASE_URL}/api/v1/create-task", json={
    "intent": "Search for React tutorials",
    "user_id": "check_user",
    "priority": "medium"
})

if response.status_code == 200:
    task_data = response.json()
    execution_id = task_data['execution_id']
    print(f"Created task: {execution_id}")
    
    # Execute
    token = task_data['execution_link'].split('/')[-1]
    requests.get(f"{BASE_URL}/api/v1/execute/{token}")
    
    # Wait for completion
    time.sleep(10)
    
    # Get detailed status
    status = requests.get(f"{BASE_URL}/api/v1/status/{execution_id}").json()
    
    print(f"\nStatus: {status['status']}")
    print(f"Progress: {status['progress']*100:.1f}%")
    print(f"Completed tasks: {status.get('completed_tasks', 0)}/{status.get('total_tasks', 0)}")
    
    # Show full result
    if status.get('result'):
        print(f"\n✅ FULL RESULT:")
        print(json.dumps(status['result'], indent=2))
    else:
        print("\n❌ No result data")
        
    # Show logs
    if status.get('logs'):
        print(f"\n📋 ALL LOGS:")
        for log in status['logs']:
            print(f"  [{log['level']}] {log['message']}")

else:
    print(f"Failed: {response.text}")
