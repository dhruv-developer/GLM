import requests
import time

BASE_URL = "http://localhost:8000"

print("🧪 SIMPLE TEST - Basic Functionality\n")

response = requests.post(f"{BASE_URL}/api/v1/create-task", json={
    "intent": "Search for Python tutorials",
    "user_id": "simple_test",
    "priority": "medium"
})

if response.status_code == 200:
    task_data = response.json()
    execution_id = task_data['execution_id']
    print(f"✅ Task created: {execution_id}")
    
    token = task_data['execution_link'].split('/')[-1]
    requests.get(f"{BASE_URL}/api/v1/execute/{token}")
    
    time.sleep(5)
    status = requests.get(f"{BASE_URL}/api/v1/status/{execution_id}").json()
    
    print(f"Status: {status['status']}")
    print(f"Progress: {status['progress']*100:.1f}%")
    
    if status['status'] == 'completed':
        print("✅ Basic execution working!")
    else:
        print(f"❌ Status: {status['status']}")
        if status.get('logs'):
            recent_errors = [log for log in status['logs'] if log['level'] == 'ERROR'][-3:]
            for error in recent_errors:
                print(f"   ERROR: {error['message']}")
else:
    print(f"❌ Failed: {response.text}")
