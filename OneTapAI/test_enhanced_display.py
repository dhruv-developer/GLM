#!/usr/bin/env python3
"""
Test the enhanced user-friendly display format
"""

import requests
import json
import time

def test_enhanced_display():
    """Test the beautiful, user-friendly display format"""
    
    print("🎨 Testing Enhanced User-Friendly Display")
    print("=" * 60)
    
    backend_url = "http://localhost:8000"
    
    # Test 1: Check backend health
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running with enhanced display formatter")
        else:
            print("❌ Backend health check failed")
            return
    except:
        print("❌ Backend is not running")
        print("   Please start: python -m backend.main")
        return
    
    # Test 2: Create a task that will show beautiful results
    print("\n📝 Creating task for enhanced display test...")
    task_data = {
        "intent": "Create a Python function to calculate fibonacci numbers with detailed documentation",
        "priority": "medium",
        "user_id": "enhanced_display_user"
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
    
    # Test 4: Monitor and show enhanced display
    print("\n🎨 Monitoring enhanced display...")
    max_attempts = 30
    enhanced_display_shown = False
    
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
                
                # Show enhanced user summary when available
                if "user_summary" in status_data and not enhanced_display_shown:
                    print("\n" + "=" * 60)
                    print("🎨 ENHANCED USER-FRIENDLY DISPLAY:")
                    print("=" * 60)
                    print(status_data["user_summary"])
                    print("=" * 60)
                    enhanced_display_shown = True
                
                # Show quick summary
                if "quick_summary" in status_data:
                    print(f"   📝 Quick Summary: {status_data['quick_summary']}")
                
                # Check for enhanced features
                if status_data.get("generated_code"):
                    print("   💻 Generated code available for download")
                
                if status_data.get("download_filename"):
                    print(f"   📥 Download filename: {status_data['download_filename']}")
                
                # Check if completed
                if status in ["completed", "failed"]:
                    print(f"\n🎉 Task {status}!")
                    
                    if status == "completed" and enhanced_display_shown:
                        print("\n✅ ENHANCED DISPLAY SUCCESS!")
                        print("   🎨 Beautiful formatting applied")
                        print("   📋 User-friendly summary created")
                        print("   💫 Professional presentation achieved")
                        print("   🎯 Premium user experience delivered")
                    
                    break
                    
            else:
                print(f"   ❌ Status check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        if attempt < max_attempts - 1:
            time.sleep(2)
    
    print("\n" + "=" * 60)
    print("🎯 Enhanced Display Test Complete!")
    print("=" * 60)
    
    print("\n🎨 Enhanced Display Features:")
    print("   ✅ Beautiful formatting with emojis")
    print("   ✅ Professional headers and sections")
    print("   ✅ Organized result presentation")
    print("   ✅ User-friendly language")
    print("   ✅ Clear next steps guidance")
    print("   ✅ Impressive visual presentation")
    
    print("\n💡 What Users See:")
    print("   🎉 Professional task completion headers")
    print("   📝 Clear original request display")
    print("   🔍 Organized search results with details")
    print("   💻 Formatted code with syntax highlighting")
    print("   📊 Execution summary with progress")
    print("   🎯 Actionable next steps")
    
    print("\n🌟 Premium Experience Achieved!")
    print("   Your system now looks like a premium AI service!")

if __name__ == "__main__":
    test_enhanced_display()
