import asyncio
import sys
import requests
import time

sys.path.append('/Users/dhruvdawar11/Desktop/Projects/GLM-Hack/t1')

BASE_URL = "http://localhost:8000"

def test_create_and_execute_task():
    """Test the complete task creation and execution flow"""
    
    # Step 1: Create a task
    print("=== Step 1: Creating Task ===")
    create_response = requests.post(f"{BASE_URL}/api/v1/create-task", json={
        "intent": "Search for the latest Python async best practices",
        "user_id": "test_user_001",
        "priority": "medium"
    })
    
    if create_response.status_code == 200:
        task_data = create_response.json()
        print(f"✓ Task created successfully!")
        print(f"  Execution ID: {task_data['execution_id']}")
        print(f"  Execution Link: {task_data['execution_link']}")
        print(f"  Estimated Duration: {task_data['estimated_duration']}s")
        print(f"  Task Count: {task_data['task_count']}")
        
        execution_id = task_data['execution_id']
        execution_link = task_data['execution_link']
        
        # Step 2: Execute the task using the execution link
        print("\n=== Step 2: Executing Task ===")
        token = execution_link.split('/')[-1]
        execute_response = requests.get(f"{BASE_URL}/api/v1/execute/{token}")
        
        if execute_response.status_code == 200:
            exec_data = execute_response.json()
            print(f"✓ Task execution started!")
            print(f"  Message: {exec_data['message']}")
            print(f"  Status: {exec_data['status']}")
            
            # Step 3: Monitor task progress
            print("\n=== Step 3: Monitoring Progress ===")
            max_attempts = 30
            attempt = 0
            
            while attempt < max_attempts:
                time.sleep(2)
                status_response = requests.get(f"{BASE_URL}/api/v1/status/{execution_id}")
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    progress = status_data.get('progress', 0) * 100
                    status = status_data.get('status', 'unknown')
                    
                    print(f"  Progress: {progress:.1f}% | Status: {status}")
                    
                    if status in ['completed', 'failed', 'cancelled']:
                        print(f"\n=== Task Final Status: {status.upper()} ===")
                        
                        if status == 'completed' and status_data.get('result'):
                            print("✓ Task completed successfully!")
                            print(f"  Result: {status_data['result']}")
                        elif status == 'failed':
                            print(f"✗ Task failed: {status_data.get('error', 'Unknown error')}")
                        
                        print(f"  Completed Tasks: {status_data.get('completed_tasks', 0)}/{status_data.get('total_tasks', 0)}")
                        
                        # Show recent logs
                        logs = status_data.get('logs', [])
                        if logs:
                            print("\n  Recent Logs:")
                            for log in logs[-3:]:
                                print(f"    [{log['level']}] {log['message']}")
                        
                        break
                
                attempt += 1
            else:
                print("⚠ Task monitoring timeout")
        else:
            print(f"✗ Execution failed: {execute_response.text}")
    else:
        print(f"✗ Task creation failed: {create_response.text}")

if __name__ == "__main__":
    test_create_and_execute_task()
