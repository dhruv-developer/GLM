import requests
import time
import json

BASE_URL = "http://localhost:8000"

print("🧠 TESTING: Document Generation with Final Results\n")
print("="*60)

# Create a task
response = requests.post(f"{BASE_URL}/api/v1/create-task", json={
    "intent": "Search for Python async programming and prepare a comprehensive summary",
    "user_id": "doc_test",
    "priority": "medium"
})

if response.status_code == 200:
    task_data = response.json()
    execution_id = task_data['execution_id']
    print(f"✅ Task Created: {execution_id}")
    
    # Execute
    token = task_data['execution_link'].split('/')[-1]
    requests.get(f"{BASE_URL}/api/v1/execute/{token}")
    print("✅ Execution started")
    
    # Monitor
    print(f"\n⏳ Processing:")
    for i in range(30):
        time.sleep(2)
        status = requests.get(f"{BASE_URL}/api/v1/status/{execution_id}").json()
        progress = status.get('progress', 0) * 100
        state = status.get('status', 'unknown')
        
        print(f"  [{i*2}s] Progress: {progress:5.1f}% | Status: {state}")
        
        if state in ['completed', 'failed']:
            print(f"\n{'='*60}")
            print(f"🎯 FINAL RESULT: {state.upper()}")
            print(f"{'='*60}")
            
            if state == 'completed' and status.get('result'):
                result = status.get('result', {})
                tasks = result.get('tasks', {})
                
                print(f"\n📋 Tasks Executed: {len(tasks)}")
                
                # Show document generation result
                for task_id, task_info in tasks.items():
                    agent = task_info.get('agent', '')
                    action = task_info.get('action', '')
                    output = task_info.get('output', {})
                    
                    print(f"\n🤖 {agent.upper()} - {action}")
                    
                    if agent == 'document' and output:
                        print(f"   ✅ DOCUMENT GENERATED!")
                        
                        summary = output.get('summary', {})
                        if summary:
                            print(f"\n   📄 SUMMARY:")
                            print(f"   Title: {summary.get('title', 'N/A')}")
                            print(f"   Intent: {summary.get('intent', 'N/A')}")
                            
                            key_findings = summary.get('key_findings', [])
                            if key_findings:
                                print(f"\n   🔍 KEY FINDINGS ({len(key_findings)}):")
                                for i, finding in enumerate(key_findings[:3], 1):
                                    print(f"      {i}. {finding[:80]}...")
                            
                            recommendations = summary.get('recommendations', [])
                            if recommendations:
                                print(f"\n   💡 RECOMMENDATIONS ({len(recommendations)}):")
                                for i, rec in enumerate(recommendations[:3], 1):
                                    print(f"      {i}. {rec}")
                            
                            sources = summary.get('sources', [])
                            if sources:
                                print(f"\n   📚 SOURCES ({len(sources)}):")
                                for i, source in enumerate(sources[:3], 1):
                                    print(f"      {i}. {source.get('title', 'N/A')}")
                        
                        document = output.get('document', {})
                        if document and document.get('document'):
                            doc_content = document['document']
                            print(f"\n   📄 DOCUMENT CONTENT (first 500 chars):")
                            print(f"   {doc_content[:500]}...")
                            print(f"\n   ✅ READY TO DISPLAY ON FRONTEND!")
                
                break
    else:
        print(f"❌ Task creation failed: {response.text}")

print(f"\n{'='*60}")
print("Test Complete")
print(f"{'='*60}")
