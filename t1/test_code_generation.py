import requests
import time

BASE_URL = "http://localhost:8000"

# Test code generation
print("=== Testing Code Generation Task ===")
response = requests.post(f"{BASE_URL}/api/v1/create-task", json={
    "intent": "Write a Python function to fetch data from an API and handle errors",
    "user_id": "test_user",
    "priority": "medium"
})

if response.status_code == 200:
    task_data = response.json()
    execution_id = task_data['execution_id']
    print(f"✓ Task created: {execution_id}")
    print(f"  Task Count: {task_data['task_count']}")
    
    # Execute
    token = task_data['execution_link'].split('/')[-1]
    requests.get(f"{BASE_URL}/api/v1/execute/{token}")
    
    # Monitor
    for i in range(20):
        time.sleep(2)
        status = requests.get(f"{BASE_URL}/api/v1/status/{execution_id}").json()
        progress = status.get('progress', 0) * 100
        print(f"  Progress: {progress:.1f}% - {status['status']}")
        
        if status['status'] in ['completed', 'failed']:
            print(f"\n✓ Task {status['status'].upper()}")
            if status['status'] == 'completed' and status.get('result'):
                print(f"  Result: {status['result']}")
            break
else:
    print(f"✗ Failed: {response.text}")
